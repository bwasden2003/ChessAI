from const import *
from square import Square
from piece import *
from move import Move
import copy


class Board:

    def __init__(self):
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        self.last_move = None
        self.white_pieces = []
        self.black_pieces = []
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    def move(self, piece, move):
        initial = move.initial
        final = move.final

        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        # pawn promotion
        if isinstance(piece, Pawn):
            self.check_promotion(piece, final)

        if isinstance(piece, King):
            if self.castling(initial, final):
                diff = final.col - initial.col
                rook = piece.left_rook if (diff < 0) else piece.right_rook
                self.move(rook, rook.moves[-1])

        # marked as moved
        piece.moved = True

        # clear valid moves
        piece.clear_moves()

        # update last move
        self.last_move = move

    def valid_move(self, piece, move):
        return move in piece.moves

    def check_promotion(self, piece, square):
        if square.row == 0 or square.row == 7:
            self.squares[square.row][square.col].piece = Queen(piece.color)

    def castling(self, initial, final):
        # if king moves 2 squares then we are castling
        return abs(initial.col - final.col) == 2

    def in_check(self, piece, move):
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)
        temp_board.move(temp_piece, move)

        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_enemy_piece(piece.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p, row, col)
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True
        return False

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
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row,
                                       possible_move_col, final_piece)
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
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row,
                                       possible_move_col, final_piece)
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
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row,
                                       possible_move_col, final_piece)
                        move = Move(initial, final)

                        if not self.squares[possible_move_row][possible_move_col].has_piece():
                            # append valid move
                            piece.add_move(move)

                        elif self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                            # append valid move
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
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)
                        move = Move(initial, final)
                        # append valid move
                        piece.add_move(move)

            # Castling moves
            if not piece.moved:
                # Queenside
                if not piece.left_rook.moved:
                    for c in range(1, 4):
                        if self.squares[row][c].has_piece():
                            break
                        if c == 3:
                            # rook move
                            initial = Square(row, 0)
                            final = Square(row, 3)
                            move = Move(initial, final)
                            piece.left_rook.add_move(move)

                            # king move
                            initial = Square(row, col)
                            final = Square(row, 2)
                            move = Move(initial, final)
                            piece.add_move(move)
                # Kingside
                if not piece.right_rook.moved:
                    for c in range(5, 7):
                        if self.squares[row][c].has_piece():
                            break
                        if c == 6:
                            # rook move
                            initial = Square(row, 7)
                            final = Square(row, 5)
                            move = Move(initial, final)
                            piece.right_rook.add_move(move)

                            # king move
                            initial = Square(row, col)
                            final = Square(row, 6)
                            move = Move(initial, final)
                            piece.add_move(move)

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
            if color == 'white':
                self.white_pieces.append(pawn)
            else:
                self.black_pieces.append(pawn)

        # rooks
        rook1 = Rook(color)
        self.squares[row_other][0] = Square(row_other, 0, rook1)
        rook2 = Rook(color)
        self.squares[row_other][7] = Square(row_other, 7, rook2)

        # knights
        knight1 = Knight(color)
        self.squares[row_other][1] = Square(row_other, 1, knight1)
        knight2 = Knight(color)
        self.squares[row_other][6] = Square(row_other, 6, knight2)

        # bishops
        bishop1 = Bishop(color)
        self.squares[row_other][2] = Square(row_other, 2, bishop1)
        bishop2 = Bishop(color)
        self.squares[row_other][5] = Square(row_other, 5, bishop2)

        # queen
        queen = Queen(color)
        self.squares[row_other][3] = Square(row_other, 3, queen)

        # king
        king = King(color)
        self.squares[row_other][4] = Square(row_other, 4, king)
        king.left_rook = rook1
        king.right_rook = rook2

        if color == 'white':
            self.white_pieces.append(rook1)
            self.white_pieces.append(rook2)
            self.white_pieces.append(knight1)
            self.white_pieces.append(knight2)
            self.white_pieces.append(bishop1)
            self.white_pieces.append(bishop2)
            self.white_pieces.append(queen)
            self.white_pieces.append(king)
        else:
            self.black_pieces.append(rook1)
            self.black_pieces.append(rook2)
            self.black_pieces.append(knight1)
            self.black_pieces.append(knight2)
            self.black_pieces.append(bishop1)
            self.black_pieces.append(bishop2)
            self.black_pieces.append(queen)
            self.black_pieces.append(king)
