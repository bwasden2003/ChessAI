from const import *

from board import Board
from game import Game
from piece import *
from square import Square
import copy


class AI:

    def __init__(self, game, color):
        self.game = game
        self.color = color
        self.enemy_color = 'white' if color == 'black' else 'black'
        self.transposition_table = {}

    def alpha_beta_search(self, board, depth):
        best_score = float('-inf')
        best_move = None

        moves = board.moves_by_color(self.color)
        Piece.sort_moves(moves)
        for d in range(1, depth + 1):
            for move in moves:
                board.move(move.initial.piece, move, testing=True)
                score = -self.minimax(board, d - 1,
                                      float('-inf'), float('inf'), False)
                board.undo_move(move.initial.piece, move)
                if score > best_score:
                    best_score = score
                    best_move = move
        return best_move

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        key = board.hash()

        if key in self.transposition_table and self.transposition_table[key][0] >= depth:
            return self.transposition_table[key][1]

        if depth == 0:  # or checkmate
            return self.evaluate(board)

        if maximizing_player:
            value = float('-inf')
            for move in board.moves_by_color(self.color):
                board.move(move.initial.piece, move, testing=True)
                value = max(value, self.minimax(
                    board, depth - 1, alpha, beta, False))
                board.undo_move(move.initial.piece, move)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
        else:
            value = float('inf')
            for move in board.moves_by_color(self.color):
                board.move(move.initial.piece, move, testing=True)
                value = min(value, self.minimax(
                    board, depth - 1, alpha, beta, True))
                board.undo_move(move.initial.piece, move)
                beta = min(beta, value)
                if beta <= alpha:
                    break
        self.transposition_table[key] = (depth, value)
        return value

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
