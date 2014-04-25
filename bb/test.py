#!/usr/bin/python
from time import time, sleep
from PIL import Image, ImageFont, ImageDraw, ImageChops
#from LedMatrix_ws2803 import LedMatrix
#from LedMatrix_n5110 import LedMatrix
from LedMatrix_ascii import LedMatrix

SIZE = (29, 6)

lm = LedMatrix(SIZE)

fb = Image.new('RGB', SIZE, (0,0,0))
font = ImageFont.load('6by6tall.pil')
draw = ImageDraw.Draw(fb)
draw.text((0,0), 'Hello!', font=font, fill=(255,255,255))

movRate = 10.0 / 1.0 # 5pixels/sec

refTime = time()
lastTime = refTime
while True:
	drawTime = time()
	frameTime = drawTime - refTime
	frameDelta = drawTime - lastTime
	lastTime = drawTime

	mov = int(movRate*frameTime + 0.5) % SIZE[0]
	fr = fb.offset(-mov, 0)
	lm.put(fr)

	# Limit update speed to 100fps
	# To be correct, we should take time again after the draw,
	# but we don't bother to be correct here.
	if frameDelta < 1.0/100:
		sleep(1.0/100 - frameDelta)
