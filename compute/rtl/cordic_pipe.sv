// N stage pipelined CORDIC implementation.

`timescale 1ns/1ps
`default_nettype none

module cordic_pipe #(
    parameter int NUM_STAGES      = 13,  // What stage in the pipeline is this current unit?
    parameter int BAR_ANGLE_WIDTH = 16, // Width of the BAR table input
    parameter int VECTOR_WIDTH    = 18  // 16 bits data + 2 gain bits for CORDIC gain (~1.64)
)(
    input wire clk_i,
    input wire rstn_i,

    // inputs to CORDIC algorithm (Q3.15)
    input wire signed [VECTOR_WIDTH-1:0]    x_i,
    input wire signed [VECTOR_WIDTH-1:0]    y_i,
    input wire signed [BAR_ANGLE_WIDTH-1:0] z_i,

    // outputs from last CORDIC (Q3.15)
    output wire signed [VECTOR_WIDTH-1:0]    x_o,
    output wire signed [VECTOR_WIDTH-1:0]    y_o,
    output wire signed [BAR_ANGLE_WIDTH-1:0] z_o,
);

// abutments
logic signed [NUM_STAGES:0][VECTOR_WIDTH-1:0]    x_mesh;
logic signed [NUM_STAGES:0][VECTOR_WIDTH-1:0]    y_mesh;
logic signed [NUM_STAGES:0][BAR_ANGLE_WIDTH-1:0] z_mesh;

// instantiate the chain of CORDIC stages
genvar i;
generate for (i = 0; i < NUM_STAGES ; i++ ) begin : gen_cordic_pipe
    cordic_stage #(
        .STAGE_INDEX     (i              ),
        .BAR_ANGLE_WIDTH (BAR_ANGLE_WIDTH),
        .VECTOR_WIDTH    (VECTOR_WIDTH   )
    ) I_cordic_stage (
        // required
        .clk_i (clk_i),
        .rstn_i (rstn_i),
        .theta_i ( arctan_angles[i] )
        // inputs
        .x_i ( x_mesh[i] )
        .y_i ( y_mesh[i] )
        .z_i ( z_mesh[i] )
        // outputs
        .x_o ( x_mesh[i+1] )
        .y_o ( y_mesh[i+1] )
        .z_o ( z_mesh[i+1] )
    );
end

assign x_mesh[0] = x_i;
assign y_mesh[0] = y_i;
assign z_mesh[0] = z_i;

assign x_o = x_mesh[NUM_STAGES];
assign y_o = y_mesh[NUM_STAGES];
assign z_o = z_mesh[NUM_STAGES];

endmodule : cordic_pipe

`default_nettype wire