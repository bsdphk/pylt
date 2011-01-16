#/usr/local/bin/python
#
# This program collects data on the frequency/amplitude flatness
# of a HP3336C Level Generator relative to a U2004 Power Sensor
#

import u2004a
import hp3336c
import time

g=hp3336c.hp3336c()

m=u2004a.u2004a()


# The amplitude range we want to sweep
amp_lo=	-30.0
amp_hi=	+7.0
amp_step= 3.0

# Frequency range to sweep, (log spacing)
freq_lo = 9e3
freq_hi = 21e6
freq_step = 2.0

# The file we dump data to, in addition to stdout
f = open("_", "w")

# Sweep amplitude
amp = amp_lo
while amp < amp_hi:

	# Set the generator amplitude and let it settle for 10 seconds
	g.set_dbm(amp)
	time.sleep(10)

	
	# Sweep frequency
	freq = freq_lo
	while freq < freq_hi:

		# Set generator frequency
		g.set_freq(freq)

		# Tell the power sensor what to expect
		m.config(freq, amp, 4)

		# Settle for a second
		time.sleep(1)

		# Do measurement (can take up to 35-40 sec)
		x = m.measure()

		# Write result to data file
		f.write("%e %e %e %e\n" % (freq, amp, x, x-amp))
		f.flush()
		print("%12.1f %7.3f %7.3f %7.3f" % (freq, amp, x, x-amp))

		freq *= freq_step

	f.write("\n")

	amp += amp_step

f.close()
