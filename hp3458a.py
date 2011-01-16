#!/usr/local/bin/python

import sys
import time
import prologix_usb

class hp3458a(prologix_usb.gpib_dev):

	def __init__(self, name = "gpib1", adr = 22):
		prologix_usb.gpib_dev.__init__(self, name, adr)
		self.spoll_cmd = 0x10
		self.spoll_data = 0x80
		self.attr("read_tmo_ms", 2000)
		self.attr("rd_mode", 10)
		#self.wr("TRIG HOLD")
		#self.wr("INBUF ON")
		self.errors()
		x = self.ask("ID?")
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
		self.wait()
		self.wr("TRIG HOLD")
		self.wr("INBUF ON")
		self.AOK()

	#################
	# HP3458A methods
	#################

	def mread(self, lo, hi):
		self.assert_noerror()
		self.wr("TRIG SGL")
		self.wr("QFORMAT NUM")
		l = list()
		for i in range(lo, hi, 2):
			l.append(self.ask("MREAD %d" % i))
		self.assert_noerror()
		return l

	def acal_dcv(self):
		print("ACAL DCV (approx 160 seconds)")
		self.wr("ACAL DCV")
		for t in range(0,180, 10):
			time.sleep(10)
			x = self.spoll()
			print(t, x)
			if x & 16 != 0:
				break
		self.assert_noerror()

	def acal_ac(self):
		print("ACAL DCV (approx 180 seconds)")
		self.wr("ACAL AC")
		for t in range(0,180, 10):
			time.sleep(10)
			x = self.spoll()
			print(t, x)
			if x & 16 != 0:
				break
		self.assert_noerror()

if __name__ == "__main__":
        d = hp3458a()
        print(d.id)

