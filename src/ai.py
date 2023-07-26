from const import *

from board import Board
from game import Game
from piece import *
from square import Square


class AI:

    def __init__(self, game):
        self.game = game

    def iterative_deepening(board, depth_limit):
        best_move = None
        pass

    def alpha_beta_search(board, depth_limit):
        best_value = float('-inf')
        alpha, beta = float('-inf'), float('inf')
        best_move = None
        # loop through legal moves

    def evaluate(self):
        # center squares = more control
        center = [3, 4]
        material_score = 0
        control_score = 0
        mobility_score = 0
        structure_score = 0

        white_pawn_files = [0] * 8
        black_pawn_files = [0] * 8

        # incorporate way to get piece scores for white and black
        for row in range(ROWS):
            for col in range(COLS):
                if self.game.board.squares[row][col].has_piece():
                    piece = self.game.board.squares[row][col].piece
                    value = piece.value
                    material_score += value
                    self.game.board.possible_moves(piece, row, col)
                    # calculate control score
                    if row in center and col in center:
                        control_score += 1 if piece.color == 'black' else -1

                    if piece.color == 'white':
                        if isinstance(piece, King):
                            # calculate safety score
                            safety_score += self.game.board.attackers(piece)
                        elif isinstance(piece, Pawn):
                            white_pawn_files[col] += 1
                            # mobility score
                        mobility_score -= len(piece.moves)
                    else:
                        if isinstance(piece, King):
                            safety_score -= self.game.board.attackers(piece)
                        elif isinstance(piece, Pawn):
                            black_pawn_files[col] += 1
                        mobility_score += len(piece.moves)
                    piece.clear_moves()
        # calculate pawn structure score
        for file in range(8):
            # doubled pawns
            if white_pawn_files[file] > 1:
                structure_score += white_pawn_files[file]
            if black_pawn_files[file] > 1:
                structure_score -= black_pawn_files[file]

            # isolated pawns
            if file > 0 and file < 7:
                if white_pawn_files[file] > 0 and white_pawn_files[file - 1] == 0 and white_pawn_files[file + 1] == 0:
                    structure_score += white_pawn_files[file]
                if black_pawn_files[file] > 0 and black_pawn_files[file - 1] == 0 and black_pawn_files[file + 1] == 0:
                    structure_score -= black_pawn_files[file]
            elif file == 0:
                if white_pawn_files[file] > 0 and white_pawn_files[file + 1] == 0:
                    structure_score += white_pawn_files[file]
                if black_pawn_files[file] > 0 and black_pawn_files[file + 1] == 0:
                    structure_score -= black_pawn_files[file]
            elif file == 7:
                if white_pawn_files[file] > 0 and white_pawn_files[file - 1] == 0:
                    structure_score += white_pawn_files[file]
                if black_pawn_files[file] > 0 and black_pawn_files[file - 1] == 0:
                    structure_score -= black_pawn_files[file]

        # need to determine weights for each factor
        # return scores * weights
