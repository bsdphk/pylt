#/usr/local/bin/python
#
# A rudimentary pen plotter which outputs SVG files
#

class plotter():

	def __init__(self, fname="_.svg"):

		self.width = "6in"
		self.height = "4.5in"
		self.bbox_coord = None
		self.bgcolor = None
		self.__pencolor = "black"
		self.__penwidth = 3
		self.__started = False
		self.__up = True

		self.fo = open(fname, "w")
		self.fo.write('<?xml version="1.0" standalone="no"?>\n')
		self.fo.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"\n')
		self.fo.write('\t"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')

	def size(self, width, height):
		self.width = width
		self.height = height

	def bbox(self, x0, y0, x1, y1):
		self.bbox_coord = (x0,y0,x1,y1)

	def background(self, col):
		self.bgcolor = col

	def __setpen(self, first):
		self.__break()
		if not first:
			self.fo.write("</g>")
		self.fo.write('<g stroke-width="%.1f" stroke="%s">\n' %
		    (self.__penwidth, self.__pencolor))

	def __bbox(self, x, y):
		if x > self.x1:
			self.x1 = x
		if x < self.x0:
			self.x0 = x
		if y > self.y1:
			self.y1 = y
		if y < self.y0:
			self.y0 = y

	def __break(self):
		if not self.__up:
			self.fo.write('\t"/>\n')
			self.__up = True

	def start(self):
	
		self.fo.write('<svg version="1.1"\n')
		if self.bbox_coord != None:
			self.fo.write(
			    '\tviewBox="%.1f %.1f %.1f %.1f"\n' %
			    self.bbox_coord)
		if self.width != None:
			self.fo.write('\twidth="%s" height="%s"\n' %
			    (self.width, self.height))
		self.fo.write('\txmlns="http://www.w3.org/2000/svg">\n')

		if self.bgcolor != None:
			self.fo.write(
			    '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>\n' % (
			    self.bbox_coord[0],
			    self.bbox_coord[1],
			    self.bbox_coord[2] - self.bbox_coord[0],
			    self.bbox_coord[3] - self.bbox_coord[1],
			    self.bgcolor))

		self.fo.write('<g stroke-linecap="round"\n')
		self.fo.write('\t stroke-linejoin="round" fill="none">\n')
		self.__setpen(True)

		self.x = 0
		self.y = 0
		self.x0 = 999999
		self.y0 = 999999
		self.x1 = -999999
		self.y1 = -999999

	def pencolor(self, pencolor):
		if pencolor == self.__pencolor:
			return
		self.__pencolor = pencolor
		self.__setpen(False)

	def penwidth(self, penwidth):
		if penwidth == self.__penwidth:
			return
		self.__penwidth = penwidth
		self.__setpen(False)

	def comment(self, c):
		self.__break()
		self.fo.write("<!-- %s -->\n" % c)

	def vector(self, x, y, draw):
		if self.x == x and self.y == y:
			self.x = self.x - .1
			self.y = self.y - .1
		# The +.01 is to work around a bug in FireFox (seen in 3.5.16)
		if draw and self.__up:
			self.fo.write('<polyline points="%.2f,%.1f' %
			    (self.x + .01, self.y))
			self.__up = False
		if draw:
			self.fo.write('\n\t%.1f,%.1f' % (x, y))
		else:
			self.__break()
		self.x = x
		self.y = y
		self.__bbox(x, y)

	def stop(self):
		self.__break()
		self.fo.write("</g>\n")
		self.fo.write("</g>\n")
		self.fo.write("</svg>\n")
		self.fo.close()
		self.fo = None

	def report_bbox(self):
		return(self.x0,self.y0,self.x1,self.y1)

if __name__ == "__main__":
	p = plotter()
	p.start()
	p.vector(0,0, False)
	p.vector(100,100, True)
	p.vector(10,100, True)
	p.stop()
