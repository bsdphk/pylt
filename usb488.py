#!/usr/local/bin/python

from __future__ import print_function

import array
import struct
import time

import usb.core
import usb.util

import pylt

usbtmc_tab16 = {
	0x01:	"STATUS_SUCCESS",
	0x02:	"STATUS_PENDING",
	0x80:	"STATUS_FAILED",
	0x81:	"STATUS_TRANSFER_NOT_IN_PROGRESS",
	0x82:	"STATUS_SPLIT_NOT_IN_PROGRESS",
	0x83:	"STATUS_SPLIT_IN_PROGRESS",
}

#################################################################################################################################
# A class to identify a USBTMC device, with optional matching on USBTMC protocol
# and the USB descriptor strings, which unfortunately, not always give useful info.
#
# We really want to be able to pin-point the device at this level without needing
# to stuff things into pipes, since that would disturb another program using that device.
#
# Best suggestion:  Match on serial number if that's unique.
#
class usbtmc_usbfind(object):
	def __init__(self, man=None, prod=None, serial=None, proto=1):
		self.man=man
		self.prod=prod
		self.serial=serial
		self.usbtmc_proto=proto

	def __call__(self, dev):
		if dev.bDeviceClass != 0:
			return;
		if dev.bDeviceSubClass != 0:
			return
		if dev.bDeviceProtocol != 0:
			return
		for cfg in dev:
			intf = usb.util.find_descriptor(cfg, bInterfaceClass=0xfe)
			if intf == None:
				continue
			if intf.bInterfaceSubClass != 0x03:
				pass
			if intf.bInterfaceProtocol != self.usbtmc_proto:
				pass
			if self.man != None and dev.iManufacturer != 0:
				if self.man != usb.util.get_string(dev, 100, dev.iManufacturer):
					return
			if self.prod != None and dev.iProduct != 0:
				if self.prod != usb.util.get_string(dev, 100, dev.iProduct):
					return
			if self.serial != None and dev.iSerialNumber != 0:
				if self.serial != usb.util.get_string(dev, 100, dev.iSerialNumber):
					return
			return (cfg, intf)

#################################################################################################################################
#
# USBTMC class
#
class usbtmc(object):
	def __init__(self, man=None, prod=None, serial=None):
		match = custom_match=usbtmc_usbfind(man, prod, serial)
		self.usbdev = usb.core.find(custom_match=match)
		assert self.usbdev != None
		self.Manufacturer = usb.util.get_string(self.usbdev, 100, self.usbdev.iManufacturer)
		self.Product = usb.util.get_string(self.usbdev, 100, self.usbdev.iProduct)
		self.SerialNumber = usb.util.get_string(self.usbdev, 100, self.usbdev.iSerialNumber)
		self.debug("USB.M=" + self.Manufacturer)
		self.debug("USB.P=" + self.Product)
		self.debug("USB.S=" + self.SerialNumber)
		self.usbcfg,self.usbintf = match(self.usbdev)
		self.usbdev.set_configuration(self.usbcfg.bConfigurationValue)
		self.usbtmc_tag = 3
		self.usbdev.default_timeout=10000

	def usbtmc_get_tag(self):
		a = self.usbtmc_tag
		self.usbtmc_tag += 1
		if self.usbtmc_tag == 256:
			self.usbtmc_tag = 3
		return a

	def usbtmc_mkmsg(self, typ, lx):
		l = array.array('B')
		l.append(typ)                   # MsgId
		t = self.usbtmc_get_tag()
		l.append(t)                     # btag
		l.append(255 - t)               # ~btag
		l.append(0)                     # rsv
		l.append(lx & 0xff)             # len
		l.append((lx >> 8) & 0xff)              
		l.append((lx >> 16) & 0xff)             
		l.append((lx >> 32) & 0xff)             
		return l

	def usbtmc_bulk_out(self, s, tmo=None):
		l = self.usbtmc_mkmsg(1, len(s))
		l.append(1)			# EOM
		l.append(0)			# rsv
		l.append(0)			# rsv
		l.append(0)			# rsv
		for i in s:
			l.append(ord(i))
		while len(l) & 0x3 != 0:
			l.append(0)		# pad
		self.debug("BULKOUT " + str(l))
		self.usbdev.write(2, l, timeout=tmo)

	def usbtmc_bulk_in(self, tmo=None, fail=True):
		lx = 4096
		l = self.usbtmc_mkmsg(2, lx)
		l.append(0)			# xfer attr
		l.append(0)			# termchar
		l.append(0)			# rsv
		l.append(0)			# rsv
		self.debug("BULKIN? " + str(l))
		self.usbdev.write(2, l, timeout = tmo)
		try:
			x = self.usbdev.read(0x81, lx, timeout = tmo)
		except Exception as foo:
			self.debug("BULK IN FAILED " + str( foo) + " " + str( foo.args))
			self.usbtmc_do_clear()
			if fail:
				self.fail("Read stalled")
			else:
				return (False, foo.args)
		l = x[4] | (x[5] << 8) | (x[6] << 16) | (x[7] << 24)
		s = ""
		for i in range(0,l):
			s = s + chr(x[12+i])
		self.debug("BULKIN " + str(x))
		if fail:
			return s
		else:
			return (True, s)

	def usbtmc_status_decode(self, x):
		y = list()
		if x[0] in usbtmc_tab16:
			y.append((x[0], usbtmc_tab16[x[0]]))
		else:
			y.append((x[0], "reserved"))
		return y

	def usbtmc_initiate_clear(self):
		x = self.usbdev.ctrl_transfer(0xa1, 5, 0, 0, 0x01, None)
		y = self.usbtmc_status_decode(x)
		y.append(list(x[1:]))
		self.debug("INITIATE_CLAR" + str(y))
		return y

	def usbtmc_check_clear_status(self):
		x = self.usbdev.ctrl_transfer(0xa1, 6, 0, 0, 0x02, None)
		y = self.usbtmc_status_decode(x)
		y.append(list(x[1:]))
		self.debug("CHECK_CLEAR_STATUS" + str(y))
		return y
		

	def usbtmc_get_capabilities(self):
		x = self.usbdev.ctrl_transfer(0xa0, 7, 0, 0, 0x18, None)
		y = self.usbtmc_status_decode(x)
		y.append(x[1])
		y.append(struct.unpack("<H", x[2:4]))
		y.append(x[4])
		y.append(x[5])
		y.append(list(x[6:12]))
		y.append(list(x[12:]))
		self.debug("GET_CAPABILITIES" + str(y))
		return y

	def usbtmc_do_clear(self):
		self.debug("DO_CLEAR begin")
		self.usbtmc_initiate_clear()
		d=.1
		t = time.time()
		while True:
			x = self.usbtmc_check_clear_status()
			if x[0][0] != 2:
				break
			time.sleep(d)
			if d < 1:
				d += d
		v = x[0][0] == 1
		# Clear Feature(Endpoint, HALT)
		self.usbtmc_do_check_pipes()
		x = self.usbdev.ctrl_transfer(0x02, 1, 0, 2, None, None)
		assert x == 0 or "CLEAR" == "HALT"
		self.debug("DO_CLEAR end (%.3f seconds)" % (time.time() - t) + str(v))
		return v

	def usbtmc_do_check_pipes(self):
		s = list()
		for i in (0x00, 0x02, 0x81, 0x83):
			x = self.usbdev.ctrl_transfer(0x82, 0, 0, i, 2, None)
			s.append(struct.unpack('BB', x))
		self.debug("DO_CHECKPIPES " + str(s))
		return s


#################################################################################################################################
#
# The actual usb488 class
#
class usb488(pylt.pylt, usbtmc):
	def __init__(self, man=None, prod=None, serial=None):
		pylt.pylt.__init__(self)
		usbtmc.__init__(self, man, prod, serial)
		self.usb488_tag = 2
		self.device_clear()

	def usb488_get_tag(self):
		a = self.usb488_tag
		self.usb488_tag += 1
		if self.usb488_tag == 128:
			self.usb488_tag = 2
		return a

	def wr(self, s, tmo=None):
		self.debug("WR <" + s + ">")
		self.usbtmc_bulk_out(s, tmo=tmo)

	def rd(self, tmo=None, fail=True):
		s = self.usbtmc_bulk_in(tmo=tmo, fail=fail)
		if fail:
			s = s.strip("\r\n")
		self.debug("RD <" + str(s) + ">")
		return s

	def spoll(self):
		t = self.usbtmc_get_tag() & 0x7f
		self.debug("SPOLL begin (%02x)" % t)
		self.usbtmc_do_check_pipes()
		try:
			x = self.usbdev.ctrl_transfer( 0xa1, 128, t, 0, 3, 1000)
		except:
			x = self.usbdev.ctrl_transfer( 0xa1, 128, t, 0, 3, 1000)
		z = self.usbdev.read(0x83, 2, None, 1000)
		self.debug("SPOLL " + str(x) + str(z) + " ==> 0x%02x" % z[1])
		assert x[0] == 1 or "SPOLL" == "STATUS"
		assert x[1] == t or "SPOLL" == "TAG"
		assert (z[0]&0x7f) == t or "SPOLL" == "INTR TAG"
		return z[1]

	def device_clear(self):
		self.usbtmc_do_clear()
