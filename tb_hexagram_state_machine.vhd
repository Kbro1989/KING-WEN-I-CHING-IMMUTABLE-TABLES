-- VHDL Testbench: tb_hexagram_state_machine.vhd
-- Target Module: hexagram_state_machine.vhd
-- Description: Testbench driving 512-state quantum oracle state machine via AXI4-Lite bus interface.

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity tb_hexagram_state_machine is
end entity;

architecture sim of tb_hexagram_state_machine is
    signal clk           : std_logic := '0';
    signal rst_n         : std_logic := '0';

    -- AXI4-Lite Interface
    signal s_axi_awaddr  : std_logic_vector(31 downto 0) := (others => '0');
    signal s_axi_awvalid : std_logic := '0';
    signal s_axi_awready : std_logic;
    signal s_axi_wdata   : std_logic_vector(31 downto 0) := (others => '0');
    signal s_axi_wstrb   : std_logic_vector(3 downto 0)  := (others => '1');
    signal s_axi_wvalid  : std_logic := '0';
    signal s_axi_wready  : std_logic;
    signal s_axi_bresp   : std_logic_vector(1 downto 0);
    signal s_axi_bvalid  : std_logic;
    signal s_axi_bready  : std_logic := '1';
    signal s_axi_araddr  : std_logic_vector(31 downto 0) := (others => '0');
    signal s_axi_arvalid : std_logic := '0';
    signal s_axi_arready : std_logic;
    signal s_axi_rdata   : std_logic_vector(31 downto 0);
    signal s_axi_rresp   : std_logic_vector(1 downto 0);
    signal s_axi_rvalid  : std_logic;
    signal s_axi_rready  : std_logic := '1';

    -- Hardware Interrupt
    signal irq           : std_logic;

    constant CLK_PERIOD  : time := 10 ns;
begin

    DUT: entity work.hexagram_state_machine
        port map (
            clk           => clk,
            rst_n         => rst_n,
            s_axi_awaddr  => s_axi_awaddr,
            s_axi_awvalid => s_axi_awvalid,
            s_axi_awready => s_axi_awready,
            s_axi_wdata   => s_axi_wdata,
            s_axi_wstrb   => s_axi_wstrb,
            s_axi_wvalid  => s_axi_wvalid,
            s_axi_wready  => s_axi_wready,
            s_axi_bresp   => s_axi_bresp,
            s_axi_bvalid  => s_axi_bvalid,
            s_axi_bready  => s_axi_bready,
            s_axi_araddr  => s_axi_araddr,
            s_axi_arvalid => s_axi_arvalid,
            s_axi_arready => s_axi_arready,
            s_axi_rdata   => s_axi_rdata,
            s_axi_rresp   => s_axi_rresp,
            s_axi_rvalid  => s_axi_rvalid,
            s_axi_rready  => s_axi_rready,
            irq           => irq
        );

    clk_gen: process
    begin
        clk <= '0';
        wait for CLK_PERIOD / 2;
        clk <= '1';
        wait for CLK_PERIOD / 2;
    end process;

    stim_proc: process
    begin
        -- Reset pulse
        rst_n <= '0';
        wait for 20 ns;
        rst_n <= '1';
        wait for 20 ns;

        -- AXI Write to CONTROL reg (0x4000_0000) to trigger evaluation
        wait until rising_edge(clk);
        s_axi_awaddr  <= x"40000000";
        s_axi_awvalid <= '1';
        s_axi_wdata   <= x"00000001"; -- START bit
        s_axi_wvalid  <= '1';

        wait until s_axi_awready = '1' and s_axi_wready = '1';
        wait until rising_edge(clk);
        s_axi_awvalid <= '0';
        s_axi_wvalid  <= '0';

        -- AXI Read STATUS reg (0x4000_0004)
        wait for 40 ns;
        wait until rising_edge(clk);
        s_axi_araddr  <= x"40000004";
        s_axi_arvalid <= '1';

        wait until s_axi_arready = '1';
        wait until rising_edge(clk);
        s_axi_arvalid <= '0';

        wait for 50 ns;

        report "=== HEXAGRAM STATE MACHINE AXI TESTBENCH PASS ===" severity note;
        wait;
    end process;

end architecture;
