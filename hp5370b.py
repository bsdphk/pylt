#!/usr/local/bin/python

import sys
import time
import prologix_usb

class hp5370b(prologix_usb.gpib_dev):

	def __init__(self, name = "gpib0", adr = 15):
		prologix_usb.gpib_dev.__init__(self, name, adr)
		self.id = "HP5370B"
		self.attr("read_tmo_ms", 2000)
		self.attr("rd_mode", 10)


if __name__ == "__main__":
	d=hp5370b()
	print("Device has no ID function")
