

doc="""
Function
--------
FN1		Time Interval
FN2		Trigger Levels
FN3		Frequency
FN4		Period

Gate Time (freq/period)
-----------------------
GT1		Single Period
GT2		0.01 sec
GT3		0.1 sec
GT4		1 sec

Statistics
----------
ST1		Mean
ST2		Stddev (min 100 samples)
ST3		Min
ST4		Max
ST5		Disp Ref
ST6		Clear Ref
ST7		Disply Events
ST8		Set ref
ST9		Disp All

Sample Size
-----------
SS1		1
SS2		100
SS3		1K
SS4		10K
SS5		100K

Mode
----
MD1		Front Panel Display Rate Control, output if addressed
MD2		Display Rate Hold, until "MR" command (NB, see manual)
MD3		Display Rate Fast, Only if addressed
MD4		Display Rate Fast, Only if addressed + SRQ

Input
-----		Start Event		Stop Event
IN1		START			STOP
IN2		STOP			STOP
IN3		START			START
IN4		STOP			START

Slope
-----
SA1		Start postive
SA2		Start negative
SO1		Stop positive
SO2		Stop ppostive
SE1		External Arm postive
SE2		External Arm negative

Arm Select
----------
AR1		+T.I Arming Only
AR2		+/-T.I Arming 

External Holdoff
----------------
EH0		External Holdoff Disable
EH1		External Holdoff Enable (must use EA1 and AR1

External Arm
------------
EA0		External Arm Disable
EA1		External Arm Enable

Internal Arm
------------
		+/-TI Arm mode only
IA1		Internal Arm Auto
IA2		Start Channel Arm
IA3		Stop Channel Arm

MRM		Manual Rate, initiate measurement (typ: with MD2)
		Must come 10msec after last command

MI		Manual Input
SL		Slope Local (Frontpanel operation
SR		Slope Remote
TL		Trigger Local
TR		Trigger Remote
TE	21bytes	Teach, send config 
LN	21bytes	Learn, receive config
PC		Period Compleent
TB0		Ascii Output
TB1		Binary output  (AR2 only, see man)

SB	BE24	Sample Binary

TA	%f	Trigger Start
TO	%f	Trigger Stop

"""
