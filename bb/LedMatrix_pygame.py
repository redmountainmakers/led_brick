#!/usr/bin/python
import pygame
from numpy import array

class LedMatrix:
	def __init__(self, size = (29, 6)):
		self.size = size
		scale = 1024 / size[0]
		self.dispsize = (self.size[0] * scale, self.size[1] * scale)

		pygame.init()
		pygame.display.set_mode(self.dispsize)
		self.surf = pygame.Surface(self.size)

	def put(self, img):
		pygame.surfarray.blit_array(self.surf, array([self.surf.map_rgb(pygame.Color(rgb[0], rgb[1], rgb[2], 255)) for rgb in img.getdata()]).reshape(self.size, order='F'))
		disp = pygame.display.get_surface()
		pygame.transform.scale(self.surf, self.dispsize, disp)
		pygame.display.flip()
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
				pygame.quit()
				quit()
