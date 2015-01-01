// File: m_fdct_read_proc_sm_monitor.v
// Generated by MyHDL 0.9dev
// Date: Fri Dec 26 22:11:20 2014


`timescale 1ns/10ps

module m_fdct_read_proc_sm_monitor (
    clock,
    reset,
    sof,
    start_int,
    x_pixel_cnt,
    y_line_cnt,
    img_size_x,
    img_size_y,
    cmp_idx,
    cur_cmp_idx,
    rd_started,
    bf_fifo_hf_full,
    fram1_rd,
    fram1_raddr,
    fram1_ln_cnt,
    fram1_px_cnt,
    fram1_we,
    fram1_waddr,
    midv,
    modv,
    zz_rd,
    zz_raddr
);
// This monitors the signals from the FDCT and tries to indentifiy
// a state that should correspond to the 

input clock;
input reset;
input sof;
input start_int;
input [15:0] x_pixel_cnt;
input [15:0] y_line_cnt;
input [15:0] img_size_x;
input [15:0] img_size_y;
input [2:0] cmp_idx;
input [2:0] cur_cmp_idx;
input rd_started;
input bf_fifo_hf_full;
input fram1_rd;
input [6:0] fram1_raddr;
input [2:0] fram1_ln_cnt;
input [2:0] fram1_px_cnt;
input fram1_we;
input [6:0] fram1_waddr;
input midv;
input modv;
input zz_rd;
input [5:0] zz_raddr;

reg [31:0] mi_ccnt;
reg [31:0] mo_rcnt;
reg [31:0] ircnt;
reg [31:0] orcnt;
reg [1:0] state;
reg [31:0] iccnt;
reg [31:0] mi_pcnt;
reg [31:0] opcnt;
reg [31:0] ipcnt;
reg [31:0] mo_pcnt;
reg [31:0] occnt;
reg [31:0] mo_ccnt;
reg [31:0] mi_rcnt;

reg [31:0] rcnt [0:128-1];
reg [31:0] wcnt [0:128-1];




always @(posedge clock, posedge reset) begin: M_FDCT_READ_PROC_SM_MONITOR_MON
    if (reset == 1) begin
        state <= 2'b00;
    end
    else begin
        case (state)
            2'b00: begin
                if ((sof || start_int)) begin
                    // pass
                end
                state <= 2'b00;
            end
            2'b01: begin
                state <= 2'b00;
            end
            2'b10: begin
                state <= 2'b00;
            end
            default: begin
                $write("invalid state ");
                $write("%0d", state);
                $write("\n");
                state <= 2'b00;
            end
        endcase
    end
end


always @(posedge clock) begin: M_FDCT_READ_PROC_SM_MONITOR_MONMEM
    integer ii;
    if (fram1_rd) begin
        rcnt[fram1_raddr] <= (rcnt[fram1_raddr] + 1);
    end
    if (fram1_we) begin
        wcnt[fram1_waddr] <= (wcnt[fram1_waddr] + 1);
    end
    for (ii=0; ii<128; ii=ii+1) begin
        if ((!(rcnt[ii] >= (wcnt[ii] + 4)))) begin
            $write("%0d", ii);
            $write(": rcnt ");
            $write("%0d", rcnt[ii]);
            $write(", wcnt ");
            $write("%0d", wcnt[ii]);
            $write("\n");
        end
    end
end


always @(posedge clock, posedge reset) begin: M_FDCT_READ_PROC_SM_MONITOR_MONCNT
    if (reset == 1) begin
        ircnt <= 0;
        opcnt <= 0;
        ipcnt <= 0;
        orcnt <= 0;
        occnt <= 0;
        mo_pcnt <= 0;
        mi_ccnt <= 0;
        mo_ccnt <= 0;
        mi_rcnt <= 0;
        mo_rcnt <= 0;
        iccnt <= 0;
        mi_pcnt <= 0;
    end
    else begin
        if (fram1_we) begin
            ipcnt <= (ipcnt + 1);
            if (($signed({1'b0, iccnt}) < ($signed({1'b0, img_size_x}) - 1))) begin
                iccnt <= (iccnt + 1);
            end
            else begin
                iccnt <= 0;
                if (($signed({1'b0, ircnt}) < ($signed({1'b0, img_size_y}) - 1))) begin
                    ircnt <= (ircnt + 1);
                end
                else begin
                    ircnt <= 0;
                end
            end

            if ((((ircnt + 1) == 80) && ((iccnt + 1) == 80))) begin
                $write("II: ");
                $write("%0d", (ipcnt + 1));
                $write(", ");
                $write("%0d", (ircnt + 1));
                $write("x");
                $write("%0d", (iccnt + 1));
                $write("\n");
            end

            if ((((ircnt + 1) == img_size_y) && ((iccnt + 1) == img_size_x))) begin
                $write("II: ");
                $write("%0d", (ipcnt + 1));
                $write(", ");
                $write("%0d", (ircnt + 1));
                $write("x");
                $write("%0d", (iccnt + 1));
                $write("\n");
            end
        end
        if (zz_rd) begin
            opcnt <= (opcnt + 1);
            if (($signed({1'b0, occnt}) < ((4 * img_size_x) - 1))) begin
                occnt <= (occnt + 1);
            end
            else begin
                occnt <= 0;
                if (($signed({1'b0, orcnt}) < ($signed({1'b0, img_size_y}) - 1))) begin
                    orcnt <= (orcnt + 1);
                end
                else begin
                    orcnt <= 0;
                end
            end
            if ((((orcnt + 1) == 40) && ((occnt + 1) == (40 * 4)))) begin
                $write("OO: ");
                $write("%0d", (opcnt + 1));
                $write(", ");
                $write("%0d", (orcnt + 1));
                $write("x");
                $write("%0d", (occnt + 1));
                $write("\n");
            end
        end
        if (midv) begin
            mi_pcnt <= (mi_pcnt + 1);
            if (($signed({1'b0, mi_ccnt}) < ((4 * img_size_x) - 1))) begin
                mi_ccnt <= (mi_ccnt + 1);
            end
            else begin
                mi_ccnt <= 0;
                if (($signed({1'b0, mi_rcnt}) < ($signed({1'b0, img_size_y}) - 1))) begin
                    mi_rcnt <= (mi_rcnt + 1);
                end
                else begin
                    mi_rcnt <= 0;
                end
            end
        end
        if (modv) begin
            mo_pcnt <= (mo_pcnt + 1);
            if (($signed({1'b0, mo_ccnt}) < ((4 * img_size_x) - 1))) begin
                mo_ccnt <= (mo_ccnt + 1);
            end
            else begin
                mo_ccnt <= 0;
                if (($signed({1'b0, mo_rcnt}) < ($signed({1'b0, img_size_y}) - 1))) begin
                    mo_rcnt <= (mo_rcnt + 1);
                end
                else begin
                    mo_rcnt <= 0;
                end
            end
        end
    end
end

endmodule
