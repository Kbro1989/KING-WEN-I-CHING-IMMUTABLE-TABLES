"""
generate_vhdl_testbench.py — emits tb_KingWen9BitResolver.vhd + a
KingWenExpected_pkg.vhd expected-vector package, both derived from
kingwen_ternary_tables_complete.py :: HEXAGRAM_BASE. The testbench drives
all 512 addresses and asserts every output field against ground truth.

Run:  python3 scripts/generate_vhdl_testbench.py
Then: ghdl -a KingWenExpected_pkg.vhd tb_KingWen9BitResolver.vhd && ghdl -e tb_KingWen9BitResolver && ghdl -r tb_KingWen9BitResolver
"""
import importlib.util
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = importlib.util.spec_from_file_location(
    "ktt", os.path.join(REPO, "kingwen_ternary_tables_complete.py")
)
KT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(KT)
HB = KT.HEXAGRAM_BASE

ACTION_CODE = {"ASSERT": "00", "YIELD": "01", "ADAPT": "10", "WAIT": "11"}


def q48(v):
    return int(v * 256.0) & 0xFFF


# Build expected table: index 0..511 -> record
rows = []
for addr in range(512):
    hex_id = (addr // 8) + 1
    phase = addr % 8
    b = HB[hex_id]
    u = b["upper_idx"]
    l = b["lower_idx"]
    action = ACTION_CODE[b["action"]]
    # exact integer round-half-up: (u*l*256 + 24) / 49
    vortex = ((u * l * 256) + 24) // 49
    motion = "1" if phase in (3, 5, 6, 7) else "0"
    rows.append((addr, hex_id, phase, action, vortex, motion))

# --- expected-vector package ---
pkg = "-- GENERATED from HEXAGRAM_BASE (single source of truth)\n"
pkg += "library IEEE;\n"
pkg += "use IEEE.STD_LOGIC_1164.ALL;\n"
pkg += "package KingWenExpected_pkg is\n"
pkg += "  type exp_rec is record\n"
pkg += "    hex_id   : integer range 1 to 64;\n"
pkg += "    phase    : integer range 0 to 7;\n"
pkg += "    action   : std_logic_vector(1 downto 0);\n"
pkg += "    vortex   : integer range 0 to 4095;\n"
pkg += "    motion   : std_logic;\n"
pkg += "  end record;\n"
pkg += "  type exp_table_t is array (0 to 511) of exp_rec;\n"
pkg += "  constant EXPECTED : exp_table_t := (\n"
body = []
for addr, hid, ph, act, vor, mot in rows:
    # record order: hex_id, phase, action, vortex, motion  (NO addr — that's the array index)
    body.append(
        f"    ({hid}, {ph}, \"{act}\", {vor}, '{mot}')"
    )
pkg += ",\n".join(body)
pkg += "\n  );\n"
pkg += "end package;\n"

PKG_PATH = os.path.join(REPO, "src", "hardware", "KingWenExpected_pkg.vhd")
with open(PKG_PATH, "w") as f:
    f.write(pkg)

# --- testbench ---
tb = """-- GENERATED testbench. Ground truth from HEXAGRAM_BASE via KingWenExpected_pkg.
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use work.KingWenExpected_pkg.ALL;

entity tb_KingWen9BitResolver is
end entity;

architecture sim of tb_KingWen9BitResolver is
  signal clk        : std_logic := '0';
  signal rst        : std_logic := '1';
  signal addr_in    : std_logic_vector(8 downto 0) := (others => '0');
  signal addr_valid : std_logic := '0';
  signal hexagram_id   : std_logic_vector(6 downto 0);
  signal phase_bits    : std_logic_vector(2 downto 0);
  signal state_fidelity: std_logic_vector(13 downto 0);
  signal action_code   : std_logic_vector(1 downto 0);
  signal vortex_tension: std_logic_vector(11 downto 0);
  signal motion_mode   : std_logic;
  signal out_valid     : std_logic;

  signal fails : integer := 0;
begin
  DUT: entity work.KingWen9BitResolver
    port map (
      clk => clk, rst => rst, addr_in => addr_in, addr_valid => addr_valid,
      hexagram_id => hexagram_id, phase_bits => phase_bits,
      state_fidelity => state_fidelity, action_code => action_code,
      vortex_tension => vortex_tension, motion_mode => motion_mode,
      out_valid => out_valid
    );

  clk <= not clk after 5 ns;

  stim: process
    variable addr : integer;
  begin
    wait for 20 ns;
    rst <= '0';
    wait until rising_edge(clk);

    for i in 0 to 511 loop
      addr := i;
      addr_in <= std_logic_vector(to_unsigned(addr, 9));
      addr_valid <= '1';
      wait until rising_edge(clk);
      wait for 1 ns;  -- settle combinatorial + register

      assert out_valid = '1'
        report "out_valid low at addr " & integer'image(addr) severity error;

      if to_integer(unsigned(hexagram_id)) /= EXPECTED(i).hex_id then
        report "hexagram_id mismatch addr " & integer'image(addr) &
               " got " & integer'image(to_integer(unsigned(hexagram_id))) &
               " exp " & integer'image(EXPECTED(i).hex_id) severity error;
        fails <= fails + 1;
      end if;
      if to_integer(unsigned(phase_bits)) /= EXPECTED(i).phase then
        report "phase_bits mismatch addr " & integer'image(addr) severity error;
        fails <= fails + 1;
      end if;
      if action_code /= EXPECTED(i).action then
        report "action_code mismatch addr " & integer'image(addr) &
               " exp " & integer'image(to_integer(unsigned(EXPECTED(i).action))) severity error;
        fails <= fails + 1;
      end if;
      if to_integer(unsigned(vortex_tension)) /= EXPECTED(i).vortex then
        report "vortex_tension mismatch addr " & integer'image(addr) &
               " got " & integer'image(to_integer(unsigned(vortex_tension))) &
               " exp " & integer'image(EXPECTED(i).vortex) severity error;
        fails <= fails + 1;
      end if;
      if motion_mode /= EXPECTED(i).motion then
        report "motion_mode mismatch addr " & integer'image(addr) severity error;
        fails <= fails + 1;
      end if;
    end loop;

    addr_valid <= '0';
    wait for 20 ns;

    if fails = 0 then
      report "=== ALL 512 STATES PASS (KingWen9BitResolver VHDL vs HEXAGRAM_BASE) ===" severity note;
    else
      report "=== " & integer'image(fails) & " FAILURES ===" severity error;
    end if;
    wait;
  end process;
end architecture;
"""

TB_PATH = os.path.join(REPO, "src", "hardware", "tb_KingWen9BitResolver.vhd")
with open(TB_PATH, "w") as f:
    f.write(tb)

print("WROTE", PKG_PATH)
print("WROTE", TB_PATH)
print("expected vectors:", len(rows), "| sample addr0:", rows[0], "| addr511:", rows[511])
