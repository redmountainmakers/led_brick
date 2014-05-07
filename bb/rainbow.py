#!/usr/bin/python
from time import time, sleep
from math import sin, pi
from PIL import Image, ImageDraw
from colorsys import hsv_to_rgb
import os
if os.access("/dev/spidev1.0", os.R_OK|os.W_OK):
	from LedMatrix_ws2803 import LedMatrix
	#from LedMatrix_n5110 import LedMatrix
else:
	from LedMatrix_pygame import LedMatrix
	#from LedMatrix_ascii import LedMatrix

print "TEST BEGINNING"

SIZE = (29, 6)

hueSpeed = 30.0
hueColSkew = 210.0
hueRowSkewMax = 25.0
hueRowSkewSpeed = 7.0
frameRate = 100.0

lm = LedMatrix(SIZE)

fb = Image.new('RGB', SIZE, (0,0,0))

try:
	refTime = time()
	lastFrameNo = 0
	while True:
		drawTime = time()
		frameTime = drawTime - refTime
		frameNo = int(frameTime * frameRate + 0.5)
		if frameNo - lastFrameNo > 1:
			print "Skipped %d frames" % (frameNo - lastFrameNo)
		lastFrameNo = frameNo

		hueOffset = frameTime * hueSpeed
		for row in range(0, fb.size[1]):
			hueRowSkew = hueRowSkewMax * sin(2*pi*frameTime / hueRowSkewSpeed)
			rowSkew = (row * hueRowSkew / (fb.size[1] - 1.0)) - 0.5
			for col in range(0, fb.size[0]):
				colSkew = col * hueColSkew / (fb.size[0] - 1.0)
				hue = ((hueOffset + colSkew + rowSkew) / 360) % 1.0
				color = ( hsv_to_rgb(hue, 1.0, 1.0) )
				color = tuple(int(v * 255) for v in color)
				fb.putpixel((col, row), color)

		lm.put(fb)
	
		# Limit update speed to frameRate
		nextTime = refTime + (int(frameRate * frameTime) + 1) / frameRate
		frameDelta = nextTime - time()
		if frameDelta > 1e-9:
			sleep(frameDelta)
finally:
	print "TEST ENDING"
	blank = ImageDraw.Draw(fb)
	blank.rectangle((0, 0, SIZE[0], SIZE[1]), fill=(0, 0, 0))
	lm.put(fb)
