from const import *
from square import Square
from piece import *
from move import Move
from sound import Sound
import copy
import numpy as np


class Board:

    def __init__(self):
        self.squares = np.zeros((8, 8), dtype=object)
        self.last_move = None
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    def move(self, piece, move, testing=False):
        initial = move.initial
        final = move.final

        en_passant_empty = not self.squares[final.row][final.col].has_piece()

        move.captured_piece = self.squares[final.row][final.col].piece
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        if isinstance(piece, Pawn):

            diff = final.col - initial.col
            if diff != 0 and en_passant_empty:
                move.captured_piece = self.squares[initial.row][initial.col + diff].piece
                self.squares[initial.row][initial.col + diff].piece = None
                self.squares[final.row][final.col].piece = piece
                move.was_enpassant = True
                if not testing:
                    sound = Sound(os.path.join('assets/sounds/capture.wav'))
                    sound.play()

            else:
                # pawn promotion
                self.check_promotion(piece, final)
                if final.row == 7 or final.row == 0:
                    move.was_promotion = True

        if isinstance(piece, King):
            if self.castling(initial, final) and not testing:
                move.was_castle = True
                if final.col > initial.col:  # King-side castle
                    rook = self.squares[initial.row][initial.col + 3].piece
                    self.squares[initial.row][initial.col +
                                                   3].piece = None
                else:  # Queen-side castle
                    rook = self.squares[initial.row][initial.col - 4].piece
                    self.squares[initial.row][initial.col -
                                                   4].piece = None

                # Move the rook to the other side of the king
                self.squares[final.row][final.col - 1 if final.col > initial.col else final.col + 1].piece = rook

        # marked as moved
        move.original_move_status = piece.moved
        piece.moved = True

        # update last move
        self.last_move = move

    def undo_move(self, piece, move):
        initial = move.initial
        final = move.final

        self.squares[initial.row][initial.col].piece = piece
        self.squares[final.row][final.col].piece = move.captured_piece

        if move.was_enpassant:
            diff = final.col - initial.col
            self.squares[initial.row][initial.col +
                                      diff].piece = move.captured_piece
            self.squares[final.row][final.col].piece = None
            piece.en_passant = False

        if move.was_promotion and (final.row == 0 or final.row == 7):
            self.squares[initial.row][initial.col].piece = Pawn(piece.color)

        if move.was_castle and abs(initial.col - final.col) == 2:
            if final.col > initial.col:  # King-side castle
                rook = self.squares[final.row][final.col - 1].piece
                self.squares[final.row][final.col - 1].piece = None
            else:  # Queen-side castle
                rook = self.squares[final.row][final.col + 1].piece
                self.squares[final.row][final.col + 1].piece = None

            self.squares[initial.row][initial.col + 3 if final.col > initial.col else initial.col - 4].piece = rook
            rook.moved = False

        piece.moved = move.original_move_status

    def valid_move(self, piece, move):
        return move in piece.moves

    def check_promotion(self, piece, square):
        if square.row == 0 or square.row == 7:
            self.squares[square.row][square.col].piece = Queen(piece.color)

    def castling(self, initial, final):
        # if king moves 2 squares then we are castling
        return abs(initial.col - final.col) == 2

    def set_true_en_passant(self, piece):
        if not isinstance(piece, Pawn):
            return

        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False

        piece.en_passant = True

    def in_check(self, piece, move):
        self.move(piece, move, testing=True)
        king_square = None
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_piece():
                    p = self.squares[row][col].piece
                    if isinstance(p, King) and p.color == piece.color:
                        king_square = (row, col)
                        break
            if king_square is not None:
                break

        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_enemy_piece(piece.color):
                    p = self.squares[row][col].piece
                    self.possible_moves(p, row, col, False)
                    for m in p.moves:
                        if (m.final.row, m.final.col) == king_square:
                            self.undo_move(piece, move)
                            return True

        self.undo_move(piece, move)
        return False

    def is_checkmate(self, color):
        for move in self.moves_by_color(color):
            if not self.in_check(move.initial.piece, move):
                return False
        return True

    # returns number of pieces that are attacking piece
    def attackers(self, piece):
        res = 0
        for r in range(ROWS):
            for c in range(COLS):
                if self.squares[r][c].has_piece():
                    p = self.squares[r][c].piece
                    self.possible_moves(p, r, c)
                    for move in p.moves:
                        if move.final.piece == piece:
                            res += 1
                    p.clear_moves()
        return res

    def moves_by_color(self, color):
        moves = []
        for row in range(ROWS):
            for col in range(ROWS):
                if self.squares[row][col].has_team_piece(color):
                    piece = self.squares[row][col].piece
                    self.possible_moves(piece, row, col)
                    for move in piece.moves:
                        moves.append(move)
        return moves

    def possible_moves(self, piece, row, col, bool=True):
        piece.clear_moves()

        def pawn_moves():
            steps = 1 if piece.moved else 2

            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))
            for move_row in range(start, end, piece.dir):
                if Square.in_range(move_row):
                    if not self.squares[move_row][col].has_piece():
                        initial = Square(row, col, piece)
                        final = Square(move_row, col)
                        move = Move(initial, final)

                        # check for pottential checks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
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
                        initial = Square(row, col, piece)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row,
                                       possible_move_col, final_piece)
                        move = Move(initial, final)

                        # check for pottential checks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

            # en passant moves
            # left
            r = 3 if piece.color == 'white' else 4
            fr = 2 if piece.color == 'white' else 5
            if Square.in_range(col - 1) and row == r:
                if self.squares[row][col - 1].has_enemy_piece(piece.color):
                    final_piece = self.squares[row][col - 1].piece
                    if isinstance(piece, Pawn) and isinstance(final_piece, Pawn):
                        if final_piece.en_passant:
                            initial = Square(row, col, piece)
                            final = Square(fr, col - 1, final_piece)
                            move = Move(initial, final)

                            # check for pottential checks
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
            # right
            if Square.in_range(col + 1) and row == r:
                if self.squares[row][col + 1].has_enemy_piece(piece.color):
                    final_piece = self.squares[row][col + 1].piece
                    if isinstance(piece, Pawn) and isinstance(final_piece, Pawn):
                        if final_piece.en_passant:
                            initial = Square(row, col, piece)
                            final = Square(fr, col + 1, final_piece)
                            move = Move(initial, final)

                            # check for pottential checks
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
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
                        initial = Square(row, col, piece)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row,
                                       possible_move_col, final_piece)
                        move = Move(initial, final)
                        # check for pottential checks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

        def straightline_moves(dirs):
            for dir in dirs:
                row_dir, col_dir = dir
                possible_move_row = row + row_dir
                possible_move_col = col + col_dir
                while True:
                    if Square.in_range(possible_move_row, possible_move_col):
                        # create new move
                        initial = Square(row, col, piece)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row,
                                       possible_move_col, final_piece)
                        move = Move(initial, final)

                        if not self.squares[possible_move_row][possible_move_col].has_piece():
                            # check for pottential checks
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)

                        elif self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                            # check for pottential checks
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
                            # break after first enemy piece found (can't go through piece)
                            break

                        elif self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
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
                        initial = Square(row, col, piece)
                        final = Square(possible_move_row, possible_move_col)
                        move = Move(initial, final)
                        # check for pottential checks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

            # Castling moves
            if not piece.moved:
                # Queenside
                left_rook = self.squares[row][0].piece
                if isinstance(left_rook, Rook):
                    if not left_rook.moved:
                        for c in range(1, 4):
                            if self.squares[row][c].has_piece():
                                break
                            if c == 3:
                                # rook move
                                initial = Square(row, 0, left_rook)
                                final = Square(row, 3)
                                moveR = Move(initial, final)

                                # king move
                                initial = Square(row, col, piece)
                                final = Square(row, 2)
                                moveK = Move(initial, final)

                                # check for pottential checks
                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(left_rook, moveR):
                                        left_rook.add_move(moveR)
                                        piece.add_move(moveK)
                                else:
                                    left_rook.add_move(moveR)
                                    piece.add_move(move)
                # Kingside
                right_rook = self.squares[row][7].piece
                if isinstance(right_rook, Rook):
                    if not right_rook.moved:
                        for c in range(5, 7):
                            if self.squares[row][c].has_piece():
                                break
                            if c == 6:
                                # rook move
                                initial = Square(row, 7, right_rook)
                                final = Square(row, 5)
                                moveR = Move(initial, final)

                                # king move
                                initial = Square(row, col, piece)
                                final = Square(row, 6)
                                moveK = Move(initial, final)

                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(right_rook, moveR):
                                        right_rook.add_move(moveR)
                                        piece.add_move(moveK)
                                else:
                                    right_rook.add_move(moveR)
                                    piece.add_move(moveK)

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
            pawn = Pawn(color)
            self.squares[row_pawn][col] = Square(row_pawn, col, pawn)

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

    def hash(self):
        board_str = ''
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.squares[row][col].piece
                if piece is None:
                    board_str += '00'
                else:
                    if piece.color == 'white':
                        board_str += '1'
                    else:
                        board_str += '2'

                    if isinstance(piece, Pawn):
                        board_str += '1'
                    elif isinstance(piece, Knight):
                        board_str += '2'
                    elif isinstance(piece, Bishop):
                        board_str += '3'
                    elif isinstance(piece, Rook):
                        board_str += '4'
                    elif isinstance(piece, Queen):
                        board_str += '5'
                    elif isinstance(piece, King):
                        board_str += '6'
        return int(board_str, base=12)
