#!/usr/local/bin/python

import sys
import time
import prologix_usb

class hp3336c(prologix_usb.gpib_dev):

	def __init__(self, name = "gpib0", adr = 13):
		prologix_usb.gpib_dev.__init__(self, name, adr)
		self.attr("eos", 2)
		self.attr("spoll_data", 0x00)
		self.attr("spoll_cmd", 0x0)
		self.errors()
		self.id = "HP3336C"
		self.AOK()

	#######################
	# PYLT Standard methods
	#######################

	def errors(self, f=sys.stderr):
		r = False
		while True:
			x = self.ask("IER")
			if x == "ER0":
				break
			f.write(self.id + ".ERROR: " +  x + "\n")
			r = True
		return r

	##################
	# HP3336C methods
	##################

	def set_freq(self, hz):
		self.wr("FR%.3fHZ" % hz)
		self.AOK()

	def read_freq(self):
		x = self.ask("IFR")
		self.AOK()
		assert x[:2] == "FR"
		assert x[-2:] == "HZ"
		return float(x[2:-2])

	def set_dbm(self, dbm):
		self.wr("AM%.3fDB" % dbm)
		self.AOK()

	def read_dbm(self):
		x = self.ask("IAM")
		self.AOK()
		assert x[:2] == "AM"
		assert x[-2:] == "DB"
		return float(x[2:-2])

if __name__ == "__main__":
	d = hp3336c()
	print("Device reponds (%s)" % d.id)
	print("Freq: %.11e Hz %.1f dBm" % (d.read_freq(), d.read_dbm()))


doc="""
Commands:
---------
FF	hz	Frequency
FR	hz	Frequency
AM	dbm	Amplitude
PH	deg	Phase
ST	hz	Sweep Start Frequency
SP	hz	Sweep Stop Frequency
MF	hz	Marker Frequency
TI	sec	Sweep time

FL0		Fast Levelling off
FL1		Fast Levelling on
MD1		Data transfermode 1
MD2		Data transfermode 2 (buffered to max 48 char)
SM1		Linear Sweep
SM2		Log Sweep
AP		Assign Zero Phase
SS		Start Single Sweep (send twice)
SC		Start Continuos Sweep
SR	digit	Store Program
RE	digit	Recall Program
MS	[@-O]	Masking Service Requests

		A		B		C
OI1		75 Ohm		75 Ohm		50 Ohm
OI2		150 Ohm		124 Ohm		75 Ohm
OI3		600 Ohm		135 Ohm
OI4				600 Ohm

MA0		AM off
MA1		AM on
MP0		PM off
MP1		PM on

AB0		Amplitude Blanking off
AB1		Amplitude Blanking on

Queries:
--------
IFR		Query Frequency
IFF		--//--
IAM		Amplitude
IPH		Phase
IST		Sweep Start Freq
ISP		Sweep Stop Freq
IMF		Marker Freq
ITI		Sweep Time
IOI		Impedance
ISM		Sweep Mode
IMA		AM mod
IMP		PM mod
IER		Error Code
IAB		Amplitude Blocking
IFL		Fast Levelling

Units:
------
HH		Hertz
HZ		Hertz
KH		KiloHertz
MH		MegaHertz
DB		dBm
DE		Degrees
SE		Seconds

Errors:
-------
0		No error
1		Entry param data is absolutely out of bounds
2		Invalid units
4		Sweep time too small
6		Sweep BW too small (ST to small for log, ST > SP)
7		Unrecognized program from HP-IB
8		Unrecognized char received
9		Option does not exist
"""
