#!/usr/local/bin/python

from __future__ import print_function

import prologix_usb

import time
import math
import sys

hp6626a_errors = {
	0:	"NO ERROR",
	1:	"INVALID CHAR",
	2:	"INVALID NUM",
	3:	"INVALID STR",
	4:	"SYNTAX ERROR",
	5:	"NUMBER RANGE",
	6:	"NO QUERY",
	7:	"DISP LENGTH",
	8:	"BUFFER FULL",
	9:	"EEPROM ERROR",
	10:	"HARDWARE ERROR",
	11:	"HDV ERR CH 1",
	12:	"HDV ERR CH 2",
	13:	"HDV ERR CH 3",
	14:	"HDV ERR CH 4",
	15:	"NO MODEL NUM",
	16:	"CAL ERROR",
	17:	"UNCALIBRATED",
	18:	"CAL LOCK",
	20:	"GPIB TIMER FAIL",
	21:	"GPIB RAM FAIL",
	22:	"SKIP SLF TST",
	27:	"GPIB ROM FAIL",
	28:	"INVALID STR",
	29:	"GPIB EEPROM CKSUM",
	30:	"STORE LIMIT",
}

class hp6626a(prologix_usb.gpib_dev):

	def __init__(self, name = "gpib0", adr = 5):
		prologix_usb.gpib_dev.__init__(self, name, adr)
		self.attr("read_tmo_ms", 500)
		self.spoll_cmd = 0x10
		self.wait_cmd(12)
		x = self.ask("ID?")
		if x != "HP6626A":
			print("HP6626A ID FAILURE (%s)" % x)
			assert False
		self.id = x
		self.__vset=dict()
		self.__vrset=dict()
		self.__iset=dict()
		self.__irset=dict()
		self.__out=dict()
		self.autorange=dict()

		# The possible pairings of outputs
		self.__dual = {
			12: (1,2),
			34: (3,4)
		}

		# Voltage ranges
		self.__vranges = {
			1: (7.00, 50.5),
			2: (7.00, 50.5),
			3: (16.16, 50.5),
			4: (16.16, 50.5)
		}

		# Current ranges
		self.__iranges = {
			1: (.01545, .515),
			2: (.01545, .515),
			3: (.206, 2.06),
			4: (.206, 2.06)
		}

		for i in (1, 2, 3, 4, 12, 34):
			self.autorange[i] = True
		self.__readback()
		self.__dualvr()
	
	def __dualvr(self):
		# Calculate the possible dual voltage ranges
		for i in (12, 34):
			c1,c2 = self.__dual[i]
			self.__vranges[i] = (
			    self.__vranges[c1][0] - self.__v0(i),
			    self.__vranges[c1][1] - self.__v0(i)
			)
			self.__iranges[i] = self.__iranges[c1]

	def __v0(self, chan):
		assert chan in self.__dual
		if chan == 12 and self.__irset[chan] < 0.050:
			return 1.0
		elif chan == 12:
			return 4.0
		elif chan == 34 and self.__irset[chan] < 1.:
			return 1.0
		else:
			return 2.0

	def __readback(self):
		# Initilialize cached settings
		for i in range(1,5):
			self.__vset[i] = float(self.ask("VSET? %d" % i))
			self.__vrset[i] = float(self.ask("VRSET? %d" % i))
			self.__iset[i] = float(self.ask("ISET? %d" % i))
			self.__irset[i] = float(self.ask("IRSET? %d" % i))
			self.__out[i] = int(self.ask("OUT? %d" % i))
		for i in (12, 34):
			c1,c2 = self.__dual[i]
			self.__iset[i] = min(self.__iset[c1], self.__iset[c2])
			self.__irset[i] = min(self.__irset[c1], self.__irset[c2])
			if i in self.__vset:
				del self.__vset[i]
				del self.__vrset[i]

	#######################
	# PYLT Standard methods
	#######################

	def errors(self, f=sys.stderr):
		i = self.spoll()
		if i & 0x20:
			x = int(self.ask("ERR?"))
			if x in hp6626a_errors:
				y = hp6626a_errors[x]
			else:
				y = "UNKNOWN ERROR"
			f.write("HP6626A.ERROR: %d = " % x + y + "\n")
			return True
		return False

	def report(self, f = sys.stdout):
		self.AOK()
		f.write(self.id + ".STATUS:\n")
		f.write("CH ON     VR    VSET   VOUT?    IR    ISET   IOUT? STATUS\n")
		f.write("---------------------------------------------------------\n")
		v=dict()
		a=dict()
		s=dict()
		for i in range(1,5):
			v[i] = float(self.ask("VOUT? %d" % i))
			a[i] = float(self.ask("IOUT? %d" % i))
			s[i] = int(self.ask("STS? %d" % i))
			f.write("%2d  %d   %4.1f %7.3f %7.3f %5.3f %7.3f %7.3f" 
			     % (i, self.__out[i], self.__vrset[i], self.__vset[i], v[i],
				self.__irset[i], self.__iset[i], a[i]))
			if s[i] & 1:
				f.write(" cv")
			if s[i] & 2:
				f.write(" +cc")
			if s[i] & 4:
				f.write(" -cc")
			if s[i] & 8:
				f.write(" OvrVOLT")
			if s[i] & 16:
				f.write(" OvrTEMP")
			if s[i] & 32:
				f.write(" UNREG")
			if s[i] & 64:
				f.write(" OvrCUR")
			if s[i] & 128:
				f.write(" CP")
			f.write("\n")
		for i in (12, 34):
			if i not in self.__vset:
				continue
			if i not in self.__iset:
				continue
			c1,c2 = self.__dual[i]
			f.write("%2d      %4.1f %7.3f %7.3f %5.3f %7.3f %7.3f\n" 
			     % (i, self.__vrset[i], self.__vset[i], v[c1] - v[c2],
				self.__irset[i], self.__iset[i], (a[c1] - a[c2]) * .5))
		f.write("---------------------------------------------------------\n")
		self.AOK()

	def reset(self):
		self.ask("ERR?")
		self.AOK()
		self.wr("CLR")
		self.wait_cmd(12)
		self.__readback()

	########################
	# HP6626 Voltage methods
	########################

	def vrange(self, chan, vrange):
		self.AOK()
		assert chan in self.__vranges
		if chan in self.__dual:
			self.__dualvr()
			vrange = math.fabs(vrange)
		assert vrange >= 0.
		j = None
		for i in (0, 1):
			if vrange <= self.__vranges[chan][i]:
				j =i 
				vx = self.__vranges[chan][i]
				break
		if j == None:
			print("HP6626A.PARAM: %f to high vrange for chan %d" % (vrange, chan))
			assert False
		if chan in self.__dual:
			c1,c2 = self.__dual[chan]
			self.vrange(c1, self.__vranges[c1][j])
			self.vrange(c2, self.__vranges[c2][j])
		elif self.__vrset[chan] != vx:
			self.wr("VRSET %d" % chan + " %.1f" % vx)
		self.__vrset[chan] = vx
		self.AOK()

	def vset(self, chan, volt):
		self.AOK()
		assert chan in self.__vranges
		if chan not in self.__dual:
			if self.autorange[chan]:
				self.vrange(chan, volt);
			assert volt >= -0.001 and volt <= self.__vrset[chan]
			if volt != self.__vset[chan]:
				self.wr("VSET %d" % chan + " %.6f" % volt)
		else:
			v2 = math.fabs(volt)
			if self.autorange[chan]:
				self.vrange(chan, v2);
			assert v2 <= self.__vrset[chan]
			c1,c2 = self.__dual[chan]
			vc = self.__vset[c1] - self.__vset[c2]
			v0 = self.__v0(chan)
			if volt * vc < 0:
				# Going though zero, program it explicity
				self.vset(c1, v0)
				self.vset(c2, v0)
			if volt > 0:
				self.vset(c2, v0)
				self.vset(c1, volt + v0)
			else:
				self.vset(c1, v0)
				self.vset(c2, v2 + v0)
		self.__vset[chan] = volt
		self.AOK()

	def vread(self, chan):
		self.AOK()
		assert chan in self.__vset
		v = float(self.ask("VOUT? %d" % chan))
		self.AOK()
		return v


	########################
	# HP6626 Current methods
	########################

	def irange(self, chan, irange):
		self.AOK()
		assert chan in self.__irset
		assert irange > 0.
		if chan in self.__dual:
			c1,c2 = self.__dual[chan]
			self.irange(c1, irange)
			self.irange(c2, irange)
			self.__irset[chan] = self.__irset[c1]
		else:
			j = None
			for i in (0, 1):
				if irange <= self.__iranges[chan][i]:
					j =i 
					ix = self.__iranges[chan][i]
					break
			if j == None:
				print("HP6626A.PARAM: %f to high irange for chan %d" % (irange, chan))
				assert False
			assert j != None
			if self.__irset[chan] != ix:
				self.wr("IRSET %d" % chan + " %.3f" % ix)
			self.__irset[chan] = ix
		self.AOK()

	def iset(self, chan, amps):
		self.AOK()
		assert chan in self.__iset
		if self.autorange[chan]:
			self.irange(chan, amps)
		assert amps >= 0. and amps <= self.__irset[chan]
		if chan in self.__dual:
			c1,c2 = self.__dual[chan]
			self.iset(c1, amps)
			self.iset(c2, amps)
			self.__iset[chan] = self.__iset[c1]
		else:
			if self.__iset[chan] != amps:
				self.wr("ISET %d" % chan + " %.6f" % amps)
			self.__iset[chan] = amps
		self.AOK()

	def iread(self, chan):
		self.AOK()
		assert chan in self.__iset
		a = float(self.ask("IOUT? %d" % chan))
		self.AOK()
		return a

if __name__ == "__main__":
	d = hp6626a()
	print("Device responds: " + d.ask("ID?"))
	d.report()

doc = """
Query accumulated status register		ASTS?	1-4	---			Q2
Return power supply to turn on state		CLR	---	---			C1
Turn calibration mode on or off			CMODE	---	0,1 (OFF,ON) 		C2
Query if calibration mode is on			CMODE?	---	See Table 5-4		Q1
Set the state of outputs at power on		DCPON	---	0,1 (OFF, ON) CC+
								2,3 (OFF, ON) CC-
Query outputs power on state			DCPON?	---	---
Set the reprogramming delay time		DLY	1-4	0-32			C4
Query the setting of the delay time		DLY?	1-4	---			Q2
Turn front panel display on or off		DSP	---	0,1(OFF,ON)		C2
Display a string on front panel			DSP	---	''STRING''		C6
Query if front panel display is on		DSP?	---	---			Q1
Query present hardware error			ERR?	---	See Table 5-8		Q1
Query fault register				FAULT?	1-4	---			Q2
Query the model number of supply		ID?	---	---			Q1
Program the I DAC in counts			IDAC	1-4	See Service Manual	C4
Query setting of I DAC in counts		IDAC?	1-4	---			Q2
Send data to calibrate I circuits		IDATA	1-4	See Table 5-4		C5
Sets output to high I cal. value		IHI	1-4	See Table 5-4		C3
Sets output to low I cal. value			ILO	1-4	See Table 5-4		C3
Query measured I output				IOUT?	1-4	See Table 5-4		Q2
Used to Calibrate I readback circuits		IRDAT	1-4	See Table 5-4		C5
Set output to + I readback high cal value	IRHI	1-4	See Table 5-4		C3
Set output to - I readback high cal value	IRHN	1-4	See Table 5-4		C3
Set output to - I readback low cal value	IRLN	1-4	See Table 5-4		C3
Set output to + I readback low cal value	IRLO	1-4	See Table 5-4		C3
Set full scale current range of output		IRSET	1-4	See Table 5-4		C4
Query full scale current range			ISET?	1-4	See Table 5-4		Q2
Set current of an output			ISET	1-4	See Table 5-4		C4
Query current of an output			ISET?	1-4	See Table 5-4		Q2
Increase or decrease output current by value	ISTEP	1-4	See Table 5-4		C4
Select which output will be metered		METER	--- 	1-4			C2
Query which output is being metered		METER?	---	---			Q1
Set model number (after repair)			MODEL	---	"6626A"			??
Send data to calibrate -I readback		NIDAT	1-4	See Table 5-4		C5
Enable overcurrent protection			OCP	1-4	0,1 (OFF,ON)		C4
Query if OCP is enabled				OCP?	1-4	---			Q2
Reset overcurrent protection			OCRST	1-4	---			C3
Turn output on or off				OUT	1-4	0,1 (OFF,ON)		C4
Query if output is on or off			OUT?	1-4	---			Q2
Perform overvoltage calibration			OVCAL	1-4	See Table 5-4		C3
Reset overvoltage circuit			OVRST	1-4	---			C3
Set overvoltage trip value			OVSET	1-4	See Table 5-4		C4
Query overvoltage trip value			OVSET?	1-4	See Table 5-4		Q2
Enable power on service request			PON	---	0,1 (OFF,ON)		C2
Query if PON is enabled				PON?	1-4	---			Q1
Recall voltage and current settings		RCL	---	0-10			C2
Set readback DAC to a number of counts		RDAC	1-4	See Service Manual	C4
Query readback DAC count setting		RDAC?	1-4	---			Q2
Query revision date of ROM			ROM?	---				Q1
Query revision date of secondary ROM		SROM?	1-4	---			Q2
Set causes for generating a service request	SRQ	---	01,2,3			C2
Query causes which will generate an SRQ		SRQ?	---	---			Q1
Store present output state			STO	---	0-10			C2
Query preset status of output			STS?	1-4				Q2
Perform self test on GP-IB interface		TEST? 					C1
Set bits in mask register			UNMASK	1-4	0-255			C4
Query bits set in mask register			UNMASK?	1-4				Q2
Program the voltage DAC in counts		VDAC	1-4	See Service Manual	C4
Querys setting of voltage DAC in counts		VDAC?	1-4				Q2
Send data to calibrate the voltage circuits	VDATA	1-4	See Table 5-4		C5
Set output to high V calibration value		VHI	1-4	See Table 5-4		C3
Set output to low V calibration value		VLO	1-4	See Table 5-4 V		C3
Query inputs of analog multiplexer		VMUX?	1-4	1-18			C4
Query measured value of an output		VOUT?	1-4	See Table 5-4		Q2
Calibrate the voltage readback circuitry	VRDAT	1-4	See Table 5-4		C5
Set output to V readback high cal value		VRHI	1-4	See Table 5-4		C3
Set output to V readback low cal value		VRLO	1-4	See Table 5-4		C3
Set full scale voltage programming range	VRSET	1-4	See Table 5-4		C4
Query full scale voltage programming range	VRSET?	1-4	See Table 5-4		Q2
Set output voltage				VSET	1-4	See Table 5-4		Q2
Query setting of output voltage			VSET?	1-4	See Table 5-4		Q2
Increase or decrease output voltage by value	VSTEP	1-4	See Table 5-4		C4

Queries:

Voltage Setting					VSET?	1-4	SZD.DDD(nb3)		0(nb8)		Q2
Current Setting					ISET?	1-4	(nb2)			10 mA (nb8)	Q2
Full Scale Current Range			IRSET?	1-4	(nb2)			High (nb8)	Q2
Full Scale Voltage Range			VRSET?	1-4	ZD.DDD (nb8)		High (nb8)	Q2
Voltage Output					VOUT?	1-4	SZD.DDD (nb3)	--			Q2
Current Output					IOUT?	1-4	(nb2)		--			Q2
OVP Setting					OVSET?	1-4	SZZD.DD			55 V (nb8)	Q2
OC Protection On/Off				OCP?	1-4	ZZD			--		Q2
Output On/Off					OUT?	1-4	ZZD			--		Q2
Unmask Setting					UNMASK?	1-4	ZZD			0 (nb8)		Q2
Delay Setting					DLY?	1-4	<sp>ZD.DDD		.02 (nb8)	Q2
Status						STS?	1-4	ZZD			--		Q2
Accumulated Status				ASTS?	1-4	ZD			--		Q2
Fault						FAULT?	1-4	ZZD			--		Q2
Error						ERR?	--	ZZD			--		Ql
Service Request Setting				SRQ?	--	ZZD			0 (OFF)		Q1
Power-On SRQ On/Off				PON?	--	ZZD			0 (OFF) (nb9)	Q1
Display On/Off					DSP?	--	ZZD			1 (ON)		Q1
Model Number					ID?	--	Agilent 662XA (nb4)	--		Q1
Selftest					TEST?	--	ZZD			--		Q1
Calibration Mode				CMODE?	--	ZZD			0 (OFF)		Q1
DC Power On					DCPON?	--	ZZD			1 (ON) (nb9)	Q1
"""
