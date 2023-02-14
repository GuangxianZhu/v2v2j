////////////////////////////////////////////////////////////
//////////////////Cell library HDL model////////////////////
//////////////////Target lib: aqfp_hstp033//////////////////
//////////////////Author: Olivia Chen///////////////////////
//////////////////        Christopher Ayala/////////////////
/////////////////////////////////////////////////// /////////

//// logic cells
//// buffer 
module bfr(a, q, xin, xout, din, dout);
    input a;
    output q;
    inout xin, xout, din, dout;
    reg q;
    biasDir_b I0 (xin, xout, din, dout, gatex);

    initial begin
        dout = 1'bz;
    end

    always @(gatex)
    begin
        q = a;
    end
endmodule

module inv(a, q, xin, xout, din, dout);
    input a;
    output q;
    inout xin, xout, din, dout;
    reg q;
    biasDir_b I0 (xin, xout, din, dout, gatex);

    initial begin
        dout = 1'bz;
    end

    always @(gatex)
    begin
        q = ~a;
    end
endmodule

module bfrL(a, q, xin, xout, din, dout);
    input a;
    output q;
    inout xin, xout, din, dout;
    reg q;
    biasDir_b I0 (xin, xout, din, dout, gatex);

    initial begin
        dout = 1'bz;
    end

    always @(gatex)
    begin
        q = a;
    end
endmodule

/// and 
module and_bb(a, b, q, xin, xout, din, dout);
	input a, b;
	output q;
	input din;
	output dout;
	inout xin, xout;
	parameter delay = 0;
	reg q;

	biasDirNS I0 (xin, xout, din, dout, gatex);

	initial begin
		q = 1'bz;
	end
	
	always @(gatex)
	begin
		q = a && b;
	end
endmodule

module and_bi(a, b, q, xin, xout, din, dout);
	input a, b;
	output q;
	input din;
	output dout;
	inout xin, xout;
	parameter delay = 0;
	reg q;

	biasDirNS I0 (xin, xout, din, dout, gatex);

	initial begin
		q = 1'bz;
	end
	
	always @(gatex)
	begin
		q = a && ~b;
	end
endmodule

module and_ib(a, b, q, xin, xout, din, dout);
	input a, b;
	output q;
	input din;
	output dout;
	inout xin, xout;
	parameter delay = 0;
	reg q;

	biasDirNS I0 (xin, xout, din, dout, gatex);

	initial begin
		q = 1'bz;
	end
	
	always @(gatex)
	begin
		q = ~a && b;
	end
endmodule

module and_ii(a, b, q, xin, xout, din, dout);
	input a, b;
	output q;
	input din;
	output dout;
	inout xin, xout;
	parameter delay = 0;
	reg q;

	biasDirNS I0 (xin, xout, din, dout, gatex);

	initial begin
		q = 1'bz;
	end
	
	always @(gatex)
	begin
		q = !a && !b;
	end
endmodule

/// or 
module or_bb(a, b, q, xin, xout, din, dout);
    input a, b;
    output q;
    input din;
    output dout;
    inout xin, xout;
    parameter delay = 0;
    reg q;

    biasDirNS I0 (xin, xout, din, dout, gatex);

    initial begin
    c = 1'bz;
    end

    always @(gatex)
    begin
	    c = a || b;
    end
endmodule

module or_bi(a, b, q, xin, xout, din, dout);
    input a, b;
    output q;
    input din;
    output dout;
    inout xin, xout;
    parameter delay = 0;
    reg q;

    biasDirNS I0 (xin, xout, din, dout, gatex);

    initial begin
        q = 1'bz;
    end

    always @(gatex)
    begin
	    q = a || ~b;
    end
endmodule

module or_ib(a, b, q, xin, xout, din, dout);
    input a, b;
    output q;
    input din;
    output dout;
    inout xin, xout;
    parameter delay = 0;
    reg q;

    biasDirNS I0 (xin, xout, din, dout, gatex);

    initial begin
    q = 1'bz;
    end

    always @(gatex)
    begin
	    q = ~a || b;
    end
endmodule

module or_ii(a, b, q, xin, xout, din, dout);
    input a, b;
    output q;
    input din;
    output dout;
    inout xin, xout;
    parameter delay = 0;
    reg q;

    biasDirNS I0 (xin, xout, din, dout, gatex);

    initial begin
    q = 1'bz;
    end

    always @(gatex)
    begin
	    q = ~a || ~b;
    end
endmodule

/// majority
module maj_bbb(a, b, c, q, xin, xout, din, dout);
    input a, b, c;
    output q;
    inout xin, xout, din, dout;
    parameter delay = 0;
    reg q;

    biasDir_b I0 (xin, xout, din, dout, gatex);

    initial begin
        q = 1'bz;
    end

    always @(gatex)
    begin
	    q = (a&b)|(a&c)|(b&c);
    end

endmodule

module maj_bbi(a, b, c, q, xin, xout, din, dout);
    input a, b, c;
    output q;
    inout xin, xout, din, dout;
    parameter delay = 0;
    reg q;

    biasDir_b I0 (xin, xout, din, dout, gatex);

    initial begin
        q = 1'bz;
    end

    always @(gatex)
    begin
	    q = (a&b)|(a&~c)|(b&~c);
    end

endmodule

module maj_ibb(a, b, c, q, xin, xout, din, dout);
    input a, b, c;
    output q;
    inout xin, xout, din, dout;
    parameter delay = 0;
    reg q;

    biasDir_b I0 (xin, xout, din, dout, gatex);

    initial begin
        q = 1'bz;
    end

    always @(gatex)
    begin
	    q = (~a&b)|(~a&c)|(b&c);
    end

endmodule

module maj_bib(a, b, c, q, xin, xout, din, dout);
    input a, b, c;
    output q;
    inout xin, xout, din, dout;
    parameter delay = 0;
    reg q;

    biasDir_b I0 (xin, xout, din, dout, gatex);

    initial begin
        q = 1'bz;
    end

    always @(gatex)
    begin
	    q = (a&~b)|(a&c)|(~b&c);
    end

endmodule

module maj_bii(a, b, c, q, xin, xout, din, dout);
    input a, b, c;
    output q;
    inout xin, xout, din, dout;
    parameter delay = 0;
    reg q;

    biasDir_b I0 (xin, xout, din, dout, gatex);

    initial begin
        q = 1'bz;
    end

    always @(gatex)
    begin
	    q = (a&~b)|(a&~c)|(~b&~c);
    end

endmodule

module maj_iib(a, b, c, q, xin, xout, din, dout);
    input a, b, c;
    output q;
    inout xin, xout, din, dout;
    parameter delay = 0;
    reg q;

    biasDir_b I0 (xin, xout, din, dout, gatex);

    initial begin
        q = 1'bz;
    end

    always @(gatex)
    begin
	    q = (~a&~b)|(~a&c)|(~b&c);
    end

endmodule

module maj_ibi(a, b, c, q, xin, xout, din, dout);
    input a, b, c;
    output q;
    inout xin, xout, din, dout;
    parameter delay = 0;
    reg q;

    biasDir_b I0 (xin, xout, din, dout, gatex);

    initial begin
        q = 1'bz;
    end

    always @(gatex)
    begin
	    q = (~a&b)|(~a&~c)|(b&~c);
    end

endmodule

module maj_iii(a, b, c, q, xin, xout, din, dout);
    input a, b, c;
    output q;
    inout xin, xout, din, dout;
    parameter delay = 0;
    reg q;

    biasDir_b I0 (xin, xout, din, dout, gatex);

    initial begin
        q = 1'bz;
    end

    always @(gatex)
    begin
	    q = (~a&~b)|(~a&~c)|(~b&~c);
    end

endmodule

///splitter
module spl2(a, x, y, xin, xout, din, dout);
    input a;
    output x, y;
    inout xin, xout, din, dout;
    reg x,y;
    biasDir_b I0 (xin, xout, din, dout, gatex);

    initial begin
        x = 1'bz;
        y = 1'bz;
    end

    always @(gatex)
    begin
	    x = a;
        y = a;
    end

endmodule

module spl3(a, x, y, z, xin, xout, din, dout);
    input a;
    output x, y, z;
    inout xin, xout, din, dout;
    reg x, y, z;
    biasDir_b I0 (xin, xout, din, dout, gatex);
    initial begin
        x = 1'bz;
        y = 1'bz;
        z = 1'bz;
    end

    always @(gatex)
    begin
	    x = a;
        y = a;
        z = a;
    end

endmodule

module spl3L(a, x, y, z, xin, xout, din, dout);
    input a;
    output x, y, z;
    inout xin, xout, din, dout;
    reg x, y, z;
    biasDir_b I0 (xin, xout, din, dout, gatex);
    initial begin
        x = 1'bz;
        y = 1'bz;
        z = 1'bz;
    end

    always @(gatex)
    begin
	    x = a;
        y = a;
        z = a;
    end

endmodule

module spl4L(a, w, x, y, z, xin, xout, din, dout);
    input a;
    output w, x, y, z;
    inout xin, xout, din, dout;
    reg w, x, y, z;
    biasDir_b I0 (xin, xout, din, dout, gatex);
    initial begin
        w = 1'bz;
        x = 1'bz;
        y = 1'bz;
        z = 1'bz;
    end

    always @(gatex)
    begin
	    w = a;
        x = a;
        y = a;
        z = a;
    end

endmodule


/// bias wiring cells

/// bi-directional enabler 
///determines direction of excitation bias and creates normalized gate
module biasDir_b(xin, xout, dcin, dcout, gatex);

  parameter propagationDelay = 0.198;

  inout xin, xout;
  inout dcin, dcout;
  output gatex;
  reg xiFrst, xoFrst, dciFrst, dcoFrst, xiReg, xoReg, dciReg, dcoReg;
  reg fndDirx, fndDirdc, gatex, sameDir, clock;

  initial
    begin
	xiFrst = 1'b0;
	xoFrst = 1'b0;
    dciFrst = 1'b0;
    dcoFrst = 1'b0;
	xiReg  = 1'b0;
	xoReg  = 1'b0;
    dciReg = 1'b0;
    dcoReg = 1'b0;
	fndDirx = 1'b0;
    fndDirdc = 1'b0;
	gatex  = 1'b0;
    sameDir = 1'b0;
    clock = 1'b0;
    end

  always@(xin or xout or dcin or dcout)
  begin
    if((xin==1'b1 || xin==1'b0) && !fndDirx)
    begin
      xiFrst = 1'b1;
      fndDirx = 1'b1;
    end

    if((xout==1'b1 || xout==1'b0) && !fndDirx)
    begin
      xoFrst = 1'b1;
      fndDirx = 1'b1;
    end

    if((dcin==1'b1) && !fndDirdc)
    begin
      dciFrst = 1'b1;
      fndDirdc = 1'b1;
    end

    if((dcout==1'b1) && !fndDirdc)
    begin
      dcoFrst = 1'b1;
      fndDirdc = 1'b1;
    end

    xiReg <= #propagationDelay xin;
    xoReg <= #propagationDelay xout;
    dciReg <= dcin;
    dcoReg <= dcout;
    clock <= xiFrst ? xin : xout;
    sameDir <= dciFrst ^ xiFrst;
    gatex <= sameDir? !clock: clock;
  end

  assign xin  = xoFrst ? xoReg : 1'bz;
  assign xout = xiFrst ? xiReg : 1'bz;
  assign dcin = dcoFrst ? dcoReg : 1'bz;
  assign dcout = dciFrst ? dciReg : 1'bz;

endmodule

module biasDirNS_b(xin, xout, dcin, dcout, gatex);
    parameter propagationDelay = 0.198;

    input dcin;
    inout xin, xout;
    output gatex, dcout;
    reg xiFrst, xoFrst, xiReg, xoReg;
    reg fndDirx, gatex, sameDir, clock;

    initial
    begin
        xiFrst = 1'b0;
        xoFrst = 1'b0;
        xiReg = 1'b0;
        xoReg = 1'b0;
        fndDirx = 1'b0;
	    gatex  = 1'b0;
        sameDir = 1'b0;
        clock = 1'b0;
    end

    always@(xin or dcin or xout)
    begin
        if((xin==1'b1 || xin == 1'b0) && !fndDirx)
            begin
                xiFrst = 1'b1;
                fndDirx = 1'b1;
            end

        if((xout==1'b1|| xout == 1'b0) && !fndDirx)
            begin
                xoFrst = 1'b1;
                fndDirx = 1'b1;
            end
        xiReg <= xin;
        xoReg <= xout;
        clock <= xiFrst? xin : xout;
        sameDir <= xiFrst;
        gatex <= sameDir? clock : !clock;
    end

    assign dcout = dcin;
    assign xin = xoFrst ? xoReg : 1'bz;
    assign xout = xiFrst ? xiReg : 1'bz;

endmodule

module biasDirNS(xin, xout, dcin, dcout, gatex);

    parameter propagationDelay = 0.594;

    input dcin;
    inout xin, xout;
    output gatex, dcout;
    reg xiFrst, xoFrst, xiReg, xoReg;
    reg fndDirx, gatex, sameDir, clock;

    initial
    begin
        xiFrst = 1'b0;
        xoFrst = 1'b0;
        xiReg = 1'b0;
        xoReg = 1'b0;
        fndDirx = 1'b0;
	    gatex  = 1'b0;
        sameDir = 1'b0;
        clock = 1'b0;
    end

    always@(xin or dcin or xout)
    begin
        if((xin==1'b1 || xin == 1'b0) && !fndDirx)
            begin
                xiFrst = 1'b1;
                fndDirx = 1'b1;
            end

        if((xout==1'b1|| xout == 1'b0) && !fndDirx)
            begin
                xoFrst = 1'b1;
                fndDirx = 1'b1;
            end

        xiReg <= xin;
        xoReg <= xout;
        clock <= xiFrst? xin : xout;
        sameDir <= xiFrst;
        gatex <= sameDir? clock : !clock;
    end

    assign dcout = dcin;
    assign xin = xoFrst ? xoReg : 1'bz;
    assign xout = xiFrst ? xiReg : 1'bz;

endmodule

///basic bias cell module
module bias(a, b);

    parameter propagationDelay = 0.198; /// 1/3 of light velocity
    parameter length = 1;
    inout a, b;
    reg aFrst, bFrst, aReg, bReg, fndDir;

    initial
    begin
        aFrst = 1'b0;
        bFrst = 1'b0;
        aReg  = 1'b0;
        bReg  = 1'b0;
        fndDir = 1'b0;
    end

    always@(a or b)
    begin
        if((a==1'b1 || a==1'b0) && !fndDir)
        begin
            aFrst = 1'b1;
            fndDir = 1'b1;
        end

        if((b==1'b1 || b==1'b0) && !fndDir)
        begin
            bFrst = 1'b1;
            fndDir = 1'b1;
        end
        aReg <= #(propagationDelay*length) a;
        bReg <= #(propagationDelay*length) b;
    end

    assign a  = bFrst ? bReg : 1'bz;
    assign b  = aFrst ? aReg : 1'bz;

endmodule

/// bias wiring cells
module bias_ac_5um(a, b);
    inout a,b;
    bias #(1) bias_ac_5um_0 (a,b);
endmodule

module bias_ac_10um(a, b);
    inout a,b;
    bias #(2) bias_ac_5um_0 (a,b);
endmodule

module bias_ac_20um(a, b);
    inout a,b;
    bias #(4) bias_ac_5um_0 (a,b);
endmodule

module bias_ac_50um(a, b);
    inout a,b;
    bias #(10) bias_ac_5um_0 (a,b);
endmodule

module bias_ac_100um(a, b);
    inout a,b;
    bias #(20) bias_ac_5um_0 (a,b);
endmodule

module bias_ac_corner(a, b);
  inout a,b;
  bias_ac_10um w (a,b);
endmodule

module bias_ac_cross(a, b, c, d);
  inout a,b,c,d;
  bias_ac_10um w1 (a,b);
  bias_ac_10um w2 (c,d);
endmodule

module bias_ac_gnd(a);
    input a;
endmodule

module bias_dc_5um(a, b);
    inout a,b;
    bias #(1) bias_ac_5um_0 (a,b);
endmodule

module bias_dc_10um(a, b);
    inout a,b;
    bias #(2) bias_ac_5um_0 (a,b);
endmodule

module bias_dc_20um(a, b);
    inout a,b;
    bias #(4) bias_ac_5um_0 (a,b);
endmodule

module bias_dc_50um(a, b);
    inout a,b;
    bias #(10) bias_ac_5um_0 (a,b);
endmodule

module bias_dc_100um(a, b);
    inout a,b;
    bias #(20) bias_ac_5um_0 (a,b);
endmodule

module bias_pair_5um(a, b, c, d);

  inout a,b,c,d;
  bias_ac_5um w1 (a,b);
  bias_dc_5um w2 (c,d);

endmodule

module bias_pair_10um(a, b, c, d);

  inout a,b,c,d;
  bias_ac_10um w1 (a,b);
  bias_dc_10um w2 (c,d);

endmodule

module bias_pair_20um(a, b, c, d);

  inout a,b,c,d;
  bias_ac_20um w1 (a,b);
  bias_dc_20um w2 (c,d);

endmodule

module bias_pair_50um(a, b, c, d);

  inout a,b,c,d;
  bias_ac_50um w1 (a,b);
  bias_dc_50um w2 (c,d);

endmodule

module bias_pair_100um(a, b, c, d);

  inout a,b,c,d;
  bias_ac_100um w1 (a,b);
  bias_dc_100um w2 (c,d);

endmodule

module bias_pair_corner(a, b, c, d);

  inout a,b,c,d;
  bias_ac_5um w1 (a,b);
  bias_dc_5um w2 (c,d);

endmodule

module bias_pair_corner2(a, b, c, d);

  inout a,b,c,d;
  bias_ac_5um w1 (a,b);
  bias_dc_5um w2 (c,d);

endmodule

module bias_separate1(a, b, c, d);

 inout a,b,c,d;
 bias_ac_10um w1 (a, b);
 bias_dc_10um w2 (c, d);

endmodule

module bias_separate2(a, b, c, d);

 inout a,b,c,d;
 bias_ac_10um w1 (a, b);
 bias_dc_10um w2 (c, d);

endmodule

/// signal wiring cell module 
module signalwire(a, b);

    real propagationDelay = 0;
    parameter length = 1;
    inout a, b;
    reg aFrst, bFrst, aReg, bReg, fndDir;

    initial
    begin
        aFrst = 1'b0;
        bFrst = 1'b0;
        aReg  = 1'b0;
        bReg  = 1'b0;
        fndDir = 1'b0;
    end

    always@(a or b)
    begin
        if((a==1'b1 || a==1'b0) && !fndDir)
        begin
            aFrst = 1'b1;
            fndDir = 1'b1;
    end

        if((b==1'b1 || b==1'b0) && !fndDir)
        begin
            bFrst = 1'b1;
            fndDir = 1'b1;
    end
    aReg <= #(propagationDelay*length) a;
    bReg <= #(propagationDelay*length) b;
    end

    assign a  = bFrst ? bReg : 1'bz;
    assign b  = aFrst ? aReg : 1'bz;

endmodule

/// wiring cells 
module wire_5um(a, b);
    inout a,b;
    signalwire #(1) wire_5um_0 (a,b);
endmodule

module wire_10um(a, b);
    inout a,b;
    signalwire #(2) wire_5um_0 (a,b);
endmodule

module wire_20um(a, b);
    inout a,b;
    signalwire #(4) wire_5um_0 (a,b);
endmodule

module wire_50um(a, b);
    inout a,b;
    signalwire #(10) wire_5um_0 (a,b);
endmodule

module wire_100um(a, b);
    inout a,b;
    signalwire #(20) wire_5um_0 (a,b);
endmodule

module wire_corner(a, b);
    inout a,b;
    wire_10um w (a,b);
endmodule

module wire_cross(a, b, c, d);
    inout a,b,c,d;
    wire_10um w1 (a,b);
    wire_10um w2 (c,d);
endmodule

module wire_diagonal(a, b);
    inout a,b;
    wire_10um w (a,b);
endmodule