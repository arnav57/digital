// Wrapper: generated Platform Designer system + SDRAM functional model.
// Exposes clk / reset / Avalon-MM slave (s1) as top-level ports for cocotb.
`timescale 1ns / 1ps
module sdram_tb_top (
    input  wire        clk_i,
    input  wire        rstn_i,

    input  wire [21:0] s1_address_i,
    input  wire [3:0]  s1_byteenable_n_i,
    input  wire        s1_chipselect_i,
    input  wire [31:0] s1_writedata_i,
    input  wire        s1_read_n_i,
    input  wire        s1_write_n_i,
    output wire [31:0] s1_readdata_o,
    output wire        s1_readdatavalid_o,
    output wire        s1_waitrequest_o
);

    // SDRAM-side bus between controller and chip model
    wire [11:0] sdram_addr;
    wire [1:0]  sdram_ba;
    wire        sdram_cas_n, sdram_cke, sdram_cs_n, sdram_ras_n, sdram_we_n;
    wire [3:0]  sdram_dqm;
    wire [31:0] sdram_dq;

    sdram I_sdram (
        .clk_clk                (clk_i),
        .reset_reset_n          (rstn_i),
        .sdram_s1_address       (s1_address_i),
        .sdram_s1_byteenable_n  (s1_byteenable_n_i),
        .sdram_s1_chipselect    (s1_chipselect_i),
        .sdram_s1_writedata     (s1_writedata_i),
        .sdram_s1_read_n        (s1_read_n_i),
        .sdram_s1_write_n       (s1_write_n_i),
        .sdram_s1_readdata      (s1_readdata_o),
        .sdram_s1_readdatavalid (s1_readdatavalid_o),
        .sdram_s1_waitrequest   (s1_waitrequest_o),
        .sdram_wire_addr        (sdram_addr),
        .sdram_wire_ba          (sdram_ba),
        .sdram_wire_cas_n       (sdram_cas_n),
        .sdram_wire_cke         (sdram_cke),
        .sdram_wire_cs_n        (sdram_cs_n),
        .sdram_wire_dq          (sdram_dq),
        .sdram_wire_dqm         (sdram_dqm),
        .sdram_wire_ras_n       (sdram_ras_n),
        .sdram_wire_we_n        (sdram_we_n)
    );

    // Functional SDRAM chip model (same clock: no PLL phase shift needed in sim)
    sdram_new_sdram_controller_0_test_component I_sdram_model (
        .clk     (clk_i),
        .zs_addr (sdram_addr),
        .zs_ba   (sdram_ba),
        .zs_cas_n(sdram_cas_n),
        .zs_cke  (sdram_cke),
        .zs_cs_n (sdram_cs_n),
        .zs_dqm  (sdram_dqm),
        .zs_ras_n(sdram_ras_n),
        .zs_we_n (sdram_we_n),
        .zs_dq   (sdram_dq)
    );

endmodule