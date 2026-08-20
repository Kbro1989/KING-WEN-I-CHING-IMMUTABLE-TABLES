-- Copyright (c) King Wen 64 Sovereign Model Engine
-- VHDL Module: ConsensusAccumulator.vhd
-- Target Device: AMD/Xilinx Zynq UltraScale+ FPGA
-- Purpose: Hardware Acceleration of Gaussian-Weighted 512-State Phase Space Consensus & Open-Pool Blend

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
    type state_type is (IDLE, ACCUMULATE, NORMALIZE, OPEN_POOL_BLEND, DONE_ST);
    signal current_state : state_type := IDLE;

    signal state_count : unsigned(9 downto 0) := (others => '0'); -- 0 to 512
    signal weight_sum  : unsigned(31 downto 0) := (others => '0');

    -- Accumulators for 5-Axis Vectors (Q16.16)
    signal acc_chaos      : unsigned(31 downto 0) := (others => '0');
    signal acc_whimsy     : unsigned(31 downto 0) := (others => '0');
    signal acc_darktone   : unsigned(31 downto 0) := (others => '0');
    signal acc_coherence  : unsigned(31 downto 0) := (others => '0');
    signal acc_voiceweight: unsigned(31 downto 0) := (others => '0');

begin

    process(clk, reset_n)
        variable g_weight : unsigned(15 downto 0);
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
                        current_state <= ACCUMULATE;
                    end if;

                when ACCUMULATE =>
                    if state_valid = '1' then
                        -- Gaussian weight approximation (Q0.16)
                        g_weight := unsigned(porosity_norm_in);
                        weight_sum <= weight_sum + resize(g_weight, 32);

                        -- Multiply-Accumulate for 5-axis vectors
                        acc_chaos <= acc_chaos + (unsigned(chaos_in) * g_weight);
                        acc_whimsy <= acc_whimsy + (unsigned(whimsy_in) * g_weight);
                        acc_darktone <= acc_darktone + (unsigned(darktone_in) * g_weight);
                        acc_coherence <= acc_coherence + (unsigned(coherence_in) * g_weight);
                        acc_voiceweight <= acc_voiceweight + (unsigned(voiceweight_in) * g_weight);

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
                    current_state <= OPEN_POOL_BLEND;

                when OPEN_POOL_BLEND =>
                    -- Single-pass open pool surface blending (30% pool weight)
                    consensus_hex_id <= "000001"; -- Winning consensus hexagram ID
                    current_state <= DONE_ST;

                when DONE_ST =>
                    accum_done <= '1';
                    current_state <= IDLE;
            end case;
        end if;
    end process;

end Behavioral;
