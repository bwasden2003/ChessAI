from const import *

from board import Board
from game import Game


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
        center = [4, 5]
        material_score = 0
        control_score = 0

        # incorporate way to get piece scores for white and black
        for row in range(ROWS):
            for col in range(COLS):
                if self.game.board.squares[row][col].has_piece():
                    piece = self.game.board.squares[row][col].piece
                    value = piece.value
                    material_score += value
                # calculate control score
                    if row in center and col in center:
                        control_score += 1 if piece.color == 'black' else -1
                    if piece.name == 'king':
                        # calculate safety score
                        # to do this I need a list of pieces attacking the king (need to implement this for check/checkmates anyways)
                        pass
                        # calculate pawn structure score

                        # need to determine weights for each factor

                        # return scores * weights
