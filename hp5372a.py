#!/usr/local/bin/python

import sys
import array
import time

import prologix_usb
import pcl_util

class hp5372a(prologix_usb.gpib_dev):

	def __init__(self, name = "gpib0", adr = 3):
		prologix_usb.gpib_dev.__init__(self, name, adr)
		x = self.ask("*IDN?")
		x = x.split(",")
		if x[0] != "Hewlett Packard" or x[1] != "5372A":
			self.fail("HP5372A ID error" + str(x))
		self.id = x[1]

	# Take a screen dump
	def screen_dump(self,fname = "_.hp5372a.pbm"):
		self.wr("INTERFACE;PSOURCE,DISPLAY")
		self.wr("PRINT")
		x = ""
		while True:
			x = x + self.rd()
			if x[-5:] == "\033*rB\0":
				break;
		pcl_util.pcl_to_pbm(x, fname)

if __name__ == "__main__":
	d=hp5372a()
	print("Device reponds: " + d.ask("*IDN?"))
	d.screen_dump()
