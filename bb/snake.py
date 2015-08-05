#!/usr/bin/python
from time import time, sleep
from math import sin, pi
from PIL import Image, ImageDraw
from colorsys import hsv_to_rgb
import random
import os

import sys
import termios
import fcntl

if os.environ.get('PYGAME') is None and os.access("/dev/spidev1.0", os.R_OK|os.W_OK):
	from LedMatrix_ws2803 import LedMatrix
	#from LedMatrix_n5110 import LedMatrix
else:
	from LedMatrix_pygame import LedMatrix
	#from LedMatrix_ascii import LedMatrix

print "TEST BEGINNING"

def getch():
  fd = sys.stdin.fileno()

  oldterm = termios.tcgetattr(fd)
  newattr = termios.tcgetattr(fd)
  newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
  termios.tcsetattr(fd, termios.TCSANOW, newattr)

  oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
  fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

  try:        
    while 1:            
      try:
        c = sys.stdin.read(1)
        break
      except IOError: pass
  finally:
    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
  return c

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

SIZE = (29, 6)

hueSpeed = 30.0
hueColSkew = 210.0
hueRowSkewMax = 25.0
hueRowSkewSpeed = 7.0
frameRate = 10.0

lm = LedMatrix(SIZE)

fb = Image.new('RGB', SIZE, (0,0,0))




stickPos = {
		"x":0, 
		"y":0
}

playerPos = {
		"x":3,
		"y":3
}
pHist = [(0, 0)]

pLength = 1

Direction = enum(UP=1, DOWN=2, LEFT=3, RIGHT=4)

moveDirec = 2

def placeStick ():
	#global pHist
	#good = True




	buttx = random.randint(0, 28)
	butty = random.randint(0, 5)

	stickPos["x"] = buttx
	stickPos["y"] = butty


	"""for (x, y) in pHist:
		if ((x == buttx) and (y == butty)):
			good = False
			break
	if good:
		stickPos["x"] = buttx
		stickPos["y"] = butty
	else:
		placeStick()"""

"""def checkFront(direc):
	global pHist
	global moveDirec
	if  moveDirec == Direction.UP:
		for (y, x) in pHist:
			if ((x <> playerPos["x"]) or (y <> playerPos["y"]-1)):
				return True
			elif ((-1  <> playerPos["y"]-1) or (6 <> playerPos["y"])):
 				return False
			else:
				return True
	if  moveDirec == Direction.DOWN:
		for (y, x) in pHist:
			if ((x <> playerPos["x"]) or (y <> playerPos["y"]+1)):
				return True
			elif ((-1  <> playerPos["y"]-1) or (6 <> playerPos["y"])):
				return False
			else:
				return True

	if  moveDirec == Direction.LEFT:
		for (y, x) in pHist:
			if ((x <> playerPos["x"]-1) or (y <> playerPos["y"])):
				return True
			elif ((-1  <> playerPos["x"]-1) or (29 <> playerPos["x"])):
				return False
			else:
				return True

	if  moveDirec == Direction.RIGHT:
		for (y, x) in pHist:
			if ((x <> playerPos["x"]+1) or (y <> playerPos["y"])):
				return True
			elif ((-1  <> playerPos["x"]-1) or (29 <> playerPos["x"])):
				return False
			else:
				return True"""


def checkPos(pos):
	print "current position: [%s, %s]" %(playerPos["x"], playerPos["y"])
	print "checking: " + str(pos)
	for (y, x) in pHist:
		if (y, x) == pos:
			return False
	if pos[0] < 0 or pos[0] > 5 or pos[1] < 0 or pos[1] > 28:
		return False
	else:
		return True
		


def moveDec():
	global pHist
	global moveDirec
	global pLength
	poss = []

	up = (playerPos["y"]-1, playerPos["x"])
	poss.append(up)
	down = (playerPos["y"]+1, playerPos["x"])
	poss.append(down)
	right = (playerPos["y"], playerPos["x"]+1)
	poss.append(right) 
	left = (playerPos["y"], playerPos["x"]-1)
	poss.append(left)
	#print str(moveDirec)
	
		
	
	dMov = False

	if moveDirec == Direction.UP:
		print checkPos(up)
		if checkPos(up):
			moveUpdate()
			dMov = True
	elif moveDirec == Direction.DOWN:
		print checkPos(down)
		if checkPos(down):
			moveUpdate()
			dMov = True
	elif moveDirec == Direction.LEFT:
		print checkPos(left)
		if checkPos(left):
			moveUpdate()
			dMov = True
	elif moveDirec == Direction.RIGHT:
		print checkPos(right)
		if checkPos(right):
			moveUpdate()
			dMov = True


	if not dMov:
		#if  moveDirec == Direction.LEFT or moveDirec == Direction.RIGHT:
 		if not dMov:
			for x, y in enumerate(poss):
				if checkPos(y):
					if x == 0:
						moveDirec = Direction.UP
						moveUpdate()
						dMov = True
					elif x == 2:
						moveDirec = Direction.RIGHT
						moveUpdate()
						dMov = True
					elif x == 1:					
						moveDirec = Direction.DOWN
						moveUpdate()
						dMov = True
					elif x == 3:
						moveDirec = Direction.LEFT
						moveUpdate()
						dMov = True


		if not dMov:
			pLength = 1
			pHist = pHist[0:pLength]
			playerPos["x"] = random.randint(0, 28) 
			playerPos["y"] = random.randint(0, 5)



def moveUpdate():
		global pHist
		if  moveDirec == Direction.RIGHT:
			pHist.insert(0, (playerPos["y"], playerPos["x"]))
			pHist = pHist[0:pLength]
			playerPos["x"] += 1
		elif  moveDirec == Direction.LEFT:
			pHist.insert(0, (playerPos["y"], playerPos["x"]))
			pHist = pHist[0:pLength]
			playerPos["x"] -= 1
		elif  moveDirec == Direction.UP:
			pHist.insert(0, (playerPos["y"], playerPos["x"]))
			pHist = pHist[0:pLength]
			playerPos["y"] -= 1
		elif  moveDirec == Direction.DOWN:
			pHist.insert(0, (playerPos["y"], playerPos["x"]))
			pHist = pHist[0:pLength]
			playerPos["y"] += 1
		



try:
	refTime = time()
	lastFrameNo = 0
	#frameTime = 0
	#hueOffset = 0
	mover = 0
	rowCount = 0

	moveDec()

	while True:
		drawTime = time()
		frameTime = drawTime - refTime
		frameNo = int(frameTime * frameRate + 0.5)
		if frameNo - lastFrameNo > 1:
			print "Skipped %d frames" % (frameNo - lastFrameNo)
		lastFrameNo = frameNo

		hueOffset = frameTime * hueSpeed
		for row in range(0, fb.size[1]):
			#hueRowSkew = hueRowSkewMax * sin(2*pi*frameTime / hueRowSkewSpeed)
			#rowSkew = (row * hueRowSkew / (fb.size[1] - 1.0)) - 0.5


			for col in range(0, fb.size[0]):
				#colSkew = col * hueColSkew / (fb.size[0] - 0.0)
				#hue = ((hueOffset + colSkew + rowSkew) / 360) % 1.0
				#color = ( hsv_to_rgb(hue, 1.0, 1.0) )
				#color = tuple(int(v * 255) for v in color)
				if (col == stickPos["x"]) and (row == stickPos["y"]):
					color = (255, 0, 0)
					fb.putpixel((col, row), color)
				elif(col == playerPos["x"]) and (row == playerPos["y"]):
					color = (0, 0, 255)
					fb.putpixel((col, row), color)
				else: 
					color = (0, 0, 0)
					fb.putpixel((col, row), color)
		for (y, x) in pHist:
			color = (0, 255, 0)
			#print str(i)
			if ((x <> stickPos["x"]) or (y <> stickPos["y"])) and  ((x <> playerPos["x"]) or (y <> playerPos["y"])):
				fb.putpixel((x, y), color)
				
		#print stickPos


		"""		
		if (mover <= 28):
			mover+=1
		else:
			mover=0
		if (rowCount == 5) and (mover == 28):
			rowCount=0
		elif(mover == 28):
			rowCount+=1
		else: 
			print "something went wrong"			
		"""

		lm.put(fb) #draw to screen
		
		if (playerPos["x"] == stickPos["x"]) and (playerPos["y"] == stickPos["y"]): #check for collision between player and stick
			placeStick()
			pLength += 1
		if (playerPos["x"] < stickPos["x"]):
			
			moveDirec = Direction.RIGHT
			moveDec()
			#pHist.insert(0, (playerPos["y"], playerPos["x"]))
			#pHist = pHist[0:pLength]
			#playerPos["x"] += 1
			
		elif (playerPos["y"] < stickPos["y"]):
			#pHist.insert(0, (playerPos["y"], playerPos["x"]))
			#pHist = pHist[0:pLength]
			#playerPos["y"] += 1
			moveDirec = Direction.DOWN
			moveDec()

		elif (playerPos["x"] > stickPos["x"]):
			#pHist.insert(0, (playerPos["y"], playerPos["x"]))
			#pHist = pHist[0:pLength]
			#playerPos["x"] -=1
			moveDirec = Direction.LEFT
			moveDec()
			
		elif (playerPos["y"] > stickPos["y"]): 
			#pHist.insert(0, (playerPos["y"], playerPos["x"]))
			#pHist = pHist[0:pLength]
			#playerPos["y"] -=1
			moveDirec = Direction.UP
			moveDec()

		print "moveDirec " + str(moveDirec)
		print "pLength " + str(pLength)

	
		"""move = getch()   #player movement
		if move == "w":
			playerPos["y"] -= 1
		elif move == "a":
			playerPos["x"] -= 1

		elif move == "s":
			playerPos["y"] += 1

		elif move == "d":
			playerPos["x"] += 1
		elif move == "r":
			placeStick()"""
		

		# Limit update speed to frameRate
		nextTime = refTime + (int(frameRate * frameTime) + 1) / frameRate
		frameDelta = nextTime - time()
		if frameDelta*90 > 1e-9:
			sleep(frameDelta)
finally:
	print "TEST ENDING"
	blank = ImageDraw.Draw(fb)
	blank.rectangle((0, 0, SIZE[0], SIZE[1]), fill=(0, 0, 0))
	lm.put(fb)
