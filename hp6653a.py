#!/usr/local/bin/python

from __future__ import print_function

import prologix_usb

import time
import math
import sys

class hp6653a(prologix_usb.gpib_dev):

	def __init__(self, name = "gpib1", adr = 12):
		prologix_usb.gpib_dev.__init__(self, name, adr)


if __name__ == "__main__":

	d = hp6653a()
	print(d.ask("*IDN?"))
	print(d.ask("*OPT?"))
	print(d.ask("SYST:LANG?"))
	print(d.ask("SYST:VERS?"))
	print(d.ask("SYST:ERR?"))
	print(d.ask("DISP:MODE?"))
	print(d.wr("DISP:MODE NORM"))
	print(d.wr("DISP:TEXT 'HELLO WORLD'"))
	print(d.ask("DISP:TEXT?"))
	for i in range(100):
		print(d.ask("MEAS:CURR?"))
