#!/usr/local/bin/python

import sys
import time
import prologix_usb
import subprocess

class hp8568b(prologix_usb.gpib_dev):

	def __init__(self, name = "gpib0", adr = 18):
		prologix_usb.gpib_dev.__init__(self, name, adr)
		x = self.ask("ID")
		if x != "HP8568B":
			self.fail("HP8568B ID failure (" + x + ")")
		self.id = x

	def screen_dump(self, fname="_.hp8568b.eps", format="eps"):
		print(self.id + " Taking a " + format +
		    " screendump into " + fname)
		x=self.ask("PLOT 0,0,40000,40000")
		p = subprocess.Popen([
			"hp2xx",
			"-m", format,
			"-f", fname,
			"-w180",
			"-o5",
			"-O5",
			"-c42145670",
			"-p11111111",
			"-"
			], stdin=subprocess.PIPE)
		p.stdin.write(x)
		p.stdin.close()
		p.wait()


if __name__ == "__main__":
	d=hp8568b()
	print("Device responds: " + d.ask("ID") + " Rev: " + d.ask("REV"))
