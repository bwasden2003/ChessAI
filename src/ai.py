from const import *

from board import Board
from game import Game
from piece import *
from square import Square
import copy

class AI:

    def __init__(self, game):
        self.game = game

    def alpha_beta_search(self, board, alpha, beta, depth, maximize):
        if depth == 0: #or gameover
            return None, self.evaluate(board)
        print(f"depth = {depth}")
        if maximize:
            best_value = float('-inf')
            best_move = None
            for row in range(ROWS):
                for col in range(COLS):
                    if board.squares[row][col].has_piece():
                        piece = board.squares[row][col].piece
                        if piece.color == 'black':
                            board.possible_moves(piece, row, col)
                            for move in piece.moves:
                                board.move(piece, move, testing=True)
                                _, eval = self.alpha_beta_search(board, alpha, beta, depth - 1, False)
                                board.undo_move(piece, move)
                                if eval > best_value:
                                    best_value = eval
                                    best_move = move
                                alpha = max(alpha, eval)
                                if beta <= alpha:
                                    return best_move, best_value
            return best_move, best_value
        else:
            worst_value = float('inf')
            worst_move = None
            for row in range(ROWS):
                for col in range(COLS):
                    if board.squares[row][col].has_piece():
                        piece = board.squares[row][col].piece
                        if piece.color == 'white':
                            board.possible_moves(piece, row, col)
                            for move in piece.moves:
                                board.move(piece, move, testing=True)
                                _, eval = self.alpha_beta_search(board, alpha, beta, depth - 1, True)
                                board.undo_move(piece, move)
                                if eval < worst_value:
                                    worst_value = eval
                                    worst_move = move
                                beta = min(beta, eval)
                                if beta <= alpha:
                                    return worst_move, worst_value
            return worst_move, worst_value




    def evaluate(self, board):
        # center squares = more control
        center = [3, 4]
        material_score = 0
        control_score = 0
        mobility_score = 0
        safety_score = 0
        structure_score = 0

        white_pawn_files = [0] * 8
        black_pawn_files = [0] * 8

        # incorporate way to get piece scores for white and black
        for row in range(ROWS):
            for col in range(COLS):
                if board.squares[row][col].has_piece():
                    piece = board.squares[row][col].piece
                    value = piece.value
                    material_score += value
                    board.possible_moves(piece, row, col)
                    # calculate control score
                    if row in center and col in center:
                        control_score += 1 if piece.color == 'black' else -1

                    if piece.color == 'white':
                        if isinstance(piece, King):
                            # calculate safety score
                            safety_score += board.attackers(piece)
                        elif isinstance(piece, Pawn):
                            white_pawn_files[col] += 1
                            # mobility score
                        mobility_score -= len(piece.moves)
                    else:
                        if isinstance(piece, King):
                            safety_score -= board.attackers(piece)
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
        material_weight = 1.0
        control_weight = 0.1
        mobility_weight = 0.1
        safety_weight = 0.2
        structure_weight = 0.1

        # return scores * weights
        return (material_score * material_weight + control_score * control_weight + mobility_score * mobility_weight + safety_score * safety_weight + structure_score * structure_weight)