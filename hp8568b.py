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
		self.errors()

	##############
	# PYLT methods
	##############

	def reset(self):
		d.wr("IP")

	def errors(self, f=sys.stderr):
		r = False
		while True:
			x = self.ask("ERR")
			if x == "0,0,0,0":
				break
			f.write(self.id + ".ERROR: " + x + "\n")
			r = True
		return r

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

	#################
	# HP8568B methods
	#################

	###############################################################
	# Read screen memory as array of 4096 unsigned shorts
	# See Appendix A in the manual for layout and meaning of this
	#
	def screen_memory(self):
		import array 
		x=bytearray()
		for i in range(0,5):
			self.wr("O2;DA%d;KS{" % (i * 1001))
			x.extend(self.rd_bin(2002))
		assert len(x) == 10010
		y = array.array("H")
		for i in range(0,4096):
			y.append(x[i * 2] * 256 + x[i * 2 + 1])
		return y

if __name__ == "__main__":
	d=hp8568b()
	print("Device responds: " + d.ask("ID") + " Rev: " + d.ask("REV"))
