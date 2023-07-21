from const import *
from square import Square
from piece import *
from move import Move

class Board:
    
	def __init__(self):
		self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
		self.last_move = None
		self._create()
		self._add_pieces('white')
		self._add_pieces('black')

	def move(self, piece, move):
		initial = move.initial
		final = move.final

		self.squares[initial.row][initial.col].piece = None
		self.squares[final.row][final.col].piece = piece

		# marked as moved
		piece.moved = True

		# clear valid moves
		piece.clear_moves()

		# update last move
		self.last_move = move

	def valid_move(self, piece, move):
		return move in piece.moves

	def possible_moves(self, piece, row, col):
		
		def pawn_moves():
			steps = 1 if piece.moved else 2
			
			start = row + piece.dir
			end = row + (piece.dir * (1 + steps))
			for move_row in range(start, end, piece.dir):
				if Square.in_range(move_row):
					if not self.squares[move_row][col].has_piece():
						initial = Square(row, col)
						final = Square(move_row, col)
						move = Move(initial, final)
						piece.add_move(move)
					else:
						break
				else:
					break
			
			possible_move_row = row + piece.dir
			possible_move_cols = [col - 1, col + 1]
			for possible_move_col in possible_move_cols:
				if Square.in_range(possible_move_row, possible_move_col):
					if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
						initial = Square(row, col)
						final = Square(possible_move_row, possible_move_col)
						move = Move(initial, final)
						piece.add_move(move)


		def knight_moves():
			possible_moves = [
				(row - 2, col + 1),
				(row - 1, col + 2),
				(row + 1, col + 2),
				(row + 2, col + 1),
				(row + 2, col - 1),
				(row + 1, col - 2),
				(row - 1, col - 2),
				(row - 2, col - 1),
			]
			
			for possible_move in possible_moves:
				possible_move_row, possible_move_col = possible_move
				
				if Square.in_range(possible_move_row, possible_move_col):
					if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
						# create new move
						initial = Square(row, col)
						final = Square(possible_move_row, possible_move_col)
						move = Move(initial, final)
						# append valid move
						piece.add_move(move)
		
		def straightline_moves(dirs):
			for dir in dirs:
				row_dir, col_dir = dir
				possible_move_row = row + row_dir
				possible_move_col = col + col_dir
				while True:
					if Square.in_range(possible_move_row, possible_move_col):
						# create new move
						initial = Square(row, col)
						final = Square(possible_move_row, possible_move_col)
						move = Move(initial, final)

						if not self.squares[possible_move_row][possible_move_col].has_piece():
							# append valid move
							piece.add_move(move)

						if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
							# append valid move
							piece.add_move(move)
							# break after first enemy piece found (can't go through piece)
							break

						if self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
							# break when team piece found (can't go through piece)
							break

					else:
						break
					possible_move_row += row_dir
					possible_move_col += col_dir
			
		def king_moves():
			possible_moves = [
				(row - 1, col),
				(row - 1, col + 1),
				(row, col + 1),
				(row + 1, col + 1),
				(row + 1, col),
				(row + 1, col - 1),
				(row, col - 1),
				(row - 1, col - 1)
			]

			for possible_move in possible_moves:
				possible_move_row, possible_move_col = possible_move
				
				if Square.in_range(possible_move_row, possible_move_col):
					if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
						# create new move
						initial = Square(row, col)
						final = Square(possible_move_row, possible_move_col)
						move = Move(initial, final)
						# append valid move
						piece.add_move(move)
			
			# Castling moves
				# Queenside
				# Kingside

		if isinstance(piece, Pawn):
			pawn_moves()
		elif isinstance(piece, Knight):
			knight_moves()
		elif isinstance(piece, Bishop):
			straightline_moves([
				(-1, 1),
				(-1, -1),
				(1, 1),
				(1, -1)
			])
		elif isinstance(piece, Rook):
			straightline_moves([
				(-1, 0),
				(0, 1),
				(1, 0),
				(0, -1)	
			])
		elif isinstance(piece, Queen):
			straightline_moves([
				(-1, 1),
				(-1, -1),
				(1, 1),
				(1, -1),
				(-1, 0),
				(0, 1),
				(1, 0),
				(0, -1)
			])
		elif isinstance(piece, King):
			king_moves()

	def _create(self):
		for row in range(ROWS):
			for col in range(COLS):
				self.squares[row][col] = Square(row, col)
	
	def _add_pieces(self, color):
		if color == 'white':
			row_pawn, row_other = (6, 7)
		else:
			row_pawn, row_other = (1, 0)

		# pawns	
		for col in range(COLS):
			self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

		# rooks
		self.squares[row_other][0] = Square(row_other, 0, Rook(color))
		self.squares[row_other][7] = Square(row_other, 7, Rook(color))

		# knights
		self.squares[row_other][1] = Square(row_other, 1, Knight(color))
		self.squares[row_other][6] = Square(row_other, 6, Knight(color))

		# bishops
		self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
		self.squares[row_other][5] = Square(row_other, 5, Bishop(color))

		# queen
		self.squares[row_other][3] = Square(row_other, 3, Queen(color))

		# king
		self.squares[row_other][4] = Square(row_other, 4, King(color))
