-- Copyright (c) King Wen 64 Sovereign Model Engine
-- VHDL Module: DynamicEmotionalInputDerivator.vhd
-- Target Device: AMD/Xilinx Zynq UltraScale+ FPGA
-- Purpose: Hardware derivation of dynamic non-50 emotional input (ASCII entropy + intent intensity + vector seed)

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity DynamicEmotionalInputDerivator is
    Port (
        clk                 : in  STD_LOGIC;
        reset_n             : in  STD_LOGIC;
        start_derive        : in  STD_LOGIC;
        
        -- Streamed Request Text Character (ASCII)
        char_valid          : in  STD_LOGIC;
        char_ascii          : in  STD_LOGIC_VECTOR(7 downto 0);
        text_end            : in  STD_LOGIC;
        
        -- Intent Intensity (Q0.8)
        intent_intensity    : in  STD_LOGIC_VECTOR(7 downto 0);
        
        -- Output Dynamic Emotional State (1 to 99, never flat 50)
        derived_done        : out STD_LOGIC;
        emotional_input_out : out STD_LOGIC_VECTOR(7 downto 0) -- 8-bit uint (1..99)
    );
end DynamicEmotionalInputDerivator;

architecture Behavioral of DynamicEmotionalInputDerivator is
    signal char_sum        : unsigned(15 downto 0) := (others => '0');
    signal dynamic_result  : unsigned(7 downto 0)  := to_unsigned(52, 8);
    signal processing      : STD_LOGIC := '0';
begin

    process(clk, reset_n)
        variable entropy_mod   : unsigned(7 downto 0);
        variable intensity_pts : unsigned(7 downto 0);
        variable raw_sum       : unsigned(7 downto 0);
    begin
        if reset_n = '0' then
            char_sum <= (others => '0');
            derived_done <= '0';
            emotional_input_out <= std_logic_vector(to_unsigned(52, 8));
            processing <= '0';
        elsif rising_edge(clk) then
            if start_derive = '1' then
                char_sum <= (others => '0');
                derived_done <= '0';
                processing <= '1';
            elsif processing = '1' then
                if char_valid = '1' then
                    char_sum <= char_sum + unsigned(char_ascii);
                elsif text_end = '1' then
                    -- 1. ASCII Entropy (1..37)
                    entropy_mod := resize((char_sum mod 37) + 1, 8);

                    -- 2. Intent Intensity (0..25)
                    intensity_pts := resize((unsigned(intent_intensity) * 25) / 255, 8);

                    -- 3. Base offset (15) + entropy + intensity
                    raw_sum := to_unsigned(15, 8) + entropy_mod + intensity_pts;

                    -- Clamp to range [1..99]
                    if raw_sum < 1 then
                        raw_sum := to_unsigned(1, 8);
                    elsif raw_sum > 99 then
                        raw_sum := to_unsigned(99, 8);
                    end if;

                    -- Eliminate flat 50
                    if raw_sum = 50 then
                        raw_sum := to_unsigned(51, 8);
                    end if;

                    emotional_input_out <= std_logic_vector(raw_sum);
                    derived_done <= '1';
                    processing <= '0';
                end if;
            end if;
        end if;
    end process;

end Behavioral;
