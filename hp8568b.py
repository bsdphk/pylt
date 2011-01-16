#!/usr/local/bin/python

import sys
import time
import prologix_usb

class hp8568b(prologix_usb.gpib_dev):

	def __init__(self, name = "gpib0", adr = 18):
		prologix_usb.gpib_dev.__init__(self, name, adr)
		x = self.ask("ID")
		if x != "HP8568B":
			self.fail("HP8568B ID failure (" + x + ")")
		self.id = x


if __name__ == "__main__":
	d=hp8568b()
	print("Device responds: " + d.ask("ID") + " Rev: " + d.ask("REV"))


