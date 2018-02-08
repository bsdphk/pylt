#!/usr/local/bin/python

from __future__ import print_function

import sys
import time
import prologix_usb

class hp3245a(prologix_usb.gpib_dev):

	def __init__(self, name = "gpib0", adr = 9):
		prologix_usb.gpib_dev.__init__(self, name, adr)
		self.spoll_cmd = 0x10
		self.spoll_data = 0x80
		self.attr("read_tmo_ms", 2000)
		self.attr("rd_mode", "eoi")
		self.wr("END ALWAYS")
		self.wr("INBUF ON")
		self.errors()
		x = self.ask("ID?")
		if x != "HP3245":
			print("HP3245A.ERROR: ID Failure (%s)" % x)
		assert x == "HP3245"
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
			x = self.ask("ERRSTR?").strip()
			if x == '0,"NO ERROR"':
				break
			f.write(self.id + ".ERROR: " +  x + "\n")
		return True

	def reset(self):
		self.wr("RESET")
		self.wait_cmd(tmo=20000)
		self.wr("END ALWAYS")
		self.wr("INBUF ON")
		self.AOK()

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

	def ftest(self, n):
		self.wr("FTEST %d" % n)
		d.wait_cmd(tmo=20000)
		return self.rd()

	def ftests(self):
		print("COAX: Front A-out Front A-trig, press ENTER")
		sys.stdin.readline()
		print(self.ftest(0))

		print("COAX: Back A-out Front A-trig, press ENTER")
		sys.stdin.readline()
		print(self.ftest(1))
		
		print("COAX: Back B-out Front B-trig, press ENTER")
		sys.stdin.readline()
		print(self.ftest(101))

		print("COAX: Front B-out Front B-trig, press ENTER")
		sys.stdin.readline()
		print(self.ftest(100))
		

if __name__ == "__main__":
        d = hp3245a()
        print(d.id)
	for a in sys.argv[1:]:
		if a == "-ftest":
			d.ftests()
		if a == "-ask":
			while True:
				a = sys.stdin.readline().strip()
				if a in ("quit", "exit"):
					break;
				print(d.ask(a))

