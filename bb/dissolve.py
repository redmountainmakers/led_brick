#!/usr/bin/python
from time import time, sleep
from math import sin, pi
from PIL import Image, ImageDraw
from colorsys import hsv_to_rgb
import os
import random
if os.access("/dev/spidev1.0", os.R_OK|os.W_OK):
    from LedMatrix_ws2803 import LedMatrix
    #from LedMatrix_n5110 import LedMatrix
else:
    from LedMatrix_pygame import LedMatrix
    #from LedMatrix_ascii import LedMatrix

print "TEST BEGINNING"

SIZE = (29, 6)

pixelDelay = 0.005
colorDelay = 3

dissolveMask = 184 # http://oeis.org/A246866

lm = LedMatrix(SIZE)

fb = Image.new('RGB', SIZE, (0,0,0))

def setPixelAtIndex(i, color):
    row = i / fb.size[0]
    col = i % fb.size[0]
    if row < fb.size[1] and col < fb.size[0]:
        fb.putpixel((col, row), color)
        lm.put(fb)
        return True
    else:
        return False

hue = 0

try:
    while True:
        # Always change the hue by at least 0.25
        hue = (hue + .25 + .5 * random.random()) % 1.0

        color = hsv_to_rgb(hue, 1, 1)
        color = tuple(int(v * 255) for v in color)

        print 'Dissolving to ' + str(color)

        i = 1
        while True:
            if setPixelAtIndex(i, color):
                sleep(pixelDelay)
            if i & 1:
                i = (i >> 1) ^ dissolveMask
            else:
                i = i >> 1
            if i == 1:
                break

        setPixelAtIndex(0, color)

        print 'Dissolve done'

        sleep(colorDelay)

finally:
    print "TEST ENDING"
    blank = ImageDraw.Draw(fb)
    blank.rectangle((0, 0, SIZE[0], SIZE[1]), fill=(0, 0, 0))
    lm.put(fb)
