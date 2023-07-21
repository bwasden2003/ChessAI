import pygame

from const import *

class Dragger:
    
	def __init__(self):
		self.piece = None
		self.dragging = False
		self.mouseX = 0
		self.mouseY = 0
		self.initial_row = 0
		self.initial_col = 0

	# blit methods
	
	def update_blit(self, surface):
		# set new texture
		self.piece.set_texture(size=128)
		texture = self.piece.texture
		# get img
		img = pygame.image.load(texture)
		# rect
		img_center = (self.mouseX, self.mouseY)
		self.piece.texture_rect = img.get_rect(center=img_center)
		# blit
		surface.blit(img, self.piece.texture_rect)

	# other methods

	def update_mouse(self, pos):
		self.mouseX, self.mouseY = pos # (xcord, ycord)

	def save_initial(self, pos):
		self.initial_row, self.initial_col = pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE

	def drag_piece(self, piece):
		self.piece = piece
		self.dragging = True

	def undrag_piece(self):
		self.piece = None
		self.dragging = False

	