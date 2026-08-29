-- King Wen 9-Bit State Resolver (POG3 Sovereign Stack)
-- Target: Zynq UltraScale+ ZU7EV PL Fabric
--
-- GENERATED FILE — DO NOT HAND-EDIT.
-- Source of truth: kingwen_ternary_tables_complete.py :: HEXAGRAM_BASE
-- Generator: scripts/generate_vhdl_roms.py
--
-- Resolves 9-bit address (0..511) in single clock cycle to:
--   - hexagram_id (6 bits, 1..64)
--   - phase_bits (3 bits, 0..7)
--   - state_fidelity (14-bit Q2.12 fixed point)
--   - action_code (2 bits: 00=ASSERT, 01=YIELD, 10=ADAPT, 11=WAIT)
--   - vortex_tension (12-bit Q4.8 fixed point from canonical upper_idx * lower_idx / 49.0)
--   - motion_mode (1 bit: 0=centripetal, 1=centrifugal)
--
-- Deterministic. No pseudo-RNG. 100% Hardware Parity (ROMs derived from Python).

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity KingWen9BitResolver is
  port (
    clk           : in  std_logic;
    rst           : in  std_logic;
    addr_in       : in  std_logic_vector(8 downto 0);
    addr_valid    : in  std_logic;

    -- Outputs (registered on rising clock edge)
    hexagram_id   : out std_logic_vector(6 downto 0);  -- 1..64
    phase_bits    : out std_logic_vector(2 downto 0);
    state_fidelity: out std_logic_vector(13 downto 0);  -- Q2.12
    action_code   : out std_logic_vector(1 downto 0);   -- 00=ASSERT, 01=YIELD, 10=ADAPT, 11=WAIT
    vortex_tension: out std_logic_vector(11 downto 0);  -- Q4.8
    motion_mode   : out std_logic;                      -- 0=centripetal, 1=centrifugal
    out_valid     : out std_logic
  );
end entity;

architecture rtl of KingWen9BitResolver is
  signal hex_id_reg     : unsigned(6 downto 0);
  signal phase_reg      : unsigned(2 downto 0);
  signal fid_reg        : unsigned(13 downto 0);
  signal act_reg        : std_logic_vector(1 downto 0);
  signal vortex_reg     : unsigned(11 downto 0);
  signal motion_reg     : std_logic;

  -- Canonical Upper & Lower Trigram Index ROM for exact Schauberger Vortex Tension
  -- Source: HEXAGRAM_BASE[hid]['upper_idx'] / ['lower_idx']
  type trigram_idx_rom_t is array (1 to 64) of integer;
  constant UPPER_IDX_ROM : trigram_idx_rom_t := (
    7, 0, 4, 2, 7, 2, 2, 0,
    7, 6, 7, 0, 7, 5, 0, 1,
    3, 4, 0, 6, 5, 4, 4, 0,
    7, 4, 4, 3, 2, 5, 3, 1,
    7, 1, 5, 0, 6, 5, 1, 2,
    6, 4, 3, 7, 3, 0, 3, 2,
    3, 5, 1, 4, 6, 1, 5, 1,
    6, 3, 6, 2, 6, 1, 2, 5
  );

  constant LOWER_IDX_ROM : trigram_idx_rom_t := (
    7, 0, 2, 1, 2, 7, 0, 2,
    3, 7, 0, 7, 5, 7, 4, 0,
    1, 6, 3, 0, 1, 5, 0, 1,
    1, 7, 1, 6, 2, 5, 4, 6,
    4, 7, 0, 5, 5, 3, 2, 4,
    1, 3, 7, 6, 0, 6, 2, 6,
    5, 6, 1, 4, 4, 3, 4, 5,
    6, 3, 2, 3, 3, 4, 5, 2
  );

  -- Canonical Action ROM (64 entries, one per hexagram) from HEXAGRAM_BASE[hid]['action']
  type action_rom_t is array (1 to 64) of std_logic_vector(1 downto 0);
  constant ACTION_ROM : action_rom_t := (
    "00", "01", "10", "11", "11", "00", "00", "01",
    "10", "10", "01", "11", "00", "00", "01", "10",
    "01", "10", "01", "11", "00", "11", "11", "01",
    "00", "10", "01", "10", "11", "10", "01", "11",
    "01", "00", "10", "11", "01", "10", "11", "10",
    "01", "00", "00", "11", "01", "10", "11", "01",
    "00", "00", "00", "11", "10", "01", "00", "10",
    "01", "01", "10", "11", "01", "11", "11", "10"
  );

  -- Helper function to generate canonical Vortex Tension Q4.8 ROM
  -- Exact integer math (no IEEE real) to match HEXAGRAM_BASE ground truth precisely.
  -- vortex = round(u_idx * l_idx * 256 / 49), clamped to 12-bit range.
  type vortex_rom_t is array (0 to 511) of unsigned(11 downto 0);
  function build_canonical_vortex_rom return vortex_rom_t is
    variable rom : vortex_rom_t;
    variable hex_id, u_idx, l_idx : integer;
    variable val : integer;
  begin
    for addr in 0 to 511 loop
      hex_id := (addr / 8) + 1;
      u_idx := UPPER_IDX_ROM(hex_id);
      l_idx := LOWER_IDX_ROM(hex_id);
      -- exact: (u*l*256 + 49/2) / 49  == round-half-up, all integer
      val := (u_idx * l_idx * 256 + 24) / 49;
      if val > 4095 then
        val := 4095;  -- safety clamp (max actual = 256, unreachable)
      end if;
      rom(addr) := to_unsigned(val, 12);
    end loop;
    return rom;
  end function;

  constant VORTEX_ROM : vortex_rom_t := build_canonical_vortex_rom;

begin

  process(addr_in)
    variable addr : integer;
    variable hex_id : integer;
  begin
    addr := to_integer(unsigned(addr_in));
    hex_id := (addr / 8) + 1;

    hex_id_reg <= to_unsigned(hex_id, 7);
    phase_reg  <= to_unsigned(addr mod 8, 3);

    -- Action mapping: direct ROM lookup (single source of truth = HEXAGRAM_BASE action field)
    act_reg <= ACTION_ROM(hex_id);

    vortex_reg <= VORTEX_ROM(addr);

    -- state_fidelity: deterministic resolver -> full fidelity (Q2.12 = 1.0)
    fid_reg <= to_unsigned(4096, 14);
    -- Motion mode derivation: phase_bits 3,5,6,7 -> Centrifugal (1), 0,1,2,4 -> Centripetal (0)
    if (addr mod 8 = 3 or addr mod 8 = 5 or addr mod 8 = 6 or addr mod 8 = 7) then
      motion_reg <= '1'; -- 1 = Centrifugal
    else
      motion_reg <= '0'; -- 0 = Centripetal
    end if;
  end process;

  process(clk, rst)
  begin
    if rst = '1' then
      hexagram_id    <= (others => '0');
      phase_bits     <= (others => '0');
      state_fidelity <= (others => '0');
      action_code    <= (others => '0');
      vortex_tension <= (others => '0');
      motion_mode    <= '0';
      out_valid      <= '0';
    elsif rising_edge(clk) then
      if addr_valid = '1' then
        hexagram_id    <= std_logic_vector(hex_id_reg);
        phase_bits     <= std_logic_vector(phase_reg);
        state_fidelity <= std_logic_vector(fid_reg);
        action_code    <= act_reg;
        vortex_tension <= std_logic_vector(vortex_reg);
        motion_mode    <= motion_reg;
        out_valid      <= '1';
      else
        out_valid <= '0';
      end if;
    end if;
  end process;

end architecture;
