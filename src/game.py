import pygame

from const import *
from board import Board
from dragger import Dragger


class Game:
    
	def __init__(self):
		self.next_player = 'white'
		self.hovered_square = None
		self.board = Board()
		self.dragger = Dragger()

	def show_bg(self, surface):
		for row in range(ROWS):
			for col in range(COLS):
				if (row + col) % 2 == 0:
					color = (234, 235, 200) # light green
				else:
					color = (119, 154, 88) # dark green
				
				rect = (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)

				pygame.draw.rect(surface, color, rect)

	def show_pieces(self, surface):
		for row in range(ROWS):
			for col in range(COLS):
				if self.board.squares[row][col].has_piece():
					piece = self.board.squares[row][col].piece

					# show all pieces but the one being dragged (if there is one)
					if piece is not self.dragger.piece:
						piece.set_texture(size=80)
						img = pygame.image.load(piece.texture)
						img_center = col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2
						piece.texture_rect = img.get_rect(center=img_center)
						surface.blit(img, piece.texture_rect)

	def show_moves(self, surface):
		if self.dragger.dragging:
			piece = self.dragger.piece

			# loop through possible moves
			for move in piece.moves:
				color = '#C86464' if (move.final.row + move.final.col) % 2 == 0 else '#C84646'
				rect = (move.final.col * SQUARE_SIZE, move.final.row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
				pygame.draw.rect(surface, color, rect)
	
	def show_last_move(self, surface):
		if self.board.last_move:
			initial = self.board.last_move.initial
			final = self.board.last_move.final

			for pos in [initial, final]:
				color = (244, 247, 116) if (pos.row + pos.col) % 2 == 0 else (172, 195, 51)
				rect = (pos.col * SQUARE_SIZE, pos.row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
				pygame.draw.rect(surface, color, rect)

	def show_hover(self, surface):
		if self.hovered_square:
			color = (180, 180, 180)
			rect = (self.hovered_square.col * SQUARE_SIZE, self.hovered_square.row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
			pygame.draw.rect(surface, color, rect, width = 3)

	def set_hover(self, row, col):
		self.hovered_square = self.board.squares[row][col]

	def next_turn(self):
		self.next_player = 'white' if self.next_player == 'black' else 'black'