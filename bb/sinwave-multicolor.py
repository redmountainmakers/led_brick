#!/usr/bin/python

from time import time, sleep
from PIL import Image, ImageDraw

import math
import os

if os.access("/dev/spidev1.0", os.R_OK|os.W_OK):
	from LedMatrix_ws2803 import LedMatrix
	#from LedMatrix_n5110 import LedMatrix
else:
	from LedMatrix_pygame import LedMatrix
	#from LedMatrix_ascii import LedMatrix

SIZE = (29, 6)

frameRate = 15.0

lm = LedMatrix(SIZE)
fb = Image.new('RGB', SIZE, (0,0,0))

x_steps = 15 # steps for one full wave (in pixels)
y_steps = SIZE[1]
sin_table = [[(0, 0, 0) for y in range(y_steps)] for x in range(x_steps)]

colors = [
	(0, 255, 0),
	(255, 255, 0),
	(255, 0, 0),
	(255, 0, 0),
	(255, 0, 0),
	(255, 0, 0),
	(255, 0, 0)
]

def blend(c1, c2, weight1):
	return (
		int(float(c1[0]) * weight1 + float(c2[0]) * (1 - weight1)),
		int(float(c1[1]) * weight1 + float(c2[1]) * (1 - weight1)),
		int(float(c1[2]) * weight1 + float(c2[2]) * (1 - weight1))
	)

# precalculate all colors along one full sine wave cycle
whatever = 0.5 # seems to work better than epsilon or 1
for x in range(x_steps):
	y = (1 + math.sin(2 * math.pi * x / x_steps)) * (y_steps - whatever) / 2
	y_int = int(y)
	y_frac = y - int(y)
	c = 0
	print 'x=%d y=%f' % (x, y)
	while y_int >= 0:
		sin_table[x][y_int] = blend(colors[c], colors[c + 1], 1 - y_frac)
		c += 1
		y_int -= 1

print "Drawing sine waves"

try:
	refTime = time()
	lastFrameNo = 0
	x_offset = 0

	while True:
		# delta time per frame
		drawTime = time()
		frameTime = drawTime - refTime
		frameNo = int(frameTime * frameRate + 0.5)
		if frameNo - lastFrameNo > 1:
			print "Skipped %d frames" % (frameNo - lastFrameNo)
		lastFrameNo = frameNo

		# draw sine wave
		for row in range(0, SIZE[1]):
			for col in range(0, SIZE[0]):
				fb.putpixel(
					(col, row),
					sin_table[(col + x_offset) % x_steps][SIZE[1] - 1 - row]
				)

		x_offset = (x_offset + 1) % x_steps
					
		# push to frame buffer			
		lm.put(fb)
		
		# Limit update speed to frameRate
		nextTime = refTime + (int(frameRate * frameTime) + 1) / frameRate
		frameDelta = nextTime - time()
		if frameDelta > 1e-9:
			sleep(frameDelta)

finally:
	print "Done drawing sine waves for now :)"
	blank = ImageDraw.Draw(fb)
	blank.rectangle((0, 0, SIZE[0], SIZE[1]), fill=(0, 0, 0))
	lm.put(fb)
