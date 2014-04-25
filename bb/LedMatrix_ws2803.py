#!/usr/bin/python
from time import time, sleep
from PIL import Image
from Adafruit_BBIO.SPI import SPI

class LedMatrix:
	def __init__(self, size = (29, 6), spi = SPI(0,0), clock = 25*1000*1000):
		self.spi = spi
		self.spi.msh = clock
		self.spi.lsbfirst = False
		self.spi.mode = 0b00
		self.spi.threewire = False
		self.spi.bpw = 8
		self.spi.writebytes([])
		self.reftime = time()

		self.size = size

	def put(self, img):
		# ensure that 600us have passed since the last draw.
		curtime = time()
		if (curtime - self.reftime < 600e-6):
			sleep(600e-6 + self.reftime - curtime)

		# crop to our display area and rotate to row-major
		rimg = img.crop((0, 0, self.size[0], self.size[1])).convert('RGB').transpose(Image.ROTATE_90)

		# convert the image in to a list of ints we can send via spi.writebytes
		data = list( ord(value) for value in rimg.tostring() )

		self.spi.mode = 0b11 # keep clock high to avoid position reset
		while data:
			out = data[0:255] # switch to 16383(4?) once Adafruit_BBIO.SPI is updated.
			del data[0:255]
			self.spi.writebytes(out)
		self.spi.mode = 0b00
		self.spi.writebytes([]) # bring clock low to allow for position reset
		self.reftime = time()
