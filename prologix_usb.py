#!/usr/local/bin/python

from __future__ import print_function

import sys
import time
import serial
import pylt

pusb = dict()

ver = "Prologix GPIB-USB Controller version 6.95"

hwset = (
		"addr",
		"auto",
		"eoi",
		"eos",
		"eot_enable",
		"eot_char",
		"read_tmo_ms"
	)

def def_set(setting):
	setting["auto"] = 0
	setting["eoi"] = 1
	setting["eos"] = 0
	setting["eot_enable"] = 0
	setting["eot_char"] = 0
	setting["read_tmo_ms"] = 500
	setting["rd_mode"] = "eoi"

	setting["autocr"] = 1

class prologix_usb(object):

	def __init__(self, name):
		self.name = name
		self.debug_fd = open("_." + name, "w")
		self.debug("====", "=============================")

		self.ser = serial.Serial("/dev/" + name, 115200, timeout = 0.5)
		self.version_check()
		self.curset = dict()
		self.rd_settings()
		d = dict()
		def_set(d)
		self.set(d)
		pusb[name] = self

	def debug(self, pfx, str):
		print((self.name, "%.6f" % time.time(), pfx, str),
		    file=self.debug_fd)
		self.debug_fd.flush()

	def version_check(self):
		self.ser.write("\r")
		self.cmd("++mode 1")
		self.cmd("++auto 0")
		self.cmd("++addr 0")
		self.cmd("++savecfg 0")
		self.cmd("++ifc")
		while True:
			x = self.ask("++ver")
			if x == ver:
				break;
		assert x == ver

	def ask(self, str):
		self.cmd(str)
		x = self.ser.readline()
		x = x.strip("\r\n")
		self.debug("{r", x)
		return (x)

	def rd_settings(self):
		for i in hwset:
			self.curset[i] = self.ask("++" + i)

	def cmd(self, str):
		assert str[0:2] == "++"
		self.debug("}w", str)
		self.ser.write(str + "\r")

	def rd_eoi(self):
		self.cmd("++read eoi")
		x = self.ser.readline()
		self.debug("<eoi<",  x)
		return (x)

	def rd_chr(self, chr):
		self.cmd("++read %d" % chr)
		x = self.ser.readline()
		self.debug("<%d<" % chr,  x)
		return (x)

	def rd_bin(self, nbr, eoi = True):
		if eoi:
			self.cmd("++read eoi")
		else:
			self.cmd("++read")
		x = self.ser.read(nbr)
		x = bytearray(x)
		self.debug("<%d/%d<" % (nbr, len(x)),  x)
		return (x)

	def wr(self, str):
		assert str[0:2] != "++"
		self.debug(">", str)
		self.ser.write(str + "\r")

	def set(self, settings):
		for i in hwset:
			if i not in settings:
				continue
			if str(settings[i]) == self.curset[i]:
				continue
			self.cmd("++" + i + "  %d" % settings[i])
			self.curset[i] = "%d" % settings[i]
		if "read_tmo_ms" in settings:
			to = settings["read_tmo_ms"]
			self.ser.timeout = (to + 500) * 1e-3

	def spoll(self):
		self.cmd("++spoll")
		while True:
			a = self.ser.readline()
			self.debug("<sp<", a)
			if a.strip().isdigit():
				break
		return(int(a))

	def trigger(self):
		self.cmd("++trg")

	def clear(self):
		self.cmd("++clr")

class gpib_dev(pylt.pylt):

	def __init__(self, name, adr):
		if not name in pusb:
			x = prologix_usb(name)

		self.pusb = pusb[name]
		self.debug_fd = self.pusb.debug_fd
		pylt.pylt.__init__(self)

		self.setting = dict()
		def_set(self.setting)
		self.setting["addr"] = adr


	def wr(self, str):
		self.pusb.set(self.setting)
		self.pusb.wr(str)

	def rd_eoi(self, tmo=None, fail=True):
		self.pusb.set(self.setting)
		x = self.pusb.rd_eoi()
		if self.setting["autocr"]:
			x = x.strip("\r\n")
		return (x)

	def rd_chr(self, chr=10, tmo=None, fail=True):
		self.pusb.set(self.setting)
		x = self.pusb.rd_chr(chr)
		if self.setting["autocr"]:
			x = x.strip("\r\n")
		return (x)

	def rd_bin(self, cnt=1, tmo=None, fail=True):
		self.pusb.set(self.setting)
		x = self.pusb.rd_bin(cnt)
		return (x)

	def rd(self, tmo=None, fail=True):
		m = self.setting["rd_mode"]
		if m == "eoi":
			return self.rd_eoi()
		else:
			return self.rd_chr(m)

	def attr(self, name, val):
		self.setting[name] = val

	def spoll(self):
		self.pusb.set(self.setting)
		return(self.pusb.spoll())

	def trigger(self):
		self.pusb.set(self.setting)
		return(self.pusb.trigger())

	def clear(self):
		self.pusb.set(self.setting)
		self.pusb.clear()

