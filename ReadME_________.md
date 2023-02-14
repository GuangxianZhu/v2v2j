input dir
1_Vlib/: verilog library
2_Vnetlist/: the input netlist
3_Jlib/: Josim library
./config.txt: using this to write driver

output dir
./xxx.inp: the output josim inp file
./Vcontent.v: the output verilog file, for debug
json/: parse libs and netlist, then output the json
./globg.gv: using this to draw figure
./globg.gv.pdf: the figure

*********************************************
Verilog to Josim converter (by Python).
version 1.2
*********************************************
using py packages:

graphviz (draw figure)
networkx (analysis cell's level)
tqdm (data process)

*********************************************
Must follow these rules:

1. make sure the name of component_pin are same with Lib_verilog and Lib_josim.
    I have checked the name, to make sure pin_name correct.
    for example:
    .a(), .b(), .q()  OK
    .a(), .b(), .c()  Error, pin_name not matched

*** if someone change libary, user must check pin_name.
*** recommand to write pins using same order with verilog library (same pin order and pin name).

2. make sure add '.print' and '.tran' command before using josim server. Such as:

.tran 0.2ps 1500ps 0ps
.print devi 
.print devi Lip.XI3.Xand_03				

3. The global output shouldn't flow to next component's pin_in. such as:

    output cout;

    and_bb and_05 (.q(cout), ... ) // ok
    and_bb and_06 (.a(cout), ... ) < error

4. Please write driver in config.txt, but if you want to change param of:
    xin1, xin2, din,
    please find them in code. 
*** They are defined in code because user usually don't need to modify them.

*********************************************

NOW YOU CAN DOUBLE CLICK RUNNNNNNN.bat !

