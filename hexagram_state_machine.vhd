-- ============================================================
-- POG2 King Wen Quantum State Machine
-- Module: hexagram_state_machine.vhd
-- Target: Zynq UltraScale+ ZU7EV
-- Revision: 1.0
-- Date: 2026-07-10
-- Author: POG2 Sovereign Systems Engineering
--
-- 512-state deterministic oracle
-- 64 hexagrams × 8 yao/temporal contexts = 2^9 states
-- Ternary line encoding: yin=00, yang=01, yao=10
-- No pseudo-RNG. Deterministic hash from immutable tables.
-- ============================================================

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity hexagram_state_machine is
    generic (
        -- State space: 512 = 2^9
        STATE_BITS : integer := 9;

        -- Hexagram ID: 1-64 (6 bits)
        HEX_ID_BITS : integer := 6;

        -- Yao context: 3 bits = 8 contexts
        YAO_CTX_BITS : integer := 3;

        -- Line encoding: 2 bits per line (ternary: 00=yin, 01=yang, 10=yao)
        LINE_BITS : integer := 2;

        -- Temporal phase: past=00, present=01, future=10
        TEMPORAL_BITS : integer := 2;

        -- Porosity: 8-bit fixed point (0.0 to 1.0)
        POROSITY_BITS : integer := 8;

        -- Stability/Change/Alignment: 8-bit fixed point
        METRIC_BITS : integer := 8
    );
    port (
        -- Clock and reset
        clk     : in  std_logic;
        rst_n   : in  std_logic;  -- Active low reset

        -- Control interface (AXI4-Lite Slave)
        -- Base address: 0x4000_0000
        s_axi_awaddr  : in  std_logic_vector(31 downto 0);
        s_axi_awvalid : in  std_logic;
        s_axi_awready : out std_logic;
        s_axi_wdata   : in  std_logic_vector(31 downto 0);
        s_axi_wstrb   : in  std_logic_vector(3 downto 0);
        s_axi_wvalid  : in  std_logic;
        s_axi_wready  : out std_logic;
        s_axi_bresp   : out std_logic_vector(1 downto 0);
        s_axi_bvalid  : out std_logic;
        s_axi_bready  : in  std_logic;
        s_axi_araddr  : in  std_logic_vector(31 downto 0);
        s_axi_arvalid : in  std_logic;
        s_axi_arready : out std_logic;
        s_axi_rdata   : out std_logic_vector(31 downto 0);
        s_axi_rresp   : out std_logic_vector(1 downto 0);
        s_axi_rvalid  : out std_logic;
        s_axi_rready  : in  std_logic;

        -- Consult interface: request a state resolution
        consult_req   : in  std_logic;
        consult_ack     : out std_logic;

        -- Input: current context vector
        -- Bits [8:6] = hexagram ID (1-64, 0=idle)
        -- Bits [5:3] = yao context (0-7)
        -- Bits [2:0] = temporal phase (0=past, 1=present, 2=future)
        context_in    : in  std_logic_vector(STATE_BITS-1 downto 0);

        -- Input: emotional weight vector (8-bit each)
        emotional_x   : in  std_logic_vector(7 downto 0);  -- Stability bias
        emotional_y   : in  std_logic_vector(7 downto 0);  -- Change bias
        emotional_z   : in  std_logic_vector(7 downto 0);  -- Alignment bias

        -- Output: resolved state
        -- Bits [8:6] = resolved hexagram ID
        -- Bits [5:3] = resolved yao context
        -- Bits [2:0] = resolved temporal phase
        state_out     : out std_logic_vector(STATE_BITS-1 downto 0);
        state_valid   : out std_logic;

        -- Output: porosity level (0.0 to 1.0, 8-bit)
        porosity_out  : out std_logic_vector(POROSITY_BITS-1 downto 0);

        -- Output: dominant trait
        -- 00=coherence, 01=chaos, 10=voiceWeight, 11=whimsy
        dominant_out  : out std_logic_vector(1 downto 0);

        -- Output: action recommendation
        -- 00=ASSERT, 01=YIELD, 10=ADAPT, 11=WAIT
        action_out    : out std_logic_vector(1 downto 0);

        -- Diagnostics: current state machine phase
        -- 000=IDLE, 001=LOAD, 010=HASH, 011=LOOKUP, 100=RESOLVE, 101=OUTPUT, 110=ERROR
        diag_phase    : out std_logic_vector(2 downto 0);

        -- Diagnostics: 640ms tick counter (10 bits = 1024 ticks)
        diag_tick     : out std_logic_vector(9 downto 0)
    );
end entity hexagram_state_machine;

architecture behavioral of hexagram_state_machine is

    -- ============================================================
    -- TYPE DEFINITIONS
    -- ============================================================

    -- Hexagram record: immutable table entry
    type hexagram_record is record
        id         : unsigned(5 downto 0);   -- 1-64
        binary     : std_logic_vector(5 downto 0);  -- 6-bit binary pattern
        category   : std_logic_vector(1 downto 0);  -- 00=sovereign, 01=transformer, 10=dissipator, 11=boundary
        action     : std_logic_vector(1 downto 0);  -- 00=ASSERT, 01=YIELD, 10=ADAPT, 11=WAIT
        porosity   : unsigned(7 downto 0);  -- 0.0-1.0 scaled to 0-255
        dominant   : std_logic_vector(1 downto 0);  -- 00=coherence, 01=chaos, 10=voiceWeight, 11=whimsy
    end record;

    -- Array of 64 hexagrams
    type hexagram_array is array (0 to 63) of hexagram_record;

    -- State machine phases
    type sm_phase is (IDLE, LOAD, HASH, LOOKUP, RESOLVE, OUTPUT, ERROR_STATE);

    -- ============================================================
    -- IMMUTABLE HEXAGRAM TABLE (ROM)
    -- Synthesized from verified King Wen sequence
    -- DO NOT MODIFY — this is the source of truth
    -- ============================================================

    constant HEX_TABLE : hexagram_array := (
        -- 01: The Creative (111111) — sovereign, ASSERT, porosity=0.25, coherence
        0  => (id=>to_unsigned(1,6),  binary=>"111111", category=>"00", action=>"00", porosity=>to_unsigned(64,8),  dominant=>"00"),
        -- 02: The Receptive (000000) — transformer, YIELD, porosity=0.25, coherence
        1  => (id=>to_unsigned(2,6),  binary=>"000000", category=>"01", action=>"01", porosity=>to_unsigned(64,8),  dominant=>"00"),
        -- 03: Difficulty at the Beginning (010001) — dissipator, ADAPT, porosity=0.75, chaos
        2  => (id=>to_unsigned(3,6),  binary=>"010001", category=>"10", action=>"10", porosity=>to_unsigned(191,8), dominant=>"01"),
        -- 04: Youthful Folly (100010) — transformer, WAIT, porosity=0.50, whimsy
        3  => (id=>to_unsigned(4,6),  binary=>"100010", category=>"01", action=>"11", porosity=>to_unsigned(128,8), dominant=>"11"),
        -- 05: Waiting (010111) — dissipator, WAIT, porosity=0.25, coherence
        4  => (id=>to_unsigned(5,6),  binary=>"010111", category=>"10", action=>"11", porosity=>to_unsigned(64,8),  dominant=>"00"),
        -- 06: Conflict (111010) — transformer, ASSERT, porosity=1.00, chaos
        5  => (id=>to_unsigned(6,6),  binary=>"111010", category=>"01", action=>"00", porosity=>to_unsigned(255,8), dominant=>"01"),
        -- 07: The Army (000010) — sovereign, ASSERT, porosity=0.00, coherence
        6  => (id=>to_unsigned(7,6),  binary=>"000010", category=>"00", action=>"00", porosity=>to_unsigned(0,8),   dominant=>"00"),
        -- 08: Holding Together (010000) — transformer, YIELD, porosity=0.50, coherence
        7  => (id=>to_unsigned(8,6),  binary=>"010000", category=>"01", action=>"01", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 09: Taming Power of the Small (110111) — dissipator, ADAPT, porosity=0.50, voiceWeight
        8  => (id=>to_unsigned(9,6),  binary=>"110111", category=>"10", action=>"10", porosity=>to_unsigned(128,8), dominant=>"10"),
        -- 10: Treading (111011) — sovereign, ADAPT, porosity=0.50, voiceWeight
        9  => (id=>to_unsigned(10,6), binary=>"111011", category=>"00", action=>"10", porosity=>to_unsigned(128,8), dominant=>"10"),
        -- 11: Peace (000111) — transformer, YIELD, porosity=0.25, coherence
        10 => (id=>to_unsigned(11,6), binary=>"000111", category=>"01", action=>"01", porosity=>to_unsigned(64,8),  dominant=>"00"),
        -- 12: Standstill (111000) — boundary, WAIT, porosity=1.00, chaos
        11 => (id=>to_unsigned(12,6), binary=>"111000", category=>"11", action=>"11", porosity=>to_unsigned(255,8), dominant=>"01"),
        -- 13: Fellowship with Men (101111) — transformer, ASSERT, porosity=0.50, voiceWeight
        12 => (id=>to_unsigned(13,6), binary=>"101111", category=>"01", action=>"00", porosity=>to_unsigned(128,8), dominant=>"10"),
        -- 14: Possession in Great Measure (111101) — sovereign, ASSERT, porosity=0.25, coherence
        13 => (id=>to_unsigned(14,6), binary=>"111101", category=>"00", action=>"00", porosity=>to_unsigned(64,8),  dominant=>"00"),
        -- 15: Modesty (001000) — transformer, YIELD, porosity=0.25, coherence
        14 => (id=>to_unsigned(15,6), binary=>"001000", category=>"01", action=>"01", porosity=>to_unsigned(64,8),  dominant=>"00"),
        -- 16: Enthusiasm (000100) — dissipator, ADAPT, porosity=0.75, voiceWeight
        15 => (id=>to_unsigned(16,6), binary=>"000100", category=>"10", action=>"10", porosity=>to_unsigned(191,8), dominant=>"10"),
        -- 17: Following (100110) — transformer, YIELD, porosity=0.50, voiceWeight
        16 => (id=>to_unsigned(17,6), binary=>"100110", category=>"01", action=>"01", porosity=>to_unsigned(128,8), dominant=>"10"),
        -- 18: Work on Decayed (011001) — dissipator, ADAPT, porosity=0.75, chaos
        17 => (id=>to_unsigned(18,6), binary=>"011001", category=>"10", action=>"10", porosity=>to_unsigned(191,8), dominant=>"01"),
        -- 19: Approach (110000) — transformer, YIELD, porosity=0.50, coherence
        18 => (id=>to_unsigned(19,6), binary=>"110000", category=>"01", action=>"01", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 20: Contemplation (000011) — boundary, WAIT, porosity=0.50, coherence
        19 => (id=>to_unsigned(20,6), binary=>"000011", category=>"11", action=>"11", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 21: Biting Through (100101) — transformer, ASSERT, porosity=0.50, coherence
        20 => (id=>to_unsigned(21,6), binary=>"100101", category=>"01", action=>"00", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 22: Grace (101001) — boundary, WAIT, porosity=0.50, coherence
        21 => (id=>to_unsigned(22,6), binary=>"101001", category=>"11", action=>"11", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 23: Splitting Apart (000001) — dissipator, WAIT, porosity=0.50, coherence
        22 => (id=>to_unsigned(23,6), binary=>"000001", category=>"10", action=>"11", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 24: Return (100000) — transformer, YIELD, porosity=0.50, coherence
        23 => (id=>to_unsigned(24,6), binary=>"100000", category=>"01", action=>"01", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 25: Innocence (100111) — sovereign, ASSERT, porosity=0.50, coherence
        24 => (id=>to_unsigned(25,6), binary=>"100111", category=>"00", action=>"00", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 26: Taming Power of the Great (111001) — boundary, ADAPT, porosity=0.50, coherence
        25 => (id=>to_unsigned(26,6), binary=>"111001", category=>"11", action=>"10", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 27: Corners of the Mouth (100001) — transformer, YIELD, porosity=0.50, coherence
        26 => (id=>to_unsigned(27,6), binary=>"100001", category=>"01", action=>"01", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 28: Preponderance of the Great (011110) — dissipator, ADAPT, porosity=0.75, chaos
        27 => (id=>to_unsigned(28,6), binary=>"011110", category=>"10", action=>"10", porosity=>to_unsigned(191,8), dominant=>"01"),
        -- 29: The Abysmal (010010) — dissipator, WAIT, porosity=0.50, coherence
        28 => (id=>to_unsigned(29,6), binary=>"010010", category=>"10", action=>"11", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 30: The Clinging (101101) — boundary, ADAPT, porosity=0.50, coherence
        29 => (id=>to_unsigned(30,6), binary=>"101101", category=>"11", action=>"10", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 31: Influence (001110) — transformer, YIELD, porosity=0.50, voiceWeight
        30 => (id=>to_unsigned(31,6), binary=>"001110", category=>"01", action=>"01", porosity=>to_unsigned(128,8), dominant=>"10"),
        -- 32: Duration (011100) — boundary, WAIT, porosity=0.50, coherence
        31 => (id=>to_unsigned(32,6), binary=>"011100", category=>"11", action=>"11", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 33: Retreat (001111) — boundary, YIELD, porosity=0.50, coherence
        32 => (id=>to_unsigned(33,6), binary=>"001111", category=>"11", action=>"01", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 34: Power of the Great (111100) — sovereign, ASSERT, porosity=0.50, coherence
        33 => (id=>to_unsigned(34,6), binary=>"111100", category=>"00", action=>"00", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 35: Progress (000101) — transformer, ADAPT, porosity=0.50, voiceWeight
        34 => (id=>to_unsigned(35,6), binary=>"000101", category=>"01", action=>"10", porosity=>to_unsigned(128,8), dominant=>"10"),
        -- 36: Darkening of the Light (101000) — dissipator, WAIT, porosity=0.50, coherence
        35 => (id=>to_unsigned(36,6), binary=>"101000", category=>"10", action=>"11", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 37: The Family (101011) — transformer, YIELD, porosity=0.50, voiceWeight
        36 => (id=>to_unsigned(37,6), binary=>"101011", category=>"01", action=>"01", porosity=>to_unsigned(128,8), dominant=>"10"),
        -- 38: Opposition (110101) — dissipator, ADAPT, porosity=0.50, chaos
        37 => (id=>to_unsigned(38,6), binary=>"110101", category=>"10", action=>"10", porosity=>to_unsigned(128,8), dominant=>"01"),
        -- 39: Obstruction (010100) — dissipator, WAIT, porosity=0.50, coherence
        38 => (id=>to_unsigned(39,6), binary=>"010100", category=>"10", action=>"11", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 40: Deliverance (001010) — transformer, ADAPT, porosity=0.50, coherence
        39 => (id=>to_unsigned(40,6), binary=>"001010", category=>"01", action=>"10", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 41: Decrease (100011) — transformer, YIELD, porosity=0.50, coherence
        40 => (id=>to_unsigned(41,6), binary=>"100011", category=>"01", action=>"01", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 42: Increase (110001) — transformer, ASSERT, porosity=0.50, coherence
        41 => (id=>to_unsigned(42,6), binary=>"110001", category=>"01", action=>"00", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 43: Breakthrough (111110) — sovereign, ASSERT, porosity=0.50, coherence
        42 => (id=>to_unsigned(43,6), binary=>"111110", category=>"00", action=>"00", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 44: Coming to Meet (011111) — boundary, WAIT, porosity=0.50, coherence
        43 => (id=>to_unsigned(44,6), binary=>"011111", category=>"11", action=>"11", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 45: Gathering Together (000110) — transformer, YIELD, porosity=0.50, voiceWeight
        44 => (id=>to_unsigned(45,6), binary=>"000110", category=>"01", action=>"01", porosity=>to_unsigned(128,8), dominant=>"10"),
        -- 46: Pushing Upward (011000) — transformer, ADAPT, porosity=0.50, coherence
        45 => (id=>to_unsigned(46,6), binary=>"011000", category=>"01", action=>"10", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 47: Oppression (010110) — dissipator, WAIT, porosity=0.50, voiceWeight
        46 => (id=>to_unsigned(47,6), binary=>"010110", category=>"10", action=>"11", porosity=>to_unsigned(128,8), dominant=>"10"),
        -- 48: The Well (011010) — boundary, YIELD, porosity=0.50, coherence
        47 => (id=>to_unsigned(48,6), binary=>"011010", category=>"11", action=>"01", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 49: Revolution (101110) — transformer, ASSERT, porosity=0.50, voiceWeight
        48 => (id=>to_unsigned(49,6), binary=>"101110", category=>"01", action=>"00", porosity=>to_unsigned(128,8), dominant=>"10"),
        -- 50: The Cauldron (011101) — sovereign, ASSERT, porosity=0.50, coherence
        49 => (id=>to_unsigned(50,6), binary=>"011101", category=>"00", action=>"00", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 51: The Arousing (100100) — sovereign, ASSERT, porosity=0.50, coherence
        50 => (id=>to_unsigned(51,6), binary=>"100100", category=>"00", action=>"00", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 52: Keeping Still (001001) — boundary, WAIT, porosity=0.50, coherence
        51 => (id=>to_unsigned(52,6), binary=>"001001", category=>"11", action=>"11", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 53: Development (001011) — transformer, ADAPT, porosity=0.50, coherence
        52 => (id=>to_unsigned(53,6), binary=>"001011", category=>"01", action=>"10", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 54: The Marrying Maiden (110100) — dissipator, YIELD, porosity=0.50, voiceWeight
        53 => (id=>to_unsigned(54,6), binary=>"110100", category=>"10", action=>"01", porosity=>to_unsigned(128,8), dominant=>"10"),
        -- 55: Abundance (001101) — sovereign, ASSERT, porosity=0.75, voiceWeight
        54 => (id=>to_unsigned(55,6), binary=>"001101", category=>"00", action=>"00", porosity=>to_unsigned(191,8), dominant=>"10"),
        -- 56: The Wanderer (101100) — dissipator, ADAPT, porosity=0.50, voiceWeight
        55 => (id=>to_unsigned(56,6), binary=>"101100", category=>"10", action=>"10", porosity=>to_unsigned(128,8), dominant=>"10"),
        -- 57: The Gentle (011011) — boundary, YIELD, porosity=0.25, coherence
        56 => (id=>to_unsigned(57,6), binary=>"011011", category=>"11", action=>"01", porosity=>to_unsigned(64,8),  dominant=>"00"),
        -- 58: The Joyous (110110) — transformer, YIELD, porosity=0.50, voiceWeight
        57 => (id=>to_unsigned(58,6), binary=>"110110", category=>"01", action=>"01", porosity=>to_unsigned(128,8), dominant=>"10"),
        -- 59: Dispersion (010011) — dissipator, ADAPT, porosity=0.75, voiceWeight
        58 => (id=>to_unsigned(59,6), binary=>"010011", category=>"10", action=>"10", porosity=>to_unsigned(191,8), dominant=>"10"),
        -- 60: Limitation (110010) — boundary, WAIT, porosity=0.25, coherence
        59 => (id=>to_unsigned(60,6), binary=>"110010", category=>"11", action=>"11", porosity=>to_unsigned(64,8),  dominant=>"00"),
        -- 61: Inner Truth (110011) — transformer, YIELD, porosity=0.25, coherence
        60 => (id=>to_unsigned(61,6), binary=>"110011", category=>"01", action=>"01", porosity=>to_unsigned(64,8),  dominant=>"00"),
        -- 62: Preponderance of the Small (001100) — dissipator, WAIT, porosity=0.50, coherence
        61 => (id=>to_unsigned(62,6), binary=>"001100", category=>"10", action=>"11", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 63: After Completion (101010) — boundary, WAIT, porosity=0.50, coherence
        62 => (id=>to_unsigned(63,6), binary=>"101010", category=>"11", action=>"11", porosity=>to_unsigned(128,8), dominant=>"00"),
        -- 64: Before Completion (010101) — transformer, ADAPT, porosity=0.75, voiceWeight
        63 => (id=>to_unsigned(64,6), binary=>"010101", category=>"01", action=>"10", porosity=>to_unsigned(191,8), dominant=>"10")
    );

    -- ============================================================
    -- DETERMINISTIC HASH FUNCTION
    -- No pseudo-RNG. All state transitions are hash-derived.
    -- Hash = fn(context_in, emotional_vector, tick_counter)
    -- ============================================================

    function deterministic_hash(
        ctx    : std_logic_vector(STATE_BITS-1 downto 0);
        emo_x  : std_logic_vector(7 downto 0);
        emo_y  : std_logic_vector(7 downto 0);
        emo_z  : std_logic_vector(7 downto 0);
        tick   : unsigned(9 downto 0)
    ) return unsigned is
        variable h : unsigned(31 downto 0);
        variable t : unsigned(31 downto 0);
    begin
        -- Mix context into hash
        h := unsigned("0000000000000000000" & ctx);

        -- XOR with emotional weights (shifted to avoid collision)
        h := h xor (unsigned(emo_x) & unsigned(emo_y) & unsigned(emo_z) & x"00");

        -- Mix with tick counter (640ms metabolic rhythm)
        t := resize(tick, 32);
        h := h xor (t sll 5) xor (t srl 7);

        -- Final avalanche
        h := h xor (h sll 13) xor (h srl 17) xor (h sll 5);

        -- Collapse to 9 bits (512 states)
        return h(8 downto 0);
    end function;

    -- ============================================================
    -- STATE REGISTERS
    -- ============================================================

    signal current_phase   : sm_phase;
    signal tick_counter    : unsigned(9 downto 0);  -- 640ms ticks
    signal state_reg       : std_logic_vector(STATE_BITS-1 downto 0);
    signal porosity_reg    : unsigned(POROSITY_BITS-1 downto 0);
    signal dominant_reg    : std_logic_vector(1 downto 0);
    signal action_reg      : std_logic_vector(1 downto 0);
    signal hash_result     : unsigned(STATE_BITS-1 downto 0);
    signal hex_index       : unsigned(5 downto 0);

    -- AXI4-Lite slave signals
    signal axi_awready_reg : std_logic;
    signal axi_wready_reg  : std_logic;
    signal axi_bvalid_reg  : std_logic;
    signal axi_arready_reg : std_logic;
    signal axi_rvalid_reg  : std_logic;
    signal axi_rdata_reg   : std_logic_vector(31 downto 0);

    -- Control register (AXI address 0x00)
    signal ctrl_reg        : std_logic_vector(31 downto 0);
    -- Status register (AXI address 0x04)
    signal status_reg      : std_logic_vector(31 downto 0);
    -- Context register (AXI address 0x08)
    signal context_reg     : std_logic_vector(31 downto 0);
    -- Result register (AXI address 0x0C)
    signal result_reg      : std_logic_vector(31 downto 0);

begin

    -- ============================================================
    -- COMBINATORIAL OUTPUTS
    -- ============================================================

    state_out    <= state_reg;
    state_valid  <= '1' when current_phase = OUTPUT else '0';
    porosity_out <= std_logic_vector(porosity_reg);
    dominant_out <= dominant_reg;
    action_out   <= action_reg;

    -- Diagnostics
    diag_phase <= "000" when current_phase = IDLE else
                  "001" when current_phase = LOAD else
                  "010" when current_phase = HASH else
                  "011" when current_phase = LOOKUP else
                  "100" when current_phase = RESOLVE else
                  "101" when current_phase = OUTPUT else
                  "110" when current_phase = ERROR_STATE else
                  "111";
    diag_tick <= std_logic_vector(tick_counter);

    -- AXI4-Lite outputs
    s_axi_awready <= axi_awready_reg;
    s_axi_wready  <= axi_wready_reg;
    s_axi_bresp   <= "00";  -- OKAY
    s_axi_bvalid  <= axi_bvalid_reg;
    s_axi_arready <= axi_arready_reg;
    s_axi_rdata   <= axi_rdata_reg;
    s_axi_rresp   <= "00";  -- OKAY
    s_axi_rvalid  <= axi_rvalid_reg;

    consult_ack <= '1' when current_phase = OUTPUT else '0';

    -- ============================================================
    -- MAIN STATE MACHINE
    -- ============================================================

    process(clk, rst_n)
        variable hex_id   : unsigned(5 downto 0);
        variable yao_ctx  : unsigned(2 downto 0);
        variable temp_phase : unsigned(1 downto 0);
        variable hex_rec  : hexagram_record;
        variable hash_val : unsigned(STATE_BITS-1 downto 0);
    begin
        if rst_n = '0' then
            current_phase   <= IDLE;
            tick_counter    <= (others => '0');
            state_reg       <= (others => '0');
            porosity_reg    <= (others => '0');
            dominant_reg    <= (others => '0');
            action_reg      <= (others => '0');
            hash_result     <= (others => '0');
            hex_index       <= (others => '0');

            axi_awready_reg <= '0';
            axi_wready_reg  <= '0';
            axi_bvalid_reg  <= '0';
            axi_arready_reg <= '0';
            axi_rvalid_reg  <= '0';
            axi_rdata_reg   <= (others => '0');

            ctrl_reg        <= (others => '0');
            status_reg      <= (others => '0');
            context_reg     <= (others => '0');
            result_reg      <= (others => '0');

        elsif rising_edge(clk) then
            -- Default: clear single-cycle signals
            axi_awready_reg <= '0';
            axi_wready_reg  <= '0';
            axi_bvalid_reg  <= '0';
            axi_arready_reg <= '0';
            axi_rvalid_reg  <= '0';

            -- Tick counter: increments every 640ms (assumed clk division external)
            -- In practice, this would be driven by a prescaled clock
            tick_counter <= tick_counter + 1;

            case current_phase is

                when IDLE =>
                    -- Wait for consult request or AXI write to context register
                    if consult_req = '1' then
                        current_phase <= LOAD;
                    elsif s_axi_awvalid = '1' and s_axi_wvalid = '1' then
                        -- AXI write transaction
                        axi_awready_reg <= '1';
                        axi_wready_reg  <= '1';
                        axi_bvalid_reg  <= '1';

                        case s_axi_awaddr(7 downto 0) is
                            when x"00" =>
                                ctrl_reg <= s_axi_wdata;
                            when x"08" =>
                                context_reg <= s_axi_wdata;
                                -- Auto-trigger consult on context write
                                current_phase <= LOAD;
                            when others =>
                                null;
                        end case;
                    elsif s_axi_arvalid = '1' then
                        -- AXI read transaction
                        axi_arready_reg <= '1';
                        axi_rvalid_reg  <= '1';

                        case s_axi_araddr(7 downto 0) is
                            when x"00" =>
                                axi_rdata_reg <= ctrl_reg;
                            when x"04" =>
                                axi_rdata_reg <= status_reg;
                            when x"08" =>
                                axi_rdata_reg <= context_reg;
                            when x"0C" =>
                                axi_rdata_reg <= result_reg;
                            when others =>
                                axi_rdata_reg <= (others => '0');
                        end case;
                    end if;

                when LOAD =>
                    -- Load context from register or input
                    if ctrl_reg(0) = '1' then
                        -- Use AXI context register
                        state_reg <= context_reg(STATE_BITS-1 downto 0);
                    else
                        -- Use direct input
                        state_reg <= context_in;
                    end if;
                    current_phase <= HASH;

                when HASH =>
                    -- Compute deterministic hash
                    hash_val := deterministic_hash(
                        state_reg,
                        emotional_x,
                        emotional_y,
                        emotional_z,
                        tick_counter
                    );
                    hash_result <= hash_val;
                    current_phase <= LOOKUP;

                when LOOKUP =>
                    -- Decode hash into hexagram + context
                    -- hash_result[8:3] = hexagram ID (0-63, maps to 1-64)
                    -- hash_result[2:0] = yao context (0-7)
                    hex_id := hash_result(8 downto 3);
                    yao_ctx := hash_result(2 downto 0);

                    -- Clamp hex_id to valid range (0-63)
                    if hex_id > 63 then
                        hex_id := to_unsigned(63, 6);
                    end if;

                    hex_index <= hex_id;
                    current_phase <= RESOLVE;

                when RESOLVE =>
                    -- Look up hexagram record from immutable table
                    hex_rec := HEX_TABLE(to_integer(hex_index));

                    -- Resolve porosity based on yao context
                    -- Porosity modulated by emotional weights
                    porosity_reg <= hex_rec.porosity + unsigned(emotional_x(3 downto 0));

                    -- Dominant trait from table
                    dominant_reg <= hex_rec.dominant;

                    -- Action from table
                    action_reg <= hex_rec.action;

                    -- Build output state
                    -- [8:6] = hexagram ID
                    -- [5:3] = yao context
                    -- [2:0] = temporal phase (from hash)
                    state_reg <= std_logic_vector(hex_index) & std_logic_vector(hash_result(2 downto 0));

                    -- Update result register for AXI reads
                    result_reg <= "000000000000000000" & std_logic_vector(hex_index) & 
                                  std_logic_vector(hash_result(2 downto 0)) & 
                                  std_logic_vector(hex_rec.porosity) & 
                                  hex_rec.dominant & hex_rec.action;

                    current_phase <= OUTPUT;

                when OUTPUT =>
                    -- Hold output for one cycle, then return to IDLE
                    status_reg <= x"00000001";  -- Done flag
                    current_phase <= IDLE;

                when ERROR_STATE =>
                    -- Error recovery: reset to idle
                    status_reg <= x"80000000";  -- Error flag
                    current_phase <= IDLE;

                when others =>
                    current_phase <= ERROR_STATE;

            end case;
        end if;
    end process;

end architecture behavioral;
