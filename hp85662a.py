#!/usr/local/bin/python
#
# This file contains code which will render a memory dump from the HP85662A 
# video processor, the top part of a HP8566 or HP8568 spectrum analyzer, onto
# a pen-plotter class, such as svg.py
#
# The output is as precise a rendering as possible of what you see on the
# CRT, including graphics/text added with display programming commands.
#
# The easiest way to see the difference, is to press:
#
#	INSTR PRESET
#	SHIFT VIDEO BW {G}
#	SHIFT LINE {w}
#
# Rev 2714 has neat little bug here, but bug or no bug, the PLOT function
# will not show you the calibration constants, whereas this code will show
# them, as text or graphics, whatever your kit does.
#
# There is a large number of tweakables, both for the precise alignment
# of your display processor and for how you want the output to look.
#
# Usage is:
#	# Get a memory dump
#	d = hp8568b.hp8568b()
#	x = d.screen_memory()
#	# Create a plotter instance
#	p = svg_plotter.plotter("/usr/local/www/data/_.svg")
#	# Create a renderer
#	r = render()
#	# Set options, these are like a photo...
#	r.geom["color-background"] = "black"
#	r.geom["color-normal"] = "green"
#	# Tada!
#	r.render(x, p);
#

import sys

#######################################################################
# I belive this is what the HP85662A video-processor character-ROM
# contains. I have zero-filled where no information was available.
#

if sys.version_info < (3,0):
	fx=unicode
else:
	fx=lambda x: x

charrom = bytearray.fromhex(fx("""
0000000000000000 2e17c75e47000000 1d4d6cb63e360000 26476a894d000000
0c1e4e5c00000000 2e0d000000000000 5c4e2e0d00000000 4626070000000000
0000000000000000 1e3e5d0000000000 0000000000000000 0000000000000000
0000000000000000 0000000000000000 0000000000000000 0000000000000000
0c1e4e5c4a000000 0000000000000000 0000000000000000 0000000000000000
3b00000000000000 ba2b000000000000 0d00000000000000 69574c2b28480000
0600000000000000 4a6846060e4e0000 0666060000000000 8d3e6d0000000000
060e000000000000 0de76db965000000 0a4a660000000000 3607000000000000
0000000000000000 b636b83e38000000 ad2fcf4d00000000 8969098c6c0c9701
882757694a2a0b02 965e169d1dd75700 8d660d2e4d090703 ad3f000000000000
c5282c4f00000000 a5484c2f00000000 886c8c68b63e0000 8a6a0ab73d370000
a73613a637000000 8a6a0a0000000000 a736b72600000000 865e060000000000
974ddc5846160804 9d3e363e96560000 865606194a5c4e05 872646584a2aca06
c64e0868084e4600 8e5e0e0b3b5a5807 8a4a584616080c09 965e0e5e16000000
9a4a584616081a10 da1a0c1e4e5c5807 a637b627ba2baa14 a73613a637bb2a15
e60a6e0a66000000 8868088b6b0b0000 866a0e6a06000000 b636b83a6b6d3e16
c626080c2e4e6c17 985818863e663e18 c6060e4e6c4a0a19 870d073667ed3e16
8e0646686c4e0e18 8a5a0a860e6e0e1a 8a5a0a860e6e0e18 ca6a6736070d071b
e66e66ea0a6a8e1c 9656b63e369e5e00 881646585e580000 e62a66de095e8e1c
860e065606000000 8e386e666e380e1c 860e666e660e0600 e76d6736070d071b
8e060e5e6c5a0a00 870d0736676d3e1d de0e060e5e6c5a1e ed3e0d0b4a69671f
8e6e0ebe363e0000 870e0736676e6700 b60e366e36000000 8e163c566e563c7f
866e068e660e0000 8e3a6e3a363a0e00 8e6e0666066e0e00 c5252f25af4f0000
9e561e0000000000 a5454f45cf2f0000 8b2e262e4b000000 8262020000000000
bf4d000000000000 d736161859d65a80 961e169736575a80 da3b1a1736570000
d65e56d736171a81 99594b2b19173682 ac262c3e5e9b4b00 d45b543314da3b83
961e169a3b5a5600 bb363bbe3e000000 9434464b46ce4e00 961e16984bb95600
b63e360000000000 860b8a2b39b63a84 961b9a3b5a560000 971a3b5a57361700
931b139736575a80 d35b53d736171a81 961b9a3b5a000000 da3b1a571ad73685
b63e36569b5b0000 9b173657d65b0000 9b365b0000000000 8b163b566b000000
965b169b561b0000 9b361bb65b362300 9b5b1656165b1b00 d535391a3b3f5f00
b33f330000000000 9535395a3b3f1f00 9e2f4e5f00000000 160e000000000000
3b1a000000000000 3b5a000000000000 5700000000000000 1a17365700000000
5b69660000000000 1700000000000000 6808000000000000 4e5c8a3a00000000
4b6c000000000000 58373d37180a0000 c6584a1d2f4f5d00 6a0a000000000000
3500000000000000 1534550000000000 5a00000000000000 493b1c0a00000000
4d1e000000000000 0000000000000000 0000000000000000 0000000000000000
0000000000000000 565ec66686260000 b63e36ae4e000000 6b6937090b3d0000
c34d000000000000 476b000000000000 1aca584616080000 1c2e4d0000000000
2ebc5c0000000000 5bd8660000000000 2618995900000000 4cac1e9949000000
863e663e06000000 9f3d5f0000000000 9f1fdf5f00000000 955e158b6b0b8886
e7462706181c2e87 e8493b1c0a183988 8a1c3d5c6a0a6a89 bf3f000000000000
8a6a0a3c0a380000 ea0a6a386a3c0000 95234355281a2c8a 866606b73d378a8b
99363e3659000000 8f6f0f0000000000 aa3bab3a00000000 8a6a0ab737bd3d00
8604234446270600 a327000000000000 8627460343000000 87474303a5450000
8d2dcb4f00000000 8e2f4e0b4b000000 8b4b4f0fad4d0000 8a2a356f00000000
892b496b00000000 8868088a2c4a6c00 a62e26c64e460000 9616bb3bd6560000
8b6e0b680b866618 8c6c0c8a6a0a8886 eb086b0e6b866618 9d3f5d0000000000
8666066e06000000 832743b414000000 ee5f4e9524354e8c d837181b3c5bbe8c
8e6e360e366e0e00 b937000000000000 a606000000000000 92315258d738178d
b55e35ca7a657a00 a326a72700000000 6a46660000000000 ee0e4a0666000000
8703330000000000 8f0b8e2f4e4b0000 8307862746430000 ab0c0e2f4e4c2b00
aa012a5a4515c58e 8a18394b6c7a688f 8703862746000000 8423440627460000
a327874700000000 cb2a182646585a90 8723470000000000 c626b63b00000000
8545058f4f0f0000 810501c145410000 1ad95bee0e6e0000 961e168e6e0ede95
8a5adc5846160804 8d0a396a6da64696 a646b63eae4ebd97 2000000000000000
8a2b283656686b98 e6484a2b0a072699 8c030c1e4e5c4a9a 8b2b4564945b0000
bb1a1736575a3b9b 9949db3c1b173682 b33dda5736171a81 8a2b4643c66b0000
961b9a3b5a530000 c7262b2600000000 94335436282a3c9c 961b994ba9560000
963b9e3c563c0000 931b13982646589d 8a2b36595b000000 971a3b5a57361700
a62b8a2b6bcb4600 981a2c4c5a58469e a3151a3b5a573685 ec3b1a1736575a14
8a2b6bbb363b0000 8a2b283656686b00 a4444626181a2c9f 9b08163756685bc5
ee0e6e6c9e161ec6 863e6606663e0600 86260a0c2e4e6cca e866064a0e6e6ccb
c666d63e163e56c6 8b0d2e3b4e6d6bd7 866606991b9a5ada 2000000000000000
""".replace("\n", "")))

#######################################################################
# Function to render a given character from the charrom above.
#
def render_char(x0, y0, char, vfunc):
	p = char * 8
	while True:
		assert p < len(charrom)
		v = charrom[p]
		if v == 0:
			return
		if p & 7 == 7:
			p = v * 8
			continue
		y = y0 + 2 * (v & 0xf)
		x = x0 + 2 * ((v >> 4) & 0x7)
		l = v >> 7
		vfunc(x, y, l == 0)
		p += 1

###########################################################################

class render():
	def __init__(self, dbg_file = None):
		self.dbg_file = dbg_file
		self.geom = {
			"ratio-d2": 1.13,
			"ratio-d3": 1.68,
			"ratio-bex": 1.55,
			"d1-x-offset": 136,
			"d1-y-offset": 83,
			"margin": 20,
			"aspect": 1.3,
			"color-normal": "black",
			"color-dim": "blue",
			"color-bright": "red",
			"color-background": "white",
			"penwidth": 3,
		}

	def v(self,x,y, draw):
		x &= 0x3ff
		y &= 0x3ff
		if not self.dummy_pass:
			self.plt.vector(
			     self.geom["margin"] +
			     self.geom["aspect"] * (self.rt * x + self.x0),
			     self.geom["margin"] +
			     self.ym - (self.rt * y + self.y0),
			     draw)
		self.x = x
		self.y = y

	def graph(self, d):
		if d <= 1023:
			if self.thr > d:
				d = self.thr
			self.v(self.x + 1, d, True)
		elif d <= 3072:
			if self.thr != 0:
				self.v(self.x + 1, self.thr, True)
			else:
				self.v(self.x + 1, 0, False)
		else:
			self.v(self.x + 1, 0, False)
		return "grp %d" % d

	def label(self, d):
		d &= 0xff
		if not self.dummy_pass:
			self.plt.comment("char 0x%02x" % d)
		if d == 0:
			return "lbl NUL"
		if d == 8:
			self.v(self.x - 16, self.y, False);
			return "lbl bs"
		if d == 10:
			self.v(self.x, self.y - 32, False);
			return "lbl nl"
		if d == 13:
			self.v(0, self.y, False);
			return "lbl cr"
		if d == 17:
			return "lbl -blink"
		if d == 18:
			return "lbl +blink"
		if d == 32:
			self.v(self.x + 16, self.y, False);
			return "lbl sp"
		if d == 145:
			self.nxtadr = (self.adr + 16) & 0xff0
			return "lbl sk16"
		if d == 146:
			self.nxtadr = (self.adr + 32) & 0xfe0
			return "lbl sk32"
		if d == 147:
			self.nxtadr = (self.adr + 64) & 0xfc0
			return "lbl sk64"
		self.y &= 0x3e0
		self.x &= 0x3f0
		render_char(self.x & ~0x0f, self.y & ~0x1f, d, self.v)
		self.y &= 0x3e0
		self.x &= 0x3f0
		self.x += 16
		if d > 32 and d <= 126:
			return "lbl '%c'" % d
		else:
			return "lbl 0x%03x" % d

	def vector(self, d):
		x = d
		y = self.ram[self.adr + 1]
		self.nxtadr = self.adr + 2
		r = x & 0x800
		x &= 0x3ff
		p = y & 0x800
		y &= 0x3ff
		if r != 0:
			x = (self.x + x) & 0x3ff
			y = (self.y + y) & 0x3ff
		self.v(x, y, p == 0)
		xx = "vec %d,%d" % (x, y)
		if p == 0:
			xx += " up"
		if r != 0:
			xx += " rel"
		return xx

	def progctl(self, d):
		d &= ~0x403
		x = "prg"
		if (d & 0x0c8) == 0x000:
			# skip to next control
			self.nxtadr = self.adr + 1
			x += " skc"

		elif (d & 0x0c8) == 0x008:
			# jmp
			d &= ~0x008
			self.nxtadr = self.ram[self.adr + 1]
			x += " jmp(%03x)" % self.nxtadr 

		elif (d & 0x0c8) == 0x048:
			# dsz
			d &= ~0x048
			self.counter -= 1
			if self.counter == 0:
				self.nxtadr = self.adr + 2
			x += " dsz(%d)" % self.counter

		elif (d & 0x0c8) == 0x088:
			# jsr
			d &= ~0x088
			s = self.ram[self.adr + 1]
			x += " jsr(%03x)" % s
			self.retadr = self.adr + 2
			self.nxtadr = s
		elif (d & 0x0c8) == 0x0c8:
			# rtn
			d &= ~0x0c8
			self.nxtadr = self.retadr
			x += " rtn(%03x)" % self.nxtadr
			
		if d != 0:
			x += " ??? %03x" % d
		self.skipctl = True
		return x

	def dispctl(self, d):
		d &= ~0x400
		x = "dsp"
		if d & 3 == 0:
			self.state = self.graph
			x += " grp"
		elif d & 3 == 1:
			self.state = self.label
			x += " lbl"
		elif d & 3 == 2:
			self.state = self.vector
			x += " vec"
		d &= ~0x003

		if d & 0x04:
			d &= ~0x004
			self.stop = True
			x += " end"

		if d & 0x080 == 0x080:
			d &= ~0x088
			if not self.dummy_pass:
				self.plt.pencolor(self.geom["color-bright"])
			x += " bright"
		elif d & 0x008 == 0x008:
			d &= ~0x088
			if not self.dummy_pass:
				self.plt.pencolor(self.geom["color-dim"])
			x += " dim"
		else:
			if not self.dummy_pass:
				self.plt.pencolor(self.geom["color-normal"])
			
		if d & 0x10:
			d &= ~0x010
			self.v(0, self.y, False)
			x += " clrx"
			
		if d & 0x20:
			d &= ~0x020
			self.nxtadr = self.adr + 0x400
			self.nxtadr &= 0xc00
			x += " skp"

		if (d & 0x140) == 0x000:
			self.rt = 1.0
		elif (d & 0x140) == 0x040:
			self.rt = self.geom["ratio-d2"]
		elif (d & 0x140) == 0x100:
			self.rt = self.geom["ratio-bex"]
		elif (d & 0x140) == 0x140:
			self.rt = self.geom["ratio-d3"]
		if d & 0x40:
			self.x0 = 0
			self.y0 = 0
		else:
			self.x0 = self.geom["d1-x-offset"]
			self.y0 = self.geom["d1-y-offset"]
		d &= ~0x140
			
		if d != 0:
			x += " ??? %03x" % d
		return x

	def count(self, d):
		self.counter = d & 0xff
		if d & 0x100:
			self.thr = 0;
		else:
			self.thr = self.counter * 4
		return "cnt (%d) thr (%d)" % (self.counter, self.thr)

	def render(self, ram, plt):
		self.plt = plt;
		self.ram = ram

		self.ym = 1023. * self.geom["ratio-d2"]
		margin = 2 * self.geom["margin"]

		self.plt.bbox(
			0,
			0,
			margin + self.geom["aspect"] * self.ym,
			margin + self.ym,
		)
		self.plt.background(self.geom["color-background"])


		self.plt.start()

		self.plt.penwidth(self.geom["penwidth"])

		self.retadr = 0
		self.counter = 0
		self.thr = 0
		self.x0 = 0
		self.y0 = 0

		self.dummy_pass = False

		# The counter/threshold register is loaded late in the
		# default program, so we have run though it twice in order
		# to have the expected value at the start of the second pass

		for self.dummy_pass in (True, False):
			self.dispctl(0x400)
			self.v(0,0, False)
			self.adr = 0
			self.stop = False
			self.skipctl = False
			while True:
				d = self.ram[self.adr]
				self.nxtadr = self.adr + 1

				if (d & 0xc00) != 0x400:
					if self.skipctl:
						xpl = "skipctl"
					else:
						xpl = self.state(d)
				else:
					self.skipctl = False
					if (d & 0x203) == 0x003:
						xpl = self.progctl(d)
					elif (d & 0x200) == 0x000:
						xpl = self.dispctl(d)
					else:
						xpl = self.count(d)

				self.adr = self.nxtadr & 0xfff

				if xpl != "" and self.dbg_file != None:
					self.dbg_file.write(
					    ("0x%03x 0x%03x [%03x, %03x]" +
					    " >%03x %s\n") %
					    (self.adr, d, self.x, self.y,
					    self.nxtadr, xpl))
				if xpl.find("??") != -1:
					break
				if self.stop:
					break;
				
		self.plt.stop()


if __name__ == "__main__":

	import array
	import hp8568b
	import svg_plotter

	if False:
		f = open("_.hp8568b.testimg.mem", 'rb')
		x = array.array("H")
		x.fromfile(f, 4096)
		f.close()
	else:
		d = hp8568b.hp8568b()
		x = d.screen_memory()
		#f = open("_.hp8568b.testimg.mem", 'wb')
		#x.tofile(f)
		#f.close()

	p = svg_plotter.plotter("_.svg")
	r = render()
	r.render(x, p);
