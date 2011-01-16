#!/usr/local/bin/python

import sys
import time
import prologix_usb
import pcl_util

class tds540a(prologix_usb.gpib_dev):

	def __init__(self, name = "gpib0", adr = 1):
		prologix_usb.gpib_dev.__init__(self, name, adr)
		self.attr("read_tmo_ms", 2000)
		self.attr("rd_mode", 10)
		self.attr("autocr", 1)
		self.errors()
		x = self.ask("*IDN?").split(",")
		if x[0] != "TEKTRONIX" or x[1] != "TDS 540A":
			self.fail("TDS540A ID Failure (%s)" % x)
		self.id = "TDS540A"
		self.AOK()

	#######################
	# PYLT Standard methods
	#######################

	def errors(self, f=sys.stderr):
		r = False
		while int(self.ask("*ESR?")) & 0x20:
			x = self.ask("EVMsg?")
			if x == '0,"No events to report - queue empty"':
				break
			f.write(self.id + ".ERROR: " +  x + "\n")
			r = True
		return r

	def reset(self):
		self.wr("*RST");
		self.AOK()

	def screen_dump(self, fname = "_.tds540a.pbm"):
		print(self.id + " Taking a screendump into " + fname)
		self.AOK()
		self.wr("HARDCOPY abort")
		self.AOK()
		self.wr("CLEARMenu")
		self.AOK()
		self.wr("HARDCOPY:FORMAT THINKJET")
		self.wr("HARDCOPY:LAYOUT PORTRAIT")
		self.wr("HARDCOPY:PORT GPIB")
		self.AOK()
		self.wr("HARDCOPY start")
		x = ""
		while True:
			y = self.rd()
			x = x + y
			if y[-1:] == "\014":
				break
		pcl_util.pcl_to_pbm(x, fname)
			

if __name__ == "__main__":
	d = tds540a()
	print("Device responds: " + d.ask("*IDN?"))
	d.AOK()
	d.screen_dump()
	
