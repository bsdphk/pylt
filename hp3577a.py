#!/usr/local/bin/python

import sys
import time
import prologix_usb
import subprocess

class hp3577a(prologix_usb.gpib_dev):

	def __init__(self, name = "gpib1", adr = 12):
		prologix_usb.gpib_dev.__init__(self, name, adr)
		x = self.ask("ID?")
		y = x.split(",")
		if y[0] != "HP3577A":
			self.fail("HP3577A ID failure (%s)" % x)
		self.id = y[0]
		self.errors()
		self.AOK()

	#######################
	# PYLT Standard methods
	#######################

	def errors(self, f=sys.stderr):
		r = False
		while True:
			x = self.ask("DMS").split(",")
			if int(x[0]) & 0x20 == 0:
				break
			f.write(self.id + ".ERROR: " +  x[3] + "\n")
			r = True
		return r

	def screen_dump(self, fname="_.hp3577a.eps", format="eps"):
		print(self.id + " Taking a " + format +
		    " screendump into " + fname)
		self.AOK()
		self.wr("T1P 2;T2P 3;PGP 4;PLA")
		while True:
			x = self.rd()
			if x[-5:] == ";SP0;":
				break
		p = subprocess.Popen([
			"hp2xx",
			"-m", format,
			"-f", fname,
			"-a2.0",
			"-w180",
			"-o5",
			"-O5",
			"-c12415671",
			"-p24421111",
			"-"
			], stdin=subprocess.PIPE)
		p.stdin.write(x[4:])
		p.stdin.close()
		p.wait()

if __name__ == "__main__":
	d = hp3577a()
	print("Device reponds (%s)" % d.ask("ID?"))
	d.errors()
	d.wr("IPR")
	time.sleep(3)
	d.screen_dump()


doc="""
### From Appendix D
## Display Format
TR1	Trace 1
TR2	Trace 2
DSF	Display Function*
DF7	Log magnitude
DF6	Lin Magnitude
DF5	Phase
DF4	Polar
DF3	Real
DF2	Imag
DF1	Delay
DF0	Trace Off
DAP	Delay Aperture Menu*
AP1	Aperture .5% of span
AP2	Aperture 1% of span
AP3	Aperture 2% of span
AP4	Aperture 4% of span
AP5	Aperture 8% of span
AP6	Aperture 16% of span
RET	Return*
INP	Input*
INR	Input = R
INA	Input = A
INB	Input = B
IAR	Input = A/R
IBR	Input = B/R
ID1	Input = D1
ID2	Input = D2
ID3	Input = D3
ID4	Input = D4
I11	Input = S11
I21	Input = S21
I12	Input = S12
I22	Input = S22
CPI	Copy Input
TSF	Test Set Forward
TSR	Test Set Reverse
SCL	Scale*
ASL	Autoscale
REF	Ref lvl (entry)
DIV	Scale/div (entry)
RPS	Ref Pos (entry)
RL0	Ref line off
RL1	Ref line on
CPS	Copy Scale
PSL	Phase slope (entry)
PS0	Phase slope off
PS1	Phase slope on
PFS	Polar Full Scale (entry)
PPR	Polar Phase Ref (entry)
GT0	Smith Chart off
GT1	Smith Chart on
MKR	Marker*
MKP	Marker Position (entry)
MR0	Marker off
MR1	Marker on
ZMK	Zero Marker
MO0	Marker offset off
MO1	Marker offset on
MKO	Marker offset (entry)
MOF	Marker offset freq (entry)
MOA	Marker offset amp (entry)
CO0	Coupling off
CO1	Coupling on
PMO	Polar Mag offset (entry)
PPO	Polar Phase offset (entry)
PRO	Polar Real offset (entry)
PIO	Polar Imag offset (entry)
MRI	Polar Marker Units (Re/Im)
MMP	Polar Marker Units (Mg/Ph)
MKG	Marker*
MTR	MKR->Ref Lev
MTA	MKR->Start Freq
MTB	MKR->Stop Freq
MTC	MKR->Center Freq
MOS	MKR Offset -> span
MTX	MKR->Max
MTN	MKR->Min
MSM	Marker Seach Menu
MTV	MRK Target Value (entry)
MRT	MKR -> Right for Target
MLT	MKR -> Left for Target
MTP	MKR -> Full Scale
MPF	MKR -> Polar Phase Ref
STO	Store Data *
SD1	Store in reg D1
SD2	Store in reg D2
SD3	Store in reg D3
SD4	Store in reg D4
STD	Store and Display
UDS	User defined store
TD1	Store to D1
TD2	Store to D2
TD3	Store to D3
TD4	Store to D4
CAL	Measurement Calibration*
NRM	Normalize
NRS	Normalize (short)
CPR	Calibrate, Partial
CFL	Calibrate, Full
CGO	Continue Calibration
DFN	Define Math*
KR1	Const. K1 Real (entry)
KI1	Const. K1 Imag (entry)
KR2	Const. K2 Real (entry)
KI2	Const. K2 Imag (entry)
KR3	Const. K3 Real (entry)
KI3	Const. K3 Imag (entry)
KR4	Const. K4 Real (entry)
KI4	Const. K4 Imag (entry)
DFC	Define Function *
UF1	Function F1
UF2	Function F2
UF3	Function F3
UF4	Function F4
UF5	Function F5
R	Math term for input R
A	Math term for input A
B	Math term for input B
D	Math term for storage reg
K	Math term for constant
F	Math term for function
(	Math bracket
+	Math function +
-	Math function -
*	Math function *
/	Math function /
)	Math bracket
# Data Entry Section Commands
IUP	Increment (up arrow)
IDN	Decrement (down arrow)
CE0	Continuous Entry (knob) off
CE1	Continuous Entry (knob) on
HLD	Entry off
# Display Format Suffix Units
DBM	dBm
DBV	dBV (rms)
DBR	dB relative
V	Volt (rms)
MV	milli-Volt (rms)
UV	micro-Volt (rms)
NV	nano-Volt (rms)
DEG	Degrees
RAD	Radians
RSP	Radians/Span
SEC	Seconds
MSC	milli-seconds
USC	micro-seconds
NSC	nano-seconds
%	Percent
DSP	Degrees/Span
RAP	Radians/Span
MHZ	MHz
KHZ	kHz
HZ	Hz
E	Exponent
## Source
# SWEEP TYPE
STY	Sweep Type*
ST1	Lin Sweep
ST2	Alt Sweep
ST3	Log Sweep
ST4	Amp Sweep
ST5	CW
SUP	Sweep direction up
SDN	Sweep direction down
SMD	Sweep Mode *
SM1	Continuous sweep
SM2	Single Sweep
SM3	Manual Sweep
MFR	Manual Freqency (entry)
MAM	Manual Amplitude (entry)
MTM	Marker -> Manual
STM	Sweep Time*
SWT	Sweep time (entry)
SMT	Step time (entry)
MSR	Sample time (entry)
FRQ	Frequency*
SFR	Src Freq (entry)
FRA	Start Freq (entry)
FRB	Stop Freq (entry)
FRC	Center Frequency (entry)
FRS	Frequency Span (entry)
CFS	FRC Step Size (entry)
SRL	Sweep Resolution menu*
RS1	Freq Sep Res 51/span
RS2	Freq Sep Res 101/span
RS3	Freq Sep Res 201/span
RS4	Freq Sep Res 401/span
FSW	Full Sweep
FST	Freq Step Size (entry)
AMP	Amplitude*
SAM	Source Amplitude (entry)
AST	Amp Step Size (entry)
CTS	Clear Trip, Source
AMA	Start Amplitude (entry)
AMB	Stop Amplitude (entry)
NST	Steps/Sweep menu *
NS1	Number of steps = 6
NS2	Number of steps = 11
NS3	Number of steps = 21
NS4	Number of steps = 51
NS5	Number of steps = 101
NS6	Number of steps = 201
NS7	Number of steps = 401
TRM	Trigger Mode*
TG1	Free Run
TG2	Line Trigger
TG3	External Trigger
TG4	Immediate
TRG	Sweep Trigger (?)
RST	Sweep Reset (?)
(units is a repeat)
## RECEIVER
RBW	Resolution BW*
RW1	Res. BW 1Hz
RW2	Res. BW 10Hz
RW3	Res. BW 100Hz
RW4	Res. BW 1kHz
AU0	Auto bw off
AU1	Auto bw on
AVE	Average*
AV0	Averaging off
AV1	AVG n=4
AV2	AVG n=8
AV3	AVG n=16
AV4	AVG n=32
AV5	AVG n=64
AV6	AVG n=128
AV7	AVG n=256
ATT	Attenuator *
AR1	Atten R 0dB
AR2	Atten R 20dB
AA1	Atten A 0dB
AA2	Atten A 20dB
AB1	Atten B 0dB
AB2	Atten B 20dB
IR1	Imp R 50Ohm
IR2	Imp R 1MOhm
IA1	Imp A 50Ohm
IA2	Imp A 1MOhm
IB1	Imp B 50Ohm
IB2	Imp B 1MOhm
CTR	Clear Trip Receiver
LEN	Length
LNR	Len R (entry)
LR0	Len R off
LR1	Len R on
LNA	Len A (entry)
LA0	Len A off
LA1	Len A on
LNB	Len B (entry)
LB0	Len B off
LB1	Len B on
LNS	Length Step (entry)
# RECEIVER SUFF UNIT
MET	meters
CM	Centimeters
(repeat)
## INSTRUMENT STATE
SPC	Special Funcitons*
SLF	Confid. Test Menu
STR	Self Test Chan R
STA	Self Test Chan A
STB	Self Test Chan B
BP0	Beeper off
BP1	Beeper on
SDG	Service Diag Menu
SL0	Source Level off
SL1	Source Level on
SE0	Settling time off
SE1	Settling time on
SY0	Synth Diag off
SY1	Synth Diag on
DTP 	Display Test Pattern
TMT	Trace Memory Test
FPT	Fast Processor Test
PRT	I/O Port Test
MOR	More Serv. Diag Menu*
DST	Display Memory Test
SRV	Software Revision Message
SP0	S-Params off
SP1	S-Params on
SAV	Save Instrument State*
SV1	Save in reg 1
SV2	Save in reg 2
SV3	Save in reg 3
SV4	Save in reg 4
SV5	Save in reg 5
RCL	Recall Instrument State*
RLS	Recall old (last) state
RC1	Recall reg 1
RC2	Recall reg 2
RC3	Recall reg 3
RC4	Recall reg 4
RC5	Recall reg 5
IPR	Instrument Preset
PLM	Plot Menu*
PLA	Plot all
PL1	Plot Trace 1
PL2	Plot Trace 2
PLG	Plot Graticule
PLC	Plot Characters
PM1	Plot Trace 1 Marker
PM2	Plot Trace 2 Marker
CPT	Configure Plot menu
T1L	Trace 1 line type (entry)
T2L	Trace 2 line type (entry)
T1P	Trace 1 pen number (entry)
T2P	Trace 2 pen number (entry)
PGP	Graticule pen no. (entry)
PNM	Pen speed fast (max)
PNS	Pen speed slow
PLD	Set Plot Config to default
---------------------------------------
### From rest of manual and elsewhere
AN0	AN0
AN1	AN1
ANC	ANC
BD0	BD0	Bus diag off (3-47)
BD1	BD1	Bus diag on, fast (3-47)
BD2	BD2	Bus diag on, slow (3-47)
BW1	BW1	Resolution BW 1Hz (3-27)
BW2	BW2	Resolution BW 10Hz (3-27)
BW3	BW3	Resolution BW 100Hz (3-27)
BW4	BW4	Resolution BW 1kHz (3-27)
CH0	CH0	Characters off (p3-58)
CH1	CH1	Characters on (p3-58)
CKB	CKB	Clear Key Buffer (3-43)
DAN	DAN	Dump Avg Number (3-42)
DCH	DCH	Dump Characters (p3-45)
DD1	DD1	Dump reg 1 (p3-34)
DD2	DD2	Dump reg 2 (p3-34)
DD3	DD3	Dump reg 3 (p3-34)
DD4	DD4	Dump reg 4 (p3-34)
DKY	DKY	Dump Keyboard (3-43)
DM1	DM1	Dump Marker 1 (3-38)
DM2	DM2	Dump Marker 2 (3-38)
DMS	DMS	Dump Status (3-41)
DRA	DRA
DRB	DRB
DRR	DRR
DT1	DT1	Dump Trace 1 (3-36)
DT2	DT2	Dump Trace 2 (3-36)
ENA	ENA	Enter annotation (3-51)
ENG	ENG	Enter graphics (3-53)
ENM	ENM	Enter Menu (3-50)
ER0	ER0	Nothing will be reported (p 3-63)
ER1	ER1	Only Errors will be reported (p 3-63)
ER2	ER2	Errors and Warnings will be reported (p 3-63)
ER3	ER3	Errors, warnings and messges will be reported (p 3-63)
EXM	EXM	-- Execute Memory #I<4 bytes address>
FM1	FM1	Ascii format (3-47)
FM2	FM2	64bit IEEE format (3-48)
FM3	FM3	32bit fast proc format (3-48)
GR0	GR0	Graticule Off (p3-58)
GR1	GR1	Graticule On (p3-58)
ID?	ID?	Dump Instrument ID (p3-30)
KI1	KI1
LD1	LD1	Load Reg 1 (p3-34)
LD2	LD2	Load Reg 2 (p3-34)
LD3	LD3	Load Reg 3 (p3-34)
LD4	LD4	Load Reg 4 (p3-34)
LMI	LMI	Learn mode in (3-39)
LMO	LMO	Learn mode out (3-39)
LRA	LRA
LRB	LRB
LRR	LRR
MN0	MN0	Menu off	(3-50)
MN1	MN1	Menu on		(3-50)
MNC	MNC	Menu Clear	(3-50)
MP1	MP1	Marker Pos 1 (3-38)
MP2	MP2	Marker Pos 1 (3-38)
P99	P99
RDM	RDM	-- Read Memory #I<4 bytes address>
SK1	SK1
SK2	SK2
SK3	SK3
SK4	SK4
SK5	SK5
SK6	SK6
SK7	SK7
SK8	SK8
SQM	SQM	SRQ Mask (p 3-63)
SRQ	SRQ	Send SRQ
STE	STE	Settling Time Entry 
SUF	SUF
TKM	TKM	Take Measurement (3-58)
UDI	UDI
WTM	WTM	-- Probably: Write Memory
"""
