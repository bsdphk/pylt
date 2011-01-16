#!/usr/local/bin/python

import sys
import time
import prologix_usb

class hp33120a(prologix_usb.gpib_dev):

	def __init__(self, name = "gpib0", adr = 10):
		prologix_usb.gpib_dev.__init__(self, name, adr)
		self.attr("read_tmo_ms", 2000)
		self.spoll_data = 0x10
		self.spoll_cmd = 0x0
		self.errors()
		x = self.ask("*IDN?").split(",")
		if x[0] != "HEWLETT-PACKARD" or x[1] != "33120A":
			self.fail("HP33120 ID Failure (%s)" % x)
		self.id = "HP33120A"
		self.AOK()

	#######################
	# PYLT Standard methods
	#######################

	def errors(self, f=sys.stderr):
		r = False
		while True:
			x = self.ask("SYST:ERR?")
			if x == '+0,"No error"':
				break
			f.write(self.id + ".ERROR: " +  x + "\n")
			r = True
		return r

	def reset(self):
		self.wr("*RST");
		self.AOK()

if __name__ == "__main__":
	d = hp33120a()
	print("Device responds: " + d.ask("*IDN?"))
