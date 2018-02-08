
from __future__ import print_function

import sys
import time

import hp3458a
import hp3245a

class hp3245service(object):
	def __init__(self, dvm, dut, chan):
		self.dvm = dvm
		self.dut = dut
		self.chan = chan
		self.term = {
			0:      "Front Out-A",
			1:      "Back Out-A",
			100:    "Front Out-B",
			101:    "Back Out-B",
		}.get(chan)

		if self.term is None:
			print("Wrong channel [0,1,100,101]")
			exit(2)

		self.fo = None
		self.cable = None

	def prompt(self, txt):
		print(txt)
		sys.stdout.flush()
		sys.stdin.readline()

	def cable_voltage(self):
		if self.cable != "voltage":
			self.prompt(self.term + " -> DVM Voltage input")
			self.cable = "voltage"

	def cable_current(self):
		if self.cable != "current":
			self.prompt(self.term + " -> DVM Current input")
			self.cable = "current"

	def dvm_cmds(self, c):
		for i in c:
			self.dvm.wr(i)
			self.dvm.wait_cmd()
			self.dvm.AOK()

	def dut_cmds(self, c, tmo=10000):
		for i in c:
			self.dut.wr(i)
			self.dut.wait_cmd(tmo)
			self.dvm.AOK()

	def dut_rst(self):
		self.dut_cmds(["RESET %d" % self.chan, "USE %d" % self.chan])

	def dvm_rst(self):
		self.dvm.reset()
		self.dvm_cmds(["NPLC 100", "NDIG 8"])

	def dvm_rd(self):
		t0 = time.time()
		self.dvm.wr("T")
		self.dvm.wait_data(tmo=25000)
		a = self.dvm.rd()
		t1 = time.time()
		if t1 - t0 > 15:
			print("DT", t1 - t0)
		return float(a)

	def calibrate(self, calcode=3245):

		self.dut_rst()
		self.dvm.reset()
		self.dvm_cmds(["NPLC 100", "NDIG 8"])
		self.cable_voltage()

		self.dut_cmds(["CAL %d" % calcode])

		for i in range(1,45):
			a = self.dvm_rd()
			print("%2d" % i, "%13.9f" % a)
			self.dut_cmds(["CAL VALUE %.9f" % a])

		i = 45
		self.dvm_cmds(["RANGE 100"])
		a = self.dvm_rd()
		print("%2d" % i, "%13.9f" % a)
		self.dut_cmds(["CAL VALUE %.9f" % a])

		self.dvm_cmds(["RANGE AUTO"])
		for i in (46, 47):
			a = self.dvm_rd()
			print("%2d" % i, "%13.9f" % a)
			self.dut_cmds(["CAL VALUE %.9f" % a])

		self.dvm_cmds(["DCI"])

		self.cable_current()

		for i in range(48, 71):
			a = self.dvm_rd()
			print("%2d" % i, "%13.9f" % a)
			self.dut_cmds(["CAL VALUE %.9f" % a])
		i = 72
		a = self.dvm_rd()
		print("%2d" % i, "%13.9f" % a)
		self.dut_cmds(["CAL VALUE %.9f" % a], tmo=60000)

	def hdr(self, txt):
		print()
		print(txt)
		print("-" * len(txt))
		if not self.fo is None:
			self.fo.write("\n" + txt + "\n")
			self.fo.write("-" * len(txt) + "\n")

	def one_test(self, lo, target, hi, unit, cmds=None):
		if not cmds is None:
			self.dut_cmds(cmds)
		s = ""
		a = self.dvm_rd()
		if a < lo or a > hi:
			t = "FAIL"
		else:
			t = "PASS"
	        s += "[%13.9f" % lo

		if target is None:
			r = "     "
			s += "%13s" % ""
		else:
			r = "%5.1f%%" % (100.0 * (a - target) / (hi - lo))
			s += " %13.9f" % target

	        s += " %13.9f]" % hi

	        s += " %13.9f" % a

		s += " %-3s" % unit

		s += " " + r
		s += " " + t
		
		print(s)
		if not self.fo is None:
			self.fo.write(s + "\n")

	def sym_test(self, target, band, unit, cmds=None):
		self.one_test(target - band, target, target + band, unit, cmds)

	def asym_test(self, app, target, band, unit, goal=None):
		if goal is None:
			goal = target
		self.one_test(goal - band, goal, goal + band, unit,
		    cmds = ["APPLY " + app + " %.6f" % target])

	def operational_verification(self):

		self.fo = open(
		    "_hp3245_operational_verification_%d.txt" % self.chan, "w")

		if True:
			self.op_ver_dcv()

		if True:
			self.op_ver_acv()

		if True:
			self.op_ver_offset()

		if True:
			self.op_ver_flatness()

		self.cable_current()

		if True:
			self.op_ver_dci()

		self.fo.close()
		self.fo = None

	def op_ver_dcv(self):
		self.hdr("DCV Amplitude Accuracy - High Res")
		self.dvm_rst()
		self.dut_rst()
		self.cable_voltage()

		self.dut_cmds(["RANGE 1"])
		self.asym_test("DCV",  1.25, 84e-6, "V")
		self.asym_test("DCV",  0.00, 31e-6, "V")
		self.asym_test("DCV", -1.25, 84e-6, "V")

		self.dut_cmds(["RANGE 10"])
		self.asym_test("DCV",  10.25, 570e-6, "V")
		self.asym_test("DCV",   0.00, 180e-6, "V")
		self.asym_test("DCV", -10.25, 570e-6, "V")

		self.hdr("DCV Amplitude Accuracy - Low Res")
		self.dut_rst()

		self.dut_cmds(["DCRES LOW", "RANGE .15625"])
		self.asym_test("DCV",  .15625, 1.00e-3, "V")
		self.asym_test("DCV",  .00000,  .73e-3, "V")
		self.asym_test("DCV", -.15625, 1.00e-3, "V")

		self.dut_cmds(["RANGE 10"])
		self.asym_test("DCV",  10.0, 54e-3, "V")
		self.asym_test("DCV",   0.0, 37e-3, "V")
		self.asym_test("DCV", -10.0, 54e-3, "V")

		self.hdr("DCV Zero Ohm Output Resistance")
		self.dut_rst()
		self.dvm_cmds(["OHM"])

		self.one_test(0, None, .5, "Ohm")

	def op_ver_dci(self):
		self.hdr("DCI Amplitude Accuracy - High Res")
		self.dut_rst()
		self.dvm_rst()
		self.dvm_cmds(["DCI"])
		self.cable_current()

		self.dut_cmds(["RANGE 0.0001"])
		self.asym_test("DCI",  .0001, 8.5e-9, "A")
		self.asym_test("DCI",  .0000, 3.3e-9, "A")
		self.asym_test("DCI", -.0001, 8.5e-9, "A")

		self.dut_cmds(["RANGE 0.1"])
		self.asym_test("DCI",  .1, 23.3e-6, "A")
		self.asym_test("DCI",  .0,  3.3e-6, "A")
		self.asym_test("DCI", -.1, 23.3e-6, "A")

		self.hdr("DCI Amplitude Accuracy - Low Res")
		self.dut_rst()
		self.dut_cmds(["DCRES LOW", "RANGE 0.0001"])
		self.asym_test("DCI",  .0001, 630e-9, "A")
		self.asym_test("DCI",  .0000, 380e-9, "A")
		self.asym_test("DCI", -.0001, 630e-9, "A")

		self.dut_cmds(["RANGE 0.1"])
		self.asym_test("DCI",  .1,  720e-6, "A")
		self.asym_test("DCI",  .0,  400e-6, "A")
		self.asym_test("DCI", -.1,  720e-6, "A")

	def op_ver_acv(self):
		self.dvm_cmds(["ACV", "ACBAND 1000"])
		self.dut_rst()
		self.dvm_rst()
		self.dvm_cmds(["ACV"])
		self.cable_voltage()

		self.hdr("ACV Amplitude Accuracy - Sine Wave")
		self.dut_cmds(["IMP 50", "APPLY ACV .15625", "RANGE .15625"])
		self.asym_test("ACV",  .15625,  720e-6, "V", .11047)
		self.asym_test("ACV",  .11719,  640e-6, "V", .08282)
		self.asym_test("ACV",  .07813,  560e-6, "V", .05523)

		self.dut_cmds(["ARANGE ON", "APPLY ACV 10", "RANGE 10"])
		self.asym_test("ACV",  10.0,  46e-3, "V", 7.070)
		self.asym_test("ACV",   7.5,  41e-3, "V", 5.303)
		self.asym_test("ACV",   5.0,  36e-3, "V", 3.535)

		self.dut_rst()
		self.hdr("ACV Amplitude Accuracy - Square Wave")
		self.dut_cmds(["IMP 50", "APPLY SQV .15625", "RANGE .15625"])
		self.asym_test("SQV",  .15625,  1.27e-3, "V")
		self.asym_test("SQV",  .11719,  1.15e-3, "V")
		self.asym_test("SQV",  .07813,  1.04e-3, "V")

		self.dut_cmds(["ARANGE ON", "APPLY SQV 10", "RANGE 10"])
		self.asym_test("SQV",  10.0,  81e-3, "V")
		self.asym_test("SQV",   7.5,  74e-3, "V")
		self.asym_test("SQV",   5.0,  67e-3, "V")

		self.dut_rst()


	def op_ver_offset(self):
		self.hdr("Offset Accuracy")
		self.dut_rst()
		self.dvm_rst()
		self.cable_voltage()

		self.dvm_cmds(["DCV"])
		self.dut_cmds(["IMP 50", "APPLY ACV 5", "FREQ 600"])
		self.dut_cmds(["DCOFF -2.5"])
		self.asym_test("ACV",  5.0,  86.5e-3, "V", -5.0)
		self.dut_cmds(["DCOFF 2.5"])
		self.asym_test("ACV",  5.0,  86.5e-3, "V", +5.0)
		self.dut_cmds(["DCOFF 0.0390625"])
		self.asym_test("ACV",  .078125,  1.352e-3, "V", 0.078125)
		self.dut_cmds(["DCOFF -0.0390625"])
		self.asym_test("ACV",  .078125,  1.352e-3, "V", -0.078125)

	def op_ver_flatness(self):
		self.hdr("Flatness")
		self.dut_rst()
		self.dvm_rst()
		self.cable_voltage()

		self.dvm_cmds(["ACDCV"])
		self.dut_cmds(["IMP 50", "APPLY ACV 10", "FREQ 1000"])
		self.asym_test("ACV", 10.0, 54e-3, "V", 7.070)

		self.dvm_cmds(["SMATH 9", "MATH DB"])
		self.dut_cmds(["FREQ 10000"])
		self.asym_test("ACV", 10.0, .07, "dB", 0.0)
		self.dut_cmds(["FREQ 1000000"])
		self.asym_test("ACV", 10.0, 2.0, "dB", 0.0)


if __name__ == "__main__":
	dvm = hp3458a.hp3458a()
	dut = hp3245a.hp3245a()
	for a in sys.argv[1:]:
		if a == "-cal_a":
			hp3245service(dvm, dut, 0).calibrate()
		elif a == "-cal_b":
			hp3245service(dvm, dut, 100).calibrate()
		elif a == "-check_a":
			hp3245service(dvm, dut, 0).operational_verification()
		elif a == "-check_b":
			hp3245service(dvm, dut, 100).operational_verification()
		else:
			print("Unknown argument")
			exit(2)

