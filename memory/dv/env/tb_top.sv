`timescale 1ns/1ps
`default_nettype none

// Test bench top: cocotb (the pattern generator) -> sdram_temp (request stage) -> Platform Designer SDRAM system + chip model
module tb_top (
    input  wire        clk_i,
    input  wire        rstn_i,

    // driven by cocotb (patgen side of sdram_temp)
    input  wire [21:0] sdram_addr_i,
    input  wire [3:0]  sdram_byte_en_i,
    input  wire        sdram_rd_en_i,
    input  wire        sdram_wr_en_i,
    input  wire [31:0] sdram_wr_data_i,

    // observed by cocotb
    output wire [31:0] sdram_rd_data_o,
    output wire        sdram_rd_valid_o,
    output wire        sdram_ready_o
);

    // wires between sdram_temp and the SDRAM system (s1 port)
    wire [21:0] dma_addr;
    wire [3:0]  dma_ben_n;
    wire        dma_cs;
    wire [31:0] dma_wr_data;
    wire        dma_rd_n;
    wire        dma_wr_n;
    wire [31:0] dma_rd_data;
    wire        dma_rd_data_valid;
    wire        dma_wait_req;

    sdram_tb_top I_sdram_env (
        .clk_i              (clk_i),
        .rstn_i             (rstn_i),
        .s1_address_i       (dma_addr),
        .s1_byteenable_n_i  (dma_ben_n),
        .s1_chipselect_i    (dma_cs),
        .s1_writedata_i     (dma_wr_data),
        .s1_read_n_i        (dma_rd_n),
        .s1_write_n_i       (dma_wr_n),
        .s1_readdata_o      (dma_rd_data),
        .s1_readdatavalid_o (dma_rd_data_valid),
        .s1_waitrequest_o   (dma_wait_req)
    );

    sdram_req I_dma (
        .clk_i              (clk_i),
        .rstn_i             (rstn_i),
        // from cocotb
        .sdram_addr_i       (sdram_addr_i),
        .sdram_byte_en_i    (sdram_byte_en_i),
        .sdram_rd_en_i      (sdram_rd_en_i),
        .sdram_wr_en_i      (sdram_wr_en_i),
        .sdram_wr_data_i    (sdram_wr_data_i),
        .sdram_rd_data_o    (sdram_rd_data_o),
        .sdram_rd_valid_o   (sdram_rd_valid_o),
        .sdram_ready_o      (sdram_ready_o),
        // to the SDRAM system
        .s1_address_o       (dma_addr),
        .s1_byteenable_n_o  (dma_ben_n),
        .s1_chipselect_o    (dma_cs),
        .s1_read_n_o        (dma_rd_n),
        .s1_write_n_o       (dma_wr_n),
        .s1_writedata_o     (dma_wr_data),
        .s1_readdata_i      (dma_rd_data),
        .s1_readdatavalid_i (dma_rd_data_valid),
        .s1_waitrequest_i   (dma_wait_req)
    );

endmodule : tb_top
`default_nettype wire