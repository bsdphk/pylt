#!/usr/local/bin/python

# Python Imports
import sys
import math
import time

# Python Imports
import prologix_usb

class hp5370b(prologix_usb.gpib_dev):

	def __init__(self, name = "gpib0", adr = 15):
		prologix_usb.gpib_dev.__init__(self, name, adr)
		self.id = "HP5370B"
		self.attr("read_tmo_ms", 2000)
		self.attr("rd_mode", 10)
		self.attr("eos", 3)

	def rd(self):
		return self.rd_chr(10)

	
	###############################################################
	# Return the "Teach" string, a 21 char long byte array
	def teach(self):
		self.wr("TE")
		return bytearray(d.rd_bin(21))

	###############################################################
	# In TB1 mode, the counter returns 5 bytes directly from the
	# registers on the A17 Count Chain Assembly with an EOI on
	# the last byte.
	#
	# According to p3-24, this mode is only good for +/-TI up to 320ps
	# but that is almost certainly a typo, as it would correspond to
	# only 4 bits of the five bytes having any meaning at all.
	#
	# A much more likely limit is approx 320 microseconds, which would
	# match the 16 bits of the N0 counter returned:
	#	65535 * 5e-9 = 327e-6
	#
	# If you can live without the seat-belts, the range is twice that
	# because the N0-overflow bit can be used as the 17th bit of the N0
	# counter, at the cost of not knowing when that rolls over.
	#
	# Set the erange param to True if you want that.
	#
	def bintofloat(self, x, erange=False):
		n1n2 = ((x[0] & 3) << 16) | (x[1] << 8) | x[2]
		if n1n2 & (1<<17):
			n1n2 -= (1 << 18)
		n0 = (x[3] << 8) | x[4]
		q = 1
		if x[0] & 0x80:
			return None
		if not x[0] & 0x20:
			q = -1.0
		if x[0] & 0x08:
			return None
		if x[0] & 0x04:
			if not erange:
				return None
			n0 += 65536
		t = (n1n2/256. + n0 * q) * 5e-9
		return t

	###############################################################
	# Read n samples in fast binary mode.
	# Return list of floating point values (or None if range error)
	#
	def read_fast(self, n):
		l = list()
		try:
			d.wr("TB1")
			for i in range(0,n):
				l.append(self.rd_bin(5))
		except:
			pass
		d.wr("TB0")
		r = list()
		for i in l:
			r.append(self.bintofloat(i))
		return r

	###############################################################
	# Use Teach and Learn to set a specific reference value
	#
	# The last 7 bytes of the TEach string is the reference value
	# in HP5370 specific floating point format.
	# (Details can be found in PyRevEng)

	def set_ref(self, refval):
		x = self.teach()
		m,e = math.frexp(refval / 5e-9)
		if m < 0:
			s = 0x80
			m = -m
		else:
			s = 0
		m = math.ldexp(m, -1)
		for i in range(14,20):
			m = math.ldexp(m, 8)
			h = int(m)
			m -= h
			x[i] = s | h
			s = 0
		
		e -= 31
		if e < 0:
			e += 256
		x[20] = e

		y=bytearray("LN")
		for i in x:
			if i == 10 or i == 27 or i == 13 or i == 43:
				y.append(27)
			y.append(i)
		d.wr(y)

if __name__ == "__main__":
	d=hp5370b()
	d.wr("TB0")
	print("Device has no ID function")

doc="""
Function:
---------
	FN1	Time Interval
	FN2	Trigger Levels
	FN3	Frequency
	FN4	Period
	FN5	Expansion Rom (undoc)

Gate Time (freq/period):
------------------------
	GT1	Single Period
	GT2	0.01 sec
	GT3	0.1 sec
	GT4	1 sec

Statistics:
-----------
	ST1	Mean
	ST2	Stddev (nsamp >= 100)
	ST3	Min
	ST4	Max
	ST5	Disp Ref
	ST6	Clear Ref (imm. exec.)
	ST7	Disp Events
	ST8	Set Ref (imm. exec.)
	ST9	All

Sample Size:
------------
	SS1	nsamp = 1
	SS2	nsamp = 100
	SS3	nsamp = 1000
	SS4	nsamp = 10k
	SS5	nsamp = 100k

Mode:
-----
	MD1	Frontpanel Display Rate, output if addressed
	MD2	Display Rate Hold, until "MR" cmd.
	MD3	Display Rate Fast (FP rate locked out)
	MD4	MD3+SRQ

Input Selection:
----------------
	IN1	Start Event = Start Input, Stop Event = Stop Input
	IN2	Start Event = Stop Input, Stop Event = Stop Input
	IN3	Start Event = Start Input, Stop Event = Start Input
	IN4	Start Event = Stop Input, Stop Event = Start Input

Slope Select:
-------------
	SA1:	Start chan positive
	SA2:	Start chan negative
	SO1:	Stop chan positive
	SO2:	Stop chan negative
	SE1:	Ext. Arm positive
	SE2:	Ext. Arm negative

Arm Select:
-----------
	AR1	+T.I Arming Only
	AR2	+T.I Arming
	EH0	Ext. Holdoff disable
	EH1	Ext. Holdoff enable
	EA0	Ext. Arm disable
	EA1	Ext. Arm enable

Internal Arm: (+/- TI arm mode only)
------------------------------------
	IA1	Internal Arm Auto
	IA2	Start Channel Arm
	IA3	Stop Channel Arm

Misc:
-----
	MR	Manual Rate
	MI	Manual Input
	SL	Slope Local
	SR	Slope Remote
	TL	Trigger Local
	TR	Trigger Remote
	TE	Teach (sends 21 bytes with EOI)
	PC	Period Complement
	TB0	Disable binary output
	TB1	Enable binary output
	SB	Sample size binary (send 24 bit binary)
	LN	Learn (send 21 bytes from TE)
	TA	Trigger Start level
	TO	Trigger Stop level
"""
