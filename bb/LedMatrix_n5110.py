#!/usr/bin/python
from PIL import Image
from n5110 import n5110

class LedMatrix:
	def __init__(self, size = (84, 48)):
		self.nok = n5110()
		self.size = size

	def put(self, img):
		bmap = img.convert('1')
		for rowset in range(0, (img.size[1] + 7) / 8):
			row = bmap.crop((0, 8*rowset, self.size[0], 8)).transpose(Image.ROTATE_270)
			data = list(ord(value) for value in row.tostring())
			self.nok.setLocation(0, rowset)
			self.nok.writeCols(data)
