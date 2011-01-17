#!/usr/local/bin/python

import usb488
import sys
import time

class u2004a(usb488.usb488):
	def __init__(self, serial = None):
		self.debug_fd = open("_.u2004a", "w")
		usb488.usb488.__init__(self,
		    "Agilent Technologies", "USB POWER SENSOR", serial)

		self.usbdev.default_timeout=7000
		self.spoll_data = 0x20
		self.reset()
		x = self.ask("*IDN?").split(',')
		self.id = x[1]
		self.AOK()

	def reset(self):
		self.debug("RESET begin")
		self.device_clear()
		self.wr("*RST")
		assert self.ask("SYST:ERR?") == '+0,"No error"'
		assert self.ask("INIT:CONT?") == "0"
		assert self.ask("TRIG:SOURCE?") == "IMM"
		self.wr("TRIG:SOURCE HOLD")
		self.wr("*ESE 1")
		self.wr("STAT:OPER:MEAS:ENAB 2")
		self.wr("STAT:OPER:ENAB 16")
		self.config(1e6,20,1)
		self.spoll()
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

	def measure(self, tmo=70000, fail=True):
		self.debug("measure() begin")
		self.AOK()
		self.spoll()
		t = time.time()

		self.wr("INIT:IMM")
		self.wr("*OPC")
		# This delay is important, USB bus hangs without it
		time.sleep(0.100)

		self.wait_spoll(0x20,tmo)
		self.debug("T %.3f" % (time.time() - t))
		self.spoll()
		x = self.ask("FETCH?", tmo=2000, fail=fail)
		self.ask("*ESR?")
		self.spoll()
		if fail:
			self.AOK()
		self.debug("measure() end %s" % str(x))
		if not fail and not x[0]:
			return x
		elif not fail:
			return (True, float(x[1]))
		return float(x)

if __name__ == "__main__":
	d = u2004a()
	print("Device reponds: " + d.ask("*IDN?"))
	print("Doing one measurements (this may take 40 seconds)")
	x = d.measure(tmo=1000, fail=False)
	if x[0]:
		print("SUCCESS: %.3f dBm" % x[1])
	else:
		print("FAILURE: %s" % str(x[1]))
		d.errors()
