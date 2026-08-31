-- VHDL Testbench: tb_DynamicEmotionalInputDerivator.vhd
-- Target Module: DynamicEmotionalInputDerivator.vhd
-- Description: Testbench driving streaming ASCII text and intent intensity to derive dynamic non-50 emotional state.

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity tb_DynamicEmotionalInputDerivator is
end entity;

architecture sim of tb_DynamicEmotionalInputDerivator is
    signal clk                 : std_logic := '0';
    signal reset_n             : std_logic := '0';
    signal start_derive        : std_logic := '0';
    signal char_valid          : std_logic := '0';
    signal char_ascii          : std_logic_vector(7 downto 0) := (others => '0');
    signal text_end            : std_logic := '0';
    signal intent_intensity    : std_logic_vector(7 downto 0) := (others => '0');

    signal derived_done        : std_logic;
    signal emotional_input_out : std_logic_vector(7 downto 0);

    constant CLK_PERIOD        : time := 10 ns;
begin

    DUT: entity work.DynamicEmotionalInputDerivator
        port map (
            clk                 => clk,
            reset_n             => reset_n,
            start_derive        => start_derive,
            char_valid          => char_valid,
            char_ascii          => char_ascii,
            text_end            => text_end,
            intent_intensity    => intent_intensity,
            derived_done        => derived_done,
            emotional_input_out => emotional_input_out
        );

    clk_gen: process
    begin
        clk <= '0';
        wait for CLK_PERIOD / 2;
        clk <= '1';
        wait for CLK_PERIOD / 2;
    end process;

    stim_proc: process
        type ascii_arr is array (0 to 11) of integer;
        constant sample_str : ascii_arr := (75, 105, 110, 103, 32, 87, 101, 110, 32, 54, 52, 33); -- "King Wen 64!"
    begin
        -- Reset pulse
        reset_n <= '0';
        wait for 20 ns;
        reset_n <= '1';
        wait for 20 ns;

        -- Start derivation
        wait until rising_edge(clk);
        start_derive <= '1';
        intent_intensity <= std_logic_vector(to_unsigned(180, 8));
        wait until rising_edge(clk);
        start_derive <= '0';

        -- Stream ASCII chars
        for i in 0 to 11 loop
            char_valid <= '1';
            char_ascii <= std_logic_vector(to_unsigned(sample_str(i), 8));
            wait until rising_edge(clk);
        end loop;

        char_valid <= '0';
        text_end <= '1';
        wait until rising_edge(clk);
        text_end <= '0';

        -- Wait for completed derivation
        wait until derived_done = '1';

        report "=== DYNAMIC EMOTIONAL INPUT DERIVATOR TESTBENCH PASS ===" severity note;
        report "Derived Emotional Input: " & integer'image(to_integer(unsigned(emotional_input_out))) severity note;

        assert to_integer(unsigned(emotional_input_out)) >= 1 and to_integer(unsigned(emotional_input_out)) <= 99
            report "Derived emotional input out of 1..99 range!" severity error;

        assert to_integer(unsigned(emotional_input_out)) /= 50
            report "Derived emotional input stuck at flat 50!" severity error;

        wait;
    end process;

end architecture;
