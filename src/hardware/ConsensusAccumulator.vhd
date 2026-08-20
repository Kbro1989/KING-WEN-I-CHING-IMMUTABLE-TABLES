-- Copyright (c) King Wen 64 Sovereign Model Engine
-- VHDL Module: ConsensusAccumulator.vhd
-- Target Device: AMD/Xilinx Zynq UltraScale+ FPGA
-- Purpose: Hardware Acceleration of Gaussian-Weighted 512-State Phase Space Consensus & Dynamic Winner Resolution

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity ConsensusAccumulator is
    Port (
        clk               : in  STD_LOGIC;
        reset_n           : in  STD_LOGIC;
        start_accum       : in  STD_LOGIC;
        
        -- State Input Streaming Interface (512 Resolved States)
        state_valid       : in  STD_LOGIC;
        hexagram_id_in    : in  STD_LOGIC_VECTOR(5 downto 0);  -- 1..64
        phase_bits_in     : in  STD_LOGIC_VECTOR(2 downto 0);  -- 0..7
        tau_val_in        : in  STD_LOGIC_VECTOR(15 downto 0); -- Fixed-point (Q8.8)
        porosity_norm_in  : in  STD_LOGIC_VECTOR(15 downto 0); -- Fixed-point (Q0.16)
        
        -- 5-Axis Vector Inputs (Q0.16)
        chaos_in          : in  STD_LOGIC_VECTOR(15 downto 0);
        whimsy_in         : in  STD_LOGIC_VECTOR(15 downto 0);
        darktone_in       : in  STD_LOGIC_VECTOR(15 downto 0);
        coherence_in      : in  STD_LOGIC_VECTOR(15 downto 0);
        voiceweight_in    : in  STD_LOGIC_VECTOR(15 downto 0);
        
        -- Consensus Outputs
        accum_done        : out STD_LOGIC;
        consensus_hex_id  : out STD_LOGIC_VECTOR(5 downto 0);
        consensus_chaos   : out STD_LOGIC_VECTOR(15 downto 0);
        consensus_whimsy  : out STD_LOGIC_VECTOR(15 downto 0);
        consensus_darktone: out STD_LOGIC_VECTOR(15 downto 0);
        consensus_coherence: out STD_LOGIC_VECTOR(15 downto 0);
        consensus_voiceweight: out STD_LOGIC_VECTOR(15 downto 0)
    );
end ConsensusAccumulator;

architecture Behavioral of ConsensusAccumulator is
    type state_type is (IDLE, ACCUMULATE, NORMALIZE, FIND_WINNER, DONE_ST);
    signal current_state : state_type := IDLE;

    signal state_count : unsigned(9 downto 0) := (others => '0'); -- 0 to 512
    signal weight_sum  : unsigned(31 downto 0) := (others => '0');

    -- 48-bit Accumulators to prevent overflow (512 * (65535 * 65535) requires 41 bits min)
    signal acc_chaos      : unsigned(47 downto 0) := (others => '0');
    signal acc_whimsy     : unsigned(47 downto 0) := (others => '0');
    signal acc_darktone   : unsigned(47 downto 0) := (others => '0');
    signal acc_coherence  : unsigned(47 downto 0) := (others => '0');
    signal acc_voiceweight: unsigned(47 downto 0) := (others => '0');

    -- Dynamic Winner Tracking
    type hex_score_array is array (1 to 64) of unsigned(31 downto 0);
    signal hex_scores : hex_score_array := (others => (others => '0'));
    signal winning_id : unsigned(5 downto 0) := "000001";

begin

    process(clk, reset_n)
        variable g_weight   : unsigned(15 downto 0);
        variable item_h_id  : integer range 1 to 64;
        variable max_score  : unsigned(31 downto 0);
        variable best_hex   : unsigned(5 downto 0);
        variable state_score: unsigned(31 downto 0);
    begin
        if reset_n = '0' then
            current_state <= IDLE;
            state_count <= (others => '0');
            weight_sum <= (others => '0');
            acc_chaos <= (others => '0');
            acc_whimsy <= (others => '0');
            acc_darktone <= (others => '0');
            acc_coherence <= (others => '0');
            acc_voiceweight <= (others => '0');
            accum_done <= '0';
            consensus_hex_id <= (others => '0');
            winning_id <= "000001";
            hex_scores <= (others => (others => '0'));
        elsif rising_edge(clk) then
            case current_state is
                when IDLE =>
                    accum_done <= '0';
                    if start_accum = '1' then
                        state_count <= (others => '0');
                        weight_sum <= (others => '0');
                        acc_chaos <= (others => '0');
                        acc_whimsy <= (others => '0');
                        acc_darktone <= (others => '0');
                        acc_coherence <= (others => '0');
                        acc_voiceweight <= (others => '0');
                        hex_scores <= (others => (others => '0'));
                        current_state <= ACCUMULATE;
                    end if;

                when ACCUMULATE =>
                    if state_valid = '1' then
                        -- Gaussian weight approximation (Q0.16)
                        g_weight := unsigned(porosity_norm_in);
                        weight_sum <= weight_sum + resize(g_weight, 32);

                        -- Multiply-Accumulate for 5-axis vectors with 48-bit wide accumulators
                        acc_chaos <= acc_chaos + (resize(unsigned(chaos_in), 32) * g_weight);
                        acc_whimsy <= acc_whimsy + (resize(unsigned(whimsy_in), 32) * g_weight);
                        acc_darktone <= acc_darktone + (resize(unsigned(darktone_in), 32) * g_weight);
                        acc_coherence <= acc_coherence + (resize(unsigned(coherence_in), 32) * g_weight);
                        acc_voiceweight <= acc_voiceweight + (resize(unsigned(voiceweight_in), 32) * g_weight);

                        -- Dynamic Score Accumulation per Hexagram ID
                        item_h_id := to_integer(unsigned(hexagram_id_in));
                        if item_h_id >= 1 and item_h_id <= 64 then
                            state_score := resize(g_weight + unsigned(coherence_in) / 2, 32);
                            hex_scores(item_h_id) <= hex_scores(item_h_id) + state_score;
                        end if;

                        state_count <= state_count + 1;
                        if state_count = 511 then
                            current_state <= NORMALIZE;
                        end if;
                    end if;

                when NORMALIZE =>
                    -- Division by total weight sum to normalize Gaussian consensus
                    if weight_sum > 0 then
                        consensus_chaos <= std_logic_vector(resize(acc_chaos / weight_sum, 16));
                        consensus_whimsy <= std_logic_vector(resize(acc_whimsy / weight_sum, 16));
                        consensus_darktone <= std_logic_vector(resize(acc_darktone / weight_sum, 16));
                        consensus_coherence <= std_logic_vector(resize(acc_coherence / weight_sum, 16));
                        consensus_voiceweight <= std_logic_vector(resize(acc_voiceweight / weight_sum, 16));
                    end if;
                    current_state <= FIND_WINNER;

                when FIND_WINNER =>
                    -- Dynamic Winner Selection: find hexagram ID with max accumulated score
                    max_score := (others => '0');
                    best_hex := "000001";
                    for idx in 1 to 64 loop
                        if hex_scores(idx) > max_score then
                            max_score := hex_scores(idx);
                            best_hex := to_unsigned(idx, 6);
                        end if;
                    end loop;
                    winning_id <= best_hex;
                    consensus_hex_id <= std_logic_vector(best_hex);
                    current_state <= DONE_ST;

                when DONE_ST =>
                    accum_done <= '1';
                    current_state <= IDLE;
            end case;
        end if;
    end process;

end Behavioral;
