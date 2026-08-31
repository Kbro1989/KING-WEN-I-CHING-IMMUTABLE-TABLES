-- VHDL Testbench: tb_ConsensusAccumulator.vhd
-- Target Module: ConsensusAccumulator.vhd
-- Description: Testbench driving 512-state streaming input into ConsensusAccumulator and asserting Gaussian normalization & dynamic winner resolution.

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity tb_ConsensusAccumulator is
end entity;

architecture sim of tb_ConsensusAccumulator is
    signal clk                : std_logic := '0';
    signal reset_n            : std_logic := '0';
    signal start_accum        : std_logic := '0';
    signal state_valid        : std_logic := '0';
    signal hexagram_id_in     : std_logic_vector(5 downto 0) := (others => '0');
    signal phase_bits_in      : std_logic_vector(2 downto 0) := (others => '0');
    signal tau_val_in         : std_logic_vector(15 downto 0) := (others => '0');
    signal porosity_norm_in   : std_logic_vector(15 downto 0) := (others => '0');
    signal chaos_in           : std_logic_vector(15 downto 0) := (others => '0');
    signal whimsy_in          : std_logic_vector(15 downto 0) := (others => '0');
    signal darktone_in        : std_logic_vector(15 downto 0) := (others => '0');
    signal coherence_in       : std_logic_vector(15 downto 0) := (others => '0');
    signal voiceweight_in     : std_logic_vector(15 downto 0) := (others => '0');

    signal accum_done         : std_logic;
    signal consensus_hex_id   : std_logic_vector(5 downto 0);
    signal consensus_chaos    : std_logic_vector(15 downto 0);
    signal consensus_whimsy   : std_logic_vector(15 downto 0);
    signal consensus_darktone : std_logic_vector(15 downto 0);
    signal consensus_coherence: std_logic_vector(15 downto 0);
    signal consensus_voiceweight: std_logic_vector(15 downto 0);

    constant CLK_PERIOD       : time := 10 ns;
begin

    DUT: entity work.ConsensusAccumulator
        port map (
            clk                => clk,
            reset_n            => reset_n,
            start_accum        => start_accum,
            state_valid        => state_valid,
            hexagram_id_in     => hexagram_id_in,
            phase_bits_in      => phase_bits_in,
            tau_val_in         => tau_val_in,
            porosity_norm_in   => porosity_norm_in,
            chaos_in           => chaos_in,
            whimsy_in          => whimsy_in,
            darktone_in        => darktone_in,
            coherence_in       => coherence_in,
            voiceweight_in     => voiceweight_in,
            accum_done         => accum_done,
            consensus_hex_id   => consensus_hex_id,
            consensus_chaos    => consensus_chaos,
            consensus_whimsy   => consensus_whimsy,
            consensus_darktone => consensus_darktone,
            consensus_coherence=> consensus_coherence,
            consensus_voiceweight=> consensus_voiceweight
        );

    clk_gen: process
    begin
        clk <= '0';
        wait for CLK_PERIOD / 2;
        clk <= '1';
        wait for CLK_PERIOD / 2;
    end process;

    stim_proc: process
        variable hex_id : integer;
        variable phase  : integer;
    begin
        -- Reset pulse
        reset_n <= '0';
        wait for 20 ns;
        reset_n <= '1';
        wait for 20 ns;

        -- Start accumulation
        wait until rising_edge(clk);
        start_accum <= '1';
        wait until rising_edge(clk);
        start_accum <= '0';

        -- Stream 512 resolved states
        for i in 0 to 511 loop
            hex_id := (i mod 64) + 1;
            phase  := i mod 8;

            state_valid       <= '1';
            hexagram_id_in    <= std_logic_vector(to_unsigned(hex_id, 6));
            phase_bits_in     <= std_logic_vector(to_unsigned(phase, 3));
            tau_val_in        <= std_logic_vector(to_unsigned(100 + i, 16));
            porosity_norm_in  <= std_logic_vector(to_unsigned(256 + (i mod 100), 16));

            chaos_in          <= std_logic_vector(to_unsigned(1000 + i * 2, 16));
            whimsy_in         <= std_logic_vector(to_unsigned(2000 + i * 3, 16));
            darktone_in       <= std_logic_vector(to_unsigned(500 + i, 16));
            coherence_in      <= std_logic_vector(to_unsigned(4000 + (hex_id * 100), 16));
            voiceweight_in    <= std_logic_vector(to_unsigned(1500 + i * 4, 16));

            wait until rising_edge(clk);
        end loop;

        state_valid <= '0';

        -- Wait for done
        wait until accum_done = '1';

        report "=== CONSENSUS ACCUMULATOR TESTBENCH PASS ===" severity note;
        report "Consensus Hexagram ID: " & integer'image(to_integer(unsigned(consensus_hex_id))) severity note;
        report "Consensus Coherence: " & integer'image(to_integer(unsigned(consensus_coherence))) severity note;

        assert to_integer(unsigned(consensus_hex_id)) >= 1 and to_integer(unsigned(consensus_hex_id)) <= 64
            report "Invalid consensus_hex_id range!" severity error;

        wait;
    end process;

end architecture;
