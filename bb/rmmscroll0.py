#!/usr/bin/python
from time import time, sleep
from math import sin, pi, pow, sqrt
from PIL import Image, ImageFont, ImageDraw, ImageChops
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

text = 'RedMountainMakers'
textSpeed = 10.0
frameRate = 100.0
backdropSpeed = 27.0

lm = LedMatrix(SIZE)

fb = Image.new('RGB', SIZE, (0,0,0))
font = ImageFont.load('6by6tall.pil')
textSize = font.getsize(text)
textimg = Image.new('RGB', (textSize[0] + 2, textSize[1]), (0,0,0))
textdraw = ImageDraw.Draw(textimg)
textdraw.text((0, 0), text, font=font, fill=(255, 255, 255))

gradient = np.ndarray(shape=(SIZE[1], SIZE[0], 3), dtype='uint8')
colnorm = 1.0 / (SIZE[0] - 1.0)
rownorm = 1.0 / (SIZE[1] - 1.0)
for row in range(0, SIZE[1]):
	nrow = row * rownorm
	for col in range(0, SIZE[0]):
		ncol = col * colnorm

		color = np.array([1.0, 1.0, 1.0])
		if ncol < 0.15:
			color *= 0.05 + (ncol*0.95/0.15)
		elif ncol >= 0.85:
			color *= 0.05 + ((1.0 - ncol)*0.95/0.15)

		dbc = (max(0, 0.75 - nrow)**2 + (2.0*ncol - 1.0)**2) / (0.75**2 + 1.0**2)
		color -= np.array([0.0, 0.85, 0.85]) * dbc

		gradient[row,col,:] = [ min(255, max(0, int(v * 255))) for v in color ]

gradient = Image.fromstring('RGB', SIZE, gradient.tostring())

backdrop = np.ndarray(shape=(SIZE[1], SIZE[0]*3, 3), dtype='uint8')
for row in range(0, SIZE[1]):
	for col in range(0, SIZE[0]*3):
		rn = random.randrange(0, 64)
		rn2 = random.randrange(0, 128)
		backdrop[row,col,:] = [ 0, rn*rn2/255, rn ]

backdrop = Image.fromstring('RGB', (SIZE[0]*3, SIZE[1]), backdrop.tostring())

try:
	refTime = time()
	lastFrameNo = 0
	while True:
		drawTime = time()
		frameTime = drawTime - refTime
		frameNo = int(frameTime / frameRate)
		if frameNo - lastFrameNo > 1:
			print "Skipped %d frames" % (frameNo - lastFrameNo)
		lastFrameNo = frameNo

		backdropPosition = int((backdropSpeed * frameTime) % backdrop.size[0])
		backdropCrop = backdrop.offset(backdropPosition, 0).crop((0, 0, SIZE[0], SIZE[1]))
		fb.paste(backdropCrop)

		position = int(-(textSpeed * frameTime) % (textSize[0] + 2))
		textCrop = textimg.offset(position, 0).crop((0, 0, SIZE[0], SIZE[1]))
		comp = ImageChops.multiply(textCrop, gradient)
		comp = Image.composite(comp, fb, textCrop.convert('L'))

		lm.put(comp)
	
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
