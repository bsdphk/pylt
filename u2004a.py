#!/usr/local/bin/python

import usb488
import sys
import time

class u2004a(usb488.usb488):
	def __init__(self, serial = None):
		self.debug_fd = open("_.U2004", "w")
		usb488.usb488.__init__(self,
		    "Agilent Technologies", "USB POWER SENSOR", serial)

		self.usbdev.default_timeout=70000
		self.spoll_data = 0x20

		x = self.ask("*IDN?").split(',')
		self.id = x[1]
		self.AOK()
		self.reset()

	def reset(self):
		self.debug("RESET begin")
		self.wr("*CLS")
		self.wr("*RST")
		self.errors()

		self.wr("ABORT")
		self.AOK()
		self.wr("INIT:CONT OFF")
		self.AOK()
		self.wr("TRIG:SOURCE HOLD")
		self.AOK()
		self.wr("*ESE 255")
		self.AOK()
		self.wr("STAT:OPER:MEAS:ENAB 2")
		self.AOK()
		self.wr("STAT:OPER:ENAB 16")
		self.AOK()
		self.debug("RESET end")


	def errors(self, f=sys.stderr):
		r = False
		while True:
			x = self.ask("SYST:ERR?")
			if x == '+0,"No error"':
				break
			f.write(self.id + ".ERROR: (" +  x + ")\n")
			r = True
		return r

	def config(self, freq=None, level=None, resolution=1):
		if freq != None:
			self.wr("FREQ %.0fHz" % freq)
			self.AOK()
		self.ask("*ESR?")
		if level == None:
			level = 20
		self.wr("CONF %g,%d" % (level, resolution))
		self.AOK()

	def measure(self, dur=70000):
		self.AOK()
		print("SP1 %02x" % self.spoll())
		t = time.time()
		self.wr("INIT:IMM")
		self.wr("*OPC")
		# This delay is important, USB bus hangs without it
		time.sleep(0.020)
		#self.wait_data(dur)
		self.wait_spoll(0x20,70000)
		print("T %.3f" % (time.time() - t))
		self.ask("*ESR?")
		print("SP2 %02x" % self.spoll())
		x = float(self.ask("FETCH?"))
		self.AOK()
		return x

if __name__ == "__main__":
	d = u2004a()
	print(d.id)



