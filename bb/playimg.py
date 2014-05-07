#!/usr/bin/python
from time import time, sleep
from PIL import Image, ImageDraw
import os
import sys
if os.access("/dev/spidev1.0", os.R_OK|os.W_OK):
	from LedMatrix_ws2803 import LedMatrix
	#from LedMatrix_n5110 import LedMatrix
else:
	from LedMatrix_pygame import LedMatrix
	#from LedMatrix_ascii import LedMatrix

if len(sys.argv) <= 1:
	print "%s <file>" % (sys.argv[0])
	exit(1)

try:
	img = Image.open(sys.argv[1])
except:
	print "Couldn't open %s!" % (sys.argv[1])
	exit(1)

print "TEST BEGINNING"

SIZE = (29, 6)

lm = LedMatrix(SIZE)

fb = Image.new('RGB', SIZE, (0,0,0))

frames = []
try:
	lrSIZE = (img.size[0] * SIZE[1] / img.size[1], SIZE[1])
	tbSIZE = (SIZE[0], img.size[1] * SIZE[0] / img.size[0])
	if lrSIZE[0] > SIZE[0]:
		resizeSize = tbSIZE
		cropBox = (0, (tbSIZE[1] - SIZE[1])/2,
			SIZE[0], (tbSIZE[1] - SIZE[1])/2 + SIZE[1])
	else:
		resizeSize = lrSIZE
		cropBox = ((lrSIZE[0] - SIZE[0])/2, 0,
			(lrSIZE[0] - SIZE[0])/2 + SIZE[0], SIZE[1])

	while True:
		frame = img.convert('RGB').resize(resizeSize, Image.ANTIALIAS)
		frame = frame.crop(cropBox)
		frames.append(frame)
		img.seek(img.tell()+1)
except EOFError:
	img.seek(0)

print "Frames:", len(frames)

frameRate = 1000.0 / img.info['duration'] if 'duration' in img.info and img.info['duration'] > 0 else 10.0
print "frameRate:", frameRate

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

		fb.paste(frames[frameNo % len(frames)])
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
