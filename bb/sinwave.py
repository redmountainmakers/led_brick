#!/usr/bin/python
from time import time, sleep
from math import sin, pi
from PIL import Image, ImageDraw
from colorsys import hsv_to_rgb

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

hueSpeed = 30.0
hueColSkew = 210.0
hueRowSkewMax = 25.0
hueRowSkewSpeed = 7.0
frameRate = 60.0

lm = LedMatrix(SIZE)

fb = Image.new('RGB', SIZE, (0,0,0))

#sine wave
fs = 44100  #number of samples along the line, higher numbers give more x,y coordinates
t = np.arange(-0.003, 0.003, 1.0/fs)  #x coordinate or time
f0 = 1000  
phi = np.pi/2
A = .35  # amplitude
x = A * np.sin(2 * np.pi * f0 * t + phi)


 

try:
	refTime = time()
	lastFrameNo = 0
	k=0
	while True:
		#shift sin wave
		if k<=27:
			k+=1
		else:
			k=0
		sinlist = []
		for i, (a, b) in enumerate(zip(t, x)):
			sinlist.append((int(a*10000)+k,int(b*10)+3))
		
		#delta time per frame
		drawTime = time()
		frameTime = drawTime - refTime
		frameNo = int(frameTime * frameRate + 0.5)
		if frameNo - lastFrameNo > 1:
			print "Skipped %d frames" % (frameNo - lastFrameNo)
		lastFrameNo = frameNo

		#clear screen
		for row in range(0, fb.size[1]):
			for col in range(0, fb.size[0]):
				fb.putpixel((col, row), (0, 0, 0))
		#draw wave
		for i in sinlist:
			if int(i[0]) <= 28 and int(i[0]) >= 0 and  int(i[1]) <= 5 and int(i[1]) >= 0:
				fb.putpixel((int(i[0]), int(i[1])), (255, 0, 0))
					
		#push to frame buffer			
		lm.put(fb)
		
		for i in sinlist:
			print i

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
