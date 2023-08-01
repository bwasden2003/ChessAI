import os


class Piece:

    def __init__(self, name, color, value, texture=None, texture_rect=None):
        self.name = name
        self.color = color

        value_sign = 1 if color == 'white' else -1
        self.value = value * value_sign

        self.moves = []
        self.moved = False

        self.texture = texture
        self.set_texture()
        self.texture_rect = texture_rect

    def set_texture(self, size=80):
        self.texture = os.path.join(
            f'assets/images/imgs-{size}px/{self.color}_{self.name}.png')

    def add_move(self, move):
        self.moves.append(move)

    def clear_moves(self):
        self.moves = []

    @staticmethod
    def sort_moves(moves):
        def move_key(move):
            initial_square = move.initial
            final_square = move.final

            is_capture = int(final_square.piece is not None)
            is_check = int(final_square.piece is not None and isinstance(
                final_square.piece, King))
            is_promotion = int(isinstance(
                initial_square.piece, Pawn) and final_square.row in [0, 7])
            is_pawn_move = int(isinstance(initial_square.piece, Pawn))
            return ((is_pawn_move * -4 + is_capture * 3 + is_check * 2 + is_promotion * 1), is_capture, is_check, is_promotion)
        moves.sort(key=move_key, reverse=True)


class Pawn(Piece):

    def __init__(self, color):
        self.dir = -1 if color == 'white' else 1
        self.en_passant = False
        super().__init__('pawn', color, 1)


class Knight(Piece):

    def __init__(self, color):
        super().__init__('knight', color, 3)


class Bishop(Piece):

    def __init__(self, color):
        super().__init__('bishop', color, 3.01)


class Rook(Piece):

    def __init__(self, color):
        super().__init__('rook', color, 5)


class Queen(Piece):

    def __init__(self, color):
        super().__init__('queen', color, 9)


class King(Piece):

    def __init__(self, color):
        super().__init__('king', color, 100000)
        self.left_rook = None
        self.right_rook = None
