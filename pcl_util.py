#/usr/local/bin/python

import array

#######################################################################
# Helper function for hp5372a class
#
# Convert a HP-PCL string from a HP5372A to a PBM file
#

def pcl_to_pbm(data, ofile="_.hp5372a.pbm"):
	a = array.array('B', data)
	l = len(a)

	# First pass, find out how tall and how wide this is
	# and split into raster lines
	h = list()
	for i in range(0,8):
		h.append(array.array('B', (0,0)))
	w = 0
	i = 0
	while i < l:
		if a[i] == 0:
			#print("NUL")
			i += 1
			continue
		if a[i] == 12:
			break
		

		# We deal with escape sequences, so insist we have one
		if a[i] != 27:
			print(a[i:i+10])
			break
		if i + 1 < l and a[i + 1] == 27:
			i += 1
			continue

		if a[i + 1] != 42:
			break

		assert a[i+1] == 42
		c = a[i+2]
		n = 0
		i += 3
		while a[i] >= 48 and a[i] <= 57:
			n *= 10
			n += a[i] - 48
			i += 1
		t = a[i]
		i += 1
		if c == 114 and t == 65:
			# "ESC * r # A"  = Start Raster Graphics
			pass;
		elif c == 114 and t == 66:
			# "ESC * r # B"  = End Raster Graphics
			pass;
		elif c == 114 and t == 83:
			# "ESC * r # S"  = Width of Raster Graphics
			pass;
		elif c == 116 and t == 82:
			# "ESC * t # R"  = Set Resolution
			pass;
		elif c == 98 and t == 87:
			# 'ESC * b # W" = Transfer Raster Data
			p = a[i: i + n]
			assert len(p) == n
			h.append(p)
			i += n
			if n > w:
				w = n
		else:
			print("Unknown: ESC * %c(%d) %d %c(%d)" % (c, c, n, t, t))
			break
			
	for i in range(0,8):
		h.append(array.array('B', (0,0)))

	fo = open(ofile, 'w')
	fo.write("P4\n%d %d\n" % (16 + w * 8, len(h)))
	for i in h:
		fo.write("%c" % 0x00)
		for j in i:
			fo.write("%c" % j)
		for k in range (len(i),w):
			fo.write("%c" % 0x00)
		fo.write("%c" % 0x00)
	fo.close()

#f = open("_x")
#a=f.read()
#f.close()
#pcl_to_pbm(a, "_tds540.pbm")
