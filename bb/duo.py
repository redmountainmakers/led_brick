#!/usr/bin/python
from time import time, sleep
from math import sin, pi
from PIL import Image, ImageDraw, ImageFont, ImageChops
from colorsys import hsv_to_rgb
import random
import numpy as np
import os
if os.access("/dev/spidev1.0", os.R_OK|os.W_OK):
	from LedMatrix_ws2803 import LedMatrix
	#from LedMatrix_n5110 import LedMatrix
else:
	from LedMatrix_pygame import LedMatrix
	#from LedMatrix_ascii import LedMatrix

print "TEST BEGINNING"

SIZE = (29, 6)

lm = LedMatrix(SIZE)

fb = Image.new('RGB', SIZE, (0,0,0))

class DemoText:
	text = 'RedMountainMakers'
	textSpeed = 10.0
	backdropSpeed = 27.0

	font = None
	gradient = None
	backdrop = None

	def __init__(self, fb):
		self.font = ImageFont.load('6by6tall.pil')
		self.textSize = self.font.getsize(self.text)
		self.textimg = Image.new('RGB', (self.textSize[0] + 4, self.textSize[1]), (0,0,0))
		textdraw = ImageDraw.Draw(self.textimg)
		textdraw.text((0, 0), self.text, font=self.font, fill=(255, 255, 255))

		gradient = np.ndarray(shape=(fb.size[1], fb.size[0], 3), dtype='uint8')
		colnorm = 1.0 / (fb.size[0] - 1.0)
		rownorm = 1.0 / (fb.size[1] - 1.0)
		for row in range(0, fb.size[1]):
			nrow = row * rownorm
			for col in range(0, fb.size[0]):
				ncol = col * colnorm
	
				color = np.array([1.0, 1.0, 1.0])
				if ncol < 0.15:
					color *= 0.05 + (ncol*0.95/0.15)
				elif ncol >= 0.85:
					color *= 0.05 + ((1.0 - ncol)*0.95/0.15)
	
				dbc = (max(0, 0.75 - nrow)**2 + (2.0*ncol - 1.0)**2) / (0.75**2 + 1.0**2)
				color -= np.array([0.0, 0.85, 0.85]) * dbc
	
				gradient[row,col,:] = [ min(255, max(0, int(v * 255))) for v in color ]
	
		self.gradient = Image.fromstring('RGB', fb.size, gradient.tostring())

		backdrop = np.ndarray(shape=(fb.size[1], fb.size[0]*3, 3), dtype='uint8')
		for row in range(0, fb.size[1]):
			for col in range(0, fb.size[0]*3):
				rn = random.randrange(0, 64)
				rn2 = random.randrange(0, 128)
				backdrop[row,col,:] = [ 0, rn*rn2/255, rn ]

		self.backdrop = Image.fromstring('RGB', (fb.size[0]*3, fb.size[1]), backdrop.tostring())

	def draw(self, fb, frameTime):
		backdropPosition = int((self.backdropSpeed * frameTime) % self.backdrop.size[0])
		backdropCrop = self.backdrop.offset(backdropPosition, 0).crop((0, 0, fb.size[0], fb.size[1]))
		fb.paste(backdropCrop)

		position = int(-(self.textSpeed * frameTime) % (self.textSize[0] + 2))
		textCrop = self.textimg.offset(position, 0).crop((0, 0, fb.size[0], fb.size[1]))
		comp = ImageChops.multiply(textCrop, self.gradient)
		comp = Image.composite(comp, fb, textCrop.convert('L'))
		fb.paste(comp)

class DemoRainbow:
	hueSpeed = 30.0
	hueColSkew = 210.0
	hueRowSkewMax = 25.0
	hueRowSkewSpeed = 7.0

	def __init__(self, fb):
		pass

	def draw(self, fb, frameTime):
		hueOffset = frameTime * self.hueSpeed
		for row in range(0, fb.size[1]):
			hueRowSkew = self.hueRowSkewMax * sin(2*pi*frameTime / self.hueRowSkewSpeed)
			rowSkew = (row * hueRowSkew / (fb.size[1] - 1.0)) - 0.5
			for col in range(0, fb.size[0]):
				colSkew = col * self.hueColSkew / (fb.size[0] - 1.0)
				hue = ((hueOffset + colSkew + rowSkew) / 360) % 1.0
				color = ( hsv_to_rgb(hue, 1.0, 1.0) )
				color = tuple(int(v * 255) for v in color)
				fb.putpixel((col, row), color)

frameRate = 60.0

demo_rainbow = DemoRainbow(fb)
demo_text = DemoText(fb)

try:
	refTime = time()
	lastFrameNo = 0
	while True:
		drawTime = time()
		frameTime = drawTime - refTime
		frameNo = int(frameTime * frameRate)
		if frameNo - lastFrameNo > 1:
			print "Skipped %d frame(s)" % (frameNo - lastFrameNo - 1)
		lastFrameNo = frameNo

		demoSel = int(frameTime / 20)
		demoSel %= 30
		if demoSel == 1:
			demo_text.draw(fb, frameTime)
		else:
			demo_rainbow.draw(fb, frameTime)

		lm.put(fb)
	
		# Limit update speed to frameRate
		nextTime = refTime + (int(frameRate * frameTime) + 1) / frameRate
		frameDelta = nextTime - time()
		if frameDelta > 1e-9:
			sleep(frameDelta)
finally:
	print "TEST ENDING"
	blank = ImageDraw.Draw(fb)
	blank.rectangle((0, 0, fb.size[0], fb.size[1]), fill=(0, 0, 0))
	lm.put(fb)
