#!/usr/local/bin/python

from __future__ import print_function

import sys
import time
import prologix_usb

class hp3458a(prologix_usb.gpib_dev):

	def __init__(self, name = "gpib0", adr = 22):
		prologix_usb.gpib_dev.__init__(self, name, adr)
		self.spoll_cmd = 0x10
		self.spoll_data = 0x80
		self.attr("read_tmo_ms", 2000)
		self.attr("rd_mode", "eoi")
		self.wr("END ALWAYS")
		#self.wr("TRIG HOLD")
		self.wr("INBUF ON")
		self.errors()
		x = self.ask("ID?").strip()
		if x != "HP3458A":
			print("HP3458A.ERROR: ID Failure (%s)" % x)
		assert x == "HP3458A"
		self.id = x
		self.AOK()

	#######################
	# PYLT Standard methods
	#######################

	def errors(self, f=sys.stderr):
		self.wait_cmd()
		if not self.spoll() & 0x20:
			return False
		while True:
			x = self.ask("ERRSTR?")
			if x == '0,"NO ERROR"':
				break
			f.write(self.id + ".ERROR: " +  x + "\n")
		return True

	def reset(self):
		self.wr("PRESET NORM")
		self.wait_cmd(tmo=20000)
		self.wr("TRIG HOLD")
		self.wr("INBUF ON")
		self.AOK()

	#################
	# HP3458A methods
	#################


	def acal_dcv(self):
		print("ACAL DCV expected duration: ~165 seconds)")
		t = time.time()
		self.wr("ACAL DCV")
		self.wait_cmd(tmo=200000)
		self.AOK()
		self.debug("ACAL DCV actual duration: %.1f" % (time.time() - t))
		print("ACAL DCV actual duration: %.1f" % (time.time() - t))

	def acal_ac(self):
		print("ACAL AC (expected duration: ~145 seconds)")
		t = time.time()
		self.wr("ACAL AC")
		self.wait_cmd(tmo=200000)
		self.AOK()
		print("ACAL DCV actual duration: %.1f" % (time.time() - t))

	def acal_ohms(self):
		print("ACAL OHMS (expected duration: ~670 seconds)")
		t = time.time()
		self.wr("ACAL OHMS")
		self.wait_cmd(tmo=800000)
		self.AOK()
		print("ACAL OHMS actual duration: %.1f" % (time.time() - t))

	def acal_all(self):
		print("ACAL ALL (expected duration: ~1000 seconds)")
		t = time.time()
		self.wr("ACAL ALL")
		self.wait_cmd(tmo=1000000)
		self.AOK()
		print("ACAL ALL actual duration: %.1f" % (time.time() - t))

	####################
	# HP3458A deep magic
	####################

	###############################################################
	# Undocumented CAL? queries
	# CAL? -1	21249=NUM_SAMPLES
	# CAL? -2	861=BURST2
	# CAL? -3	1149=BURST1
	# CAL? -4	11=NREADINGS
	# CAL? -5	2010=SMPL_RATE
	# CAL? -6	1=SSMP_INC
	# CAL? -7	3.54147092E-05=PERIOD
	# CAL 2437	16611, DEFEATS valid 2437
	# CAL 2941	0, DESTRUCTIVE OVERLOADS valid 2941

	###############################################################
	# Read a memory range using the undocumented MREAD command
	# Return as a list of python 'int' [0...65535]
	#
	# ROMs are located at:		high/low byte
	# 	0x000000-0x01ffff	U110 U111
	# 	0x200000-0x03ffff	U112 U113
	# 	0x040000-0x04ffff	U114 U115
	#
	# NVRAMs are located at:
	#	0x060000-0x060fff	CALRAM 	(see nvram() function below)
	#	0x120000-0x12ffff	DATARAM
	#
	# Other undocumented commands: MWRITE, MADDR, JSR & XYZZY
	#
	def mread(self, lo, hi):
		self.AOK()
		self.wr("TRIG HOLD")
		self.wr("QFORMAT NUM")
		# Addresses must be even
		assert lo & 1 == 0
		assert hi & 1 == 0
		l = list()
		for i in range(lo, hi, 2):
			j = int(self.ask("MREAD %d" % i))
			if j < 0:
				j = 65536 + j
			l.append(j)
		self.AOK()
		return l

	###############################################################
	# Read a copy of the Calibration NVRAM and write it to a file.
	#
	# The NVRAM containing the calibration data is mapped in the
	# high byte only, so we need to retrieve 2048 words and discard
	# the low byte from them.
	#
	# If your NVRAM is socketed, pretty much any EPROM programmer
	# should be able to write the device from the file this function
	# creates.
	#
	# Writing it from software is not easy and involves downloading
	# M68000 machine code to the instrument for execution.
	# There are several layers of write-protection involved and
	# the functions that know how to deal with that magic are
	# not the same address from one software version to the next.
	#
	# If you need to do it really, really, really, badly, send me
	# an email and I may drop you some hints. /phk
	#

	def nvram(self,  fname="_.hp3458.calram.bin"):
		l=self.mread(0x60000, 0x60000 + 2048 * 2)
		fo = open(fname, "w")
		for i in l:
			fo.write("%c" % (i >> 8))
		fo.close()


def voltlog(d):
	fo = open("_volt_log.txt", "w")
	tcal = 3600
	t0 = time.time()
	while True:
		tc = time.time()
		fo.write("\n")
		s = "# %.3f %10.3f ACAL DCV" % (tc, tc - t0)
		print(s)
		fo.write(s + "\n")
		d.acal_dcv()
		t = time.time()
		a = d.ask("CAL? 72")
		s = "# %.3f %10.3f CAL? 72 = %s" % (t, t - t0, a)
		print(s)
		fo.write(s + "\n")
		d.wr("NPLC 200")
		d.wr("NDIG 8")
		while True:
			d.wait_data(tmo=10000)
			a = d.rd()
			t = time.time()
			if a != "":
				s = "%.3f %10.3f %10.3f %s" % (t, t-t0, t-tc, a)
				print(s)
				fo.write(s + "\n")
				fo.flush()
			if t > tc + tcal:
				fo.write("\n")
				break

if __name__ == "__main__":
        d = hp3458a()
        print(d.id)
	for a in sys.argv[1:]:
		if a == "-voltlog":
			voltlog(d)
		if a == "-sn18":
			print("TIME", time.time())
			print("Factory CAL72", d.ask("CAL? 72,0"))
			print("Actual CAL72", d.ask("CAL? 72,1"))
			print("Min CAL72", d.ask("CAL? 72,3"))
			print("Max CAL72", d.ask("CAL? 72,5"))
			d.acal_dcv()

