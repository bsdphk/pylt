#!/usr/local/bin/python

from __future__ import print_function

import sys
import time

import hp6626a
import hp34401a

p=hp6626a.hp6626a(name="gpib1")
print(p.id)
# p.reset()
p.errors()

d=hp34401a.hp34401a(name="gpib0")
print(d.id)

def dvm_volt():
	d.reset()
	d.errors()
	d.wr("CONF:VOLT:DC DEF,MIN")
	d.wr("TRIG:SOUR BUS")

def dvm_amp():
	d.reset()
	d.errors()
	d.wr("CONF:CURR:DC DEF,MIN")
	d.wr("TRIG:SOUR BUS")

def rddvm(n=3):
	d.errors()
	d.wr("INIT")
	d.trigger()
	time.sleep(6)
	a = d.ask("FETC?")
	print(">>> " + a)
	return float(a)

def pwr(s, tmo=1):
	print("#### " + s)
	sys.stdout.flush()
	p.wr(s)
	time.sleep(tmo)
	p.errors()

def pwr_poll():
	t0 = time.time()
	for i in range(300):
		a = p.spoll()
		if a & 0x10:
			print("#### ready", time.time() - t0, a)
			return
		time.sleep(.1)

def pwr_on():
	for i in range(1,5):
		p.wr("OUT %d,1" % i)
	time.sleep(1)

def pwr_off():
	for i in range(1,5):
		p.wr("OUT %d,0" % i)


def cal_volt(chan, vrange):
	dvm_volt()
	d.errors()
	p.errors()
	t0 = time.time()
	print("#--- Calibrating channel %d Voltage Range %g" % (chan, vrange))

	pwr("VRSET %d,%g" % (chan, vrange))
	pwr_on()

	pwr("VLO %d" % chan)
	time.sleep(1)
	vlo = rddvm()
	assert vlo < 0.5

	pwr("VHI %d" % chan)
	time.sleep(1)
	vhi = rddvm()
	assert vhi > vrange

	d.errors()

	pwr("VDATA %d,%.9f,%.9f" % (chan, vlo, vhi))

	pwr("VRLO %d" % chan)
	time.sleep(1)
	vrlo = rddvm();

	pwr("VRHI %d" % chan)
	time.sleep(1)
	vrhi = rddvm();

	d.errors()
	p.errors()

	pwr("VRDAT %d,%.9f,%.9f" % (chan, vrlo, vrhi))

	p.errors()
	d.errors()

	pwr_off()
	print("#--- %gs " % (time.time() - t0))

#######################################################################
def cal_overvoltage(chan, vrange):
	d.errors()
	p.errors()
	t0 = time.time()
	print("#--- Calibrating channel %d Overvoltage Range %g" % (chan, vrange))

	pwr("VRSET %d,%g" % (chan, vrange))
	pwr_on()
	pwr("OVCAL %d" % chan)
	for i in range(100):
		a = p.spoll()
		if a & 0x10:
			break
		print(time.time() - t0, a)
		time.sleep(.1)
	pwr_off()

#######################################################################

def cal_amp(chan, irange):
	dvm_amp()
	d.errors()
	p.errors()
	t0 = time.time()
	print("#--- Calibrating channel %d Ampere Range %g" % (chan, irange))

	pwr("IRSET %d,%g" % (chan, irange))
	pwr_on()

	pwr("ILO %d" % chan)
	time.sleep(1)
	ilo = rddvm()
	assert ilo < 0.5

	pwr("IHI %d" % chan)
	time.sleep(1)
	ihi = rddvm()
	assert ihi > irange

	d.errors()

	pwr("IDATA %d,%.9f,%.9f" % (chan, ilo, ihi))

	pwr("IRLO %d" % chan)
	pwr_poll()
	irlo = rddvm();

	pwr("IRHI %d" % chan)
	pwr_poll()
	irhi = rddvm();

	d.errors()
	p.errors()

	pwr("IRDAT %d,%.9f,%.9f" % (chan, irlo, irhi))

	p.errors()
	d.errors()

	pwr_off()
	print("#--- %gs " % (time.time() - t0))

#######################################################################

def cal_sink(chan, irange):
	dvm_amp()
	d.errors()
	p.errors()
	t0 = time.time()
	print("#--- Calibrating channel %d Ampere Range %g" % (chan, irange))
	if chan & 1:
		ochan = chan + 1
	else:
		ochan = chan - 1

	if ochan > chan:
		pol = -1.0
	else:
		pol = 1.0

	pwr("IRSET %d,%g" % (chan, irange))
	pwr("IRSET %d,%g" % (ochan, irange))
	pwr("ISET %d,%g" % (ochan, 0))
	pwr("VSET %d,%g" % (ochan, 7))

	pwr_on()
	time.sleep(1)

	pwr("IRLN %d" % chan)
	pwr_poll()
	ilo = rddvm() * pol

	pwr("ISET %d,%g" % (ochan, irange))
	time.sleep(1)

	pwr("IRHN %d" % chan)
	pwr_poll()
	ihi = rddvm() * pol

	d.errors()

	pwr("NIDAT %d,%.9f,%.9f" % (chan, ilo, ihi))

	pwr_off()
	print("#--- %gs " % (time.time() - t0))

#######################################################################
def cal_volt_25w(chan):
	cal_volt(chan, 7)
	cal_volt(chan, 50.5)
	cal_overvoltage(chan, 50.5)

def cal_amp_25w(chan):
	cal_amp(chan, .015)
	cal_amp(chan, .5)

def cal_sink_25w(chan):
	cal_sink(chan, .015)
	cal_sink(chan, .5)

#######################################################################
def cal_volt_50w(chan):
	cal_volt(chan, 16)
	cal_volt(chan, 50.5)
	cal_overvoltage(chan, 50.5)

def cal_amp_50w(chan):
	cal_amp(chan, .200)
	cal_amp(chan, 2)

def cal_sink_50w(chan):
	cal_sink(chan, .200)
	cal_sink(chan, 2)

#######################################################################

def calibrate_all():
	pwr_off()
	pwr("CMODE 1")
	if True:
		p.errors()
		for ch in (1,2,3,4):
			print("Connect HP34401A(Voltage) to Channel %d" % ch)
			sys.stdin.readline()
			if ch < 3:
				cal_volt_25w(ch)
			else:
				cal_volt_50w(ch)
	if True:
		p.errors()
		pwr_off()
		for ch in (1,2,3,4):
			print("Connect HP34401A(Current) to Channel %d" % ch)
			sys.stdin.readline()
			if ch < 3:
				cal_amp_25w(ch)
			else:
				cal_amp_50w(ch)

	if True:
		pwr_off()
		print("Connect HP34401A(Current) to Channel 1 + 2")
		print("ch1- <--> ch2-, ch2+ <--> dvm+, ch1+ <--> dvm-")
		sys.stdin.readline()
		cal_sink_25w(1)
		cal_sink_25w(2)

	if True:
		pwr_off()
		print("Connect HP34401A(Current) to Channel 3 + 4")
		print("ch3- <--> ch4-, ch4+ <--> dvm+, ch3+ <--> dvm-")
		sys.stdin.readline()
		cal_sink_50w(3)
		cal_sink_50w(4)

	pwr_off()
	pwr("CMODE 0")
	pwr_poll()
	p.errors()

calibrate_all()
