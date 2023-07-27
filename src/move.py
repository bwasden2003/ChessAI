
class Move:
    
	def __init__(self, initial, final):
		# initial and final are both Square objects
		self.initial = initial
		self.final = final
		self.was_enpassant = False
		self.was_castle = False
		self.was_promotion = False
		self.original_moved_status = False
		self.captured_piece = None

	def __str__(self):
		s = ''
		s += f'({self.initial.col}, {self.initial.row})'
		s += f' -> ({self.final.col}, {self.final.row})'
		return s
	
	def __eq__(self, other):
		return self.initial == other.initial and self.final == other.final