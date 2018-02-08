#/usr/local/bin/python
#
# This is the PYLT baseclas which defines the fall-back methods
#
# This file also serves to document the canonical method functions
# and other programming conventions
#
# Timeout arguments are always named "tmo" and have units of milliseconds.
#

import sys
import time

class PyltError(Exception):
	def __init__(self, id, reason):
		self.id = id
		self.reason = reason
		self.args = (str(id), str(self.reason),)
	def __str__(self):
		return str(id) + ":" + str(self.reason)

class pylt(object):

	def __init__(self):
		# Instrument identification, eg: "HP6626A"
		self.id = "undefined"
		self.spoll_cmd = 0x00
		self.spoll_data = 0x00
		if not hasattr(self, 'debug_fd'):
			self.debug_fd = sys.stderr

	###############################################################
	# Raise a Pylt specific exception
	def fail(self, s):
		raise PyltError(self.id, str(s))

	###############################################################
	# Dump debug output
	def debug(self, s):
		self.debug_fd.write(self.id + ".DEBUG: " + s + "\n")
		self.debug_fd.flush()

	###############################################################
	# Report any errors to f
	# Return True if there are any
	def errors(self, f=sys.stderr):
		sys.stderr.write(
		    "PYLT.WARN: [%s].errors() undefined\n" % self.id)
		return False

	###############################################################
	# Read a response
	# if fail is True, raise an exception if we cannot complete the read
	# if fail is False return a two-element tupple, either:
	#	( True, <result> )
	# or
	#	( False, <diagnostic> )
	def rd(self, tmo=None, fail=True):
		sys.stderr.write("PYLT.WARN: [%s].rd() undefined\n" % self.id)
		return None

	###############################################################
	# Send a command
	# XXX: Technically this can fail too...
	def wr(self):
		sys.stderr.write("PYLT.WARN: [%s].wr() undefined\n" % self.id)

	###############################################################
	# Ask a question
	# Same meaning of fail argumentas rd()
	def ask(self, q, tmo = None, fail=True):
		self.wr(q)
		return self.rd(tmo=tmo, fail=fail)

	###############################################################
	# Raise exception if the instrument reports errors
	def AOK(self):
		if self.errors():
			self.fail('Instrument reported errors')

	###############################################################
	# Give a brief report of instrument state
	def report(self, f=sys.stdout):
		sys.stderr.write(
		    "PYLT.WARN: [%s].report() undefined\n" % self.id)

	###############################################################
	# Reset instrument to known state
	def reset(self):
		sys.stderr.write(
		    "PYLT.WARN: [%s].reset() undefined\n" % self.id)

	###############################################################
	# Trigger intrument into action
	def trigger(self):
		sys.stderr.write(
		    "PYLT.WARN: [%s].trigger() undefined\n" % self.id)

	def spoll(self):
		sys.stderr.write(
		    "PYLT.WARN: [%s].spoll() undefined\n" % self.id)
		return 0

	###############################################################
	# Wait for a bits to turn on in spoll()
	#
	def wait_spoll(self, bits, tmo = 10000.):
		self.debug("SPOLL WAITING FOR %02x" % bits)
		assert bits > 0 or "wait_spoll bits" == "must > 0"
		assert bits < 256 or "wait_spoll bits" == "must be < 256"
		obits = 256
		te = time.time() + tmo * 1e-3
		x = 0
		dt = 0.001
		while time.time() < te:
			x = self.spoll()
			if x != obits:
				self.debug("SPOLL CHG %02x -> %02x" %
				    (obits, x))
				obits = x
			if x & bits:
				return True
			time.sleep(dt)
			if dt < 3:
				dt += dt
		return False

	###############################################################
	# Wait until instrument is ready.
	# if fail is set, fail when timeout expires, else return False
	#
	def wait_cmd(self, tmo = 10000, fail=True):
		if self.wait_spoll(self.spoll_cmd, tmo):
			return True
		if not fail:
			return False
		self.fail("Timeout waiting for cmd")

	###############################################################
	# Wait until instrument has data ready, return false if not
	# if fail is set, fail when timeout expires, else return False
	#
	def wait_data(self, tmo = 10000, fail=True):
		if self.wait_spoll(self.spoll_data, tmo):
			return True
		if not fail:
			return False
		self.fail("Timeout waiting for data")
