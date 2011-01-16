#!/usr/local/bin/python

import sys
import time
import prologix_usb

class hp8657a(prologix_usb.gpib_dev):

	def __init__(self, name = "gpib0", adr = 6):
		prologix_usb.gpib_dev.__init__(self, name, adr)

	def set_freq(self, hz):
		self.wr("FR %.0fHZ" % hz)

	def set_dbm(self, dbm):
		self.wr("AP %.1fDM" % dbm)


if __name__ == "__main__":
	d=hp8657a()
	print("Device has no way of talking back")
	d.set_freq(10e6)
	d.set_dbm(-70.0)


doc="""
NB: Has no serial poll or response support


FR		Frequency (carrier)	100kHz..1040MHz

AP		Amplitude (carrier)	-127...+7dBm (-143.5..+17dBm)
AO		Amplitude Offset

AM		Amplitude Modulation 
FM		Frequency Modulation

S1		External mod source
S2		400Hz mod source
S3		1kHz mod source
S4		No mod source
S5		DC FM mod source
PM		Pulse mod		(8657B only)
PF		Pulse mod (fast)	(8657B only)

HI		HI ALC
LO		LO ALC

UP		Step Up
DN		Step Down

IS		Increment Set
PI		Phase increment
PD		Phase decrement

R0		Standby
R1		On
R2		RF OFF
R3		RF ON
R4		RF DEAD
ST	[0-9]	Save
RC	[0-9]	Recall
SEQ		Sequence
GT		Flexible sequence
QS		Reverse sequence
RP		Reverse Power Protection Reset

Units
-----
DB		dB
DF		dBf
DM		dBm
EM		EMF
VL		Volt
MV		millivolt
UV		microvolt
HZ		Hz
KZ		kHz
MZ		MHz
PC		%
%		%

"""
