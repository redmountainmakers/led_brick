#!/usr/bin/python
from time import time
from PIL import Image
import pyximport; pyximport.install()
from RMM_SPI import SPI, SPI_MODE_0, SPI_NO_CS

class LedMatrix:
	def __init__(self, size = (29, 6), spi = None, clock = 12*1000*1000):
		self.spi = spi if spi is not None else SPI()
		self.spi.mode = SPI_MODE_0 | SPI_NO_CS
		self.spi.bpw = 8
		self.spi.speed_hz = clock
		self.reftime = time()

		self.size = size

	def put(self, img):
		# crop to our display area and rotate to row-major
		rimg = img.crop((0, 0, self.size[0], self.size[1])).convert('RGB').transpose(Image.ROTATE_270).transpose(Image.FLIP_LEFT_RIGHT)
		data = bytearray(rimg.tostring())

		# XXX FIXME: *Why* does the data need to be reversed?  Driver problem?
		data.reverse()

		# ensure that 600us have passed since the last draw.
		# XXX TODO: maybe just add this to the last transaction always..
		# Need to see if the driver is synchronous or asynchronous.
		curtime = time()
		if curtime - self.reftime < 600e-6:
			delay_us = int(1e6 * (600e-6 + self.reftime - curtime))
			if delay_us <= 0: delay_us = None
		else:
			delay_us = None

		transactions = [ { 'tx': data } ]
		if delay_us is not None:
			transactions.insert(0, { 'tx': 0, 'delay_us': delay_us })
		# WS2803 has strange behavior when all 144 bits (18 bytes) are not sent.
		if len(data) % 18:
			transactions.append({ 'tx': 18 - (len(data) % 18) })
		self.spi.transact(transactions)
		self.reftime = time()
