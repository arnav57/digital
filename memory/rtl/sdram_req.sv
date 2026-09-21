`timescale 1ns/1ps
`default_nettype none


module sdram_req (
    input wire clk_i,
    input wire rstn_i,

    // DMA TO PATGEN
    input  wire [21:0] sdram_addr_i,
    input  wire [3:0]  sdram_byte_en_i,
    input  wire        sdram_rd_en_i,
    input  wire        sdram_wr_en_i,
    input  wire [31:0] sdram_wr_data_i,
    output wire [31:0] sdram_rd_data_o,
    output wire        sdram_rd_valid_o,

    output wire        sdram_ready_o,

    // DMA TO IP
    output  wire [21:0] s1_address_o,
    output  wire [3:0]  s1_byteenable_n_o,
    output  wire        s1_read_n_o,
    output  wire        s1_write_n_o,
    output  wire [31:0] s1_writedata_o,
    output  wire        s1_chipselect_o,

    input wire [31:0] s1_readdata_i,
    input wire        s1_readdatavalid_i,
    input wire        s1_waitrequest_i
);

logic [21:0] addr_r;
logic  [3:0] ben_r;
logic        wr_en_r;
logic        rd_en_r;
logic [31:0] wr_data_r;
logic [31:0] rd_data_r;

// present requests to the SDRAM
always_ff @( posedge clk_i, negedge rstn_i ) begin
    if (~rstn_i) begin
        addr_r     <= 22'b0;
        ben_r      <= 4'b0;
        wr_en_r    <= 1'b0;
        rd_en_r    <= 1'b0;
        wr_data_r  <= 32'b0;
    end else begin
        // if we dont wait we latch in the next stuff
        if (sdram_ready_o) begin
            addr_r    <= sdram_addr_i;
            ben_r     <= sdram_byte_en_i;
            wr_en_r   <= sdram_wr_en_i;
            rd_en_r   <= sdram_rd_en_i;
            wr_data_r <= sdram_wr_data_i;
        end
    end
end

// latch the read data out, delay the valid by 1 cc to match
logic rd_valid_r;
always_ff @( posedge clk_i, negedge rstn_i ) begin
    if (~rstn_i) begin
        rd_data_r <= 32'b0;
        rd_valid_r <= 1'd0;
    end else begin
        rd_valid_r <= s1_readdatavalid_i;
        if (s1_readdatavalid_i) begin
            rd_data_r <= s1_readdata_i;
        end
    end
end

// post-reset delay
logic [3:0] hold_cnt_r;
logic       hold_cnt_sat;
assign hold_cnt_sat = (hold_cnt_r == 4'd15);

always_ff @( posedge clk_i, negedge rstn_i ) begin
    if (~rstn_i) begin
        hold_cnt_r <= 4'd0;
    end else begin
        hold_cnt_r <= (hold_cnt_sat) ? hold_cnt_r : hold_cnt_r + 4'd1;
    end
end

assign s1_address_o = addr_r;
assign s1_byteenable_n_o = ~ben_r;
assign s1_read_n_o = ~rd_en_r;
assign s1_write_n_o = ~wr_en_r;
assign s1_writedata_o = wr_data_r;
assign s1_chipselect_o = rd_en_r | wr_en_r;
assign sdram_ready_o = ~s1_waitrequest_i & hold_cnt_sat;
assign sdram_rd_valid_o = rd_valid_r;
assign sdram_rd_data_o = rd_data_r;

endmodule : sdram_req