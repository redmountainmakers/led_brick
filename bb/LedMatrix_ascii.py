#!/usr/bin/python
from PIL import Image
from aalib import AnsiScreen # too annoying to install python-caca in Debian :P

class LedMatrix:
	def __init__(self, size = (29, 6)):
		self.size = size
		self.scr = AnsiScreen()
		self.rsize = (self.scr.virtual_size[0], self.scr.virtual_size[0] * self.size[1] / self.size[0])
		if self.rsize[1] > self.scr.virtual_size[1]:
			self.rsize[1] = self.scr.virtual_size[1]
		self.centrow = (self.scr.virtual_size[1] - self.rsize[1]) / 2
		print "\033[2J\033[1;1H",

	def put(self, img):
		rimg = img.convert('L').resize(self.rsize, Image.NEAREST);
		self.scr.put_image((0, self.centrow), rimg)
		print "\033[1;1H", self.scr.render(),
