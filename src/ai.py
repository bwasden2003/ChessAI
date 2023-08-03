from const import *

from board import Board
from game import Game
from piece import *
from square import Square
import threading
import numpy as np


class AI:
    WHITE_PAWN_TABLE = np.array([
        [8, 8, 8, 8, 8, 8, 8, 8],
        [8, 8, 8, 8, 8, 8, 8, 8],
        [5, 6, 6, 7, 7, 6, 6, 5],
        [2, 3, 3, 5, 5, 3, 3, 2],
        [1, 2, 3, 4, 4, 3, 2, 1],
        [1, 1, 2, 3, 3, 2, 1, 1],
        [1, 1, 1, 0, 0, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ])

    BLACK_PAWN_TABLE = np.array([
        [0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 2, 3, 3, 2, 1, 1],
        [1, 2, 3, 4, 4, 3, 2, 1],
        [2, 3, 3, 5, 5, 3, 3, 2],
        [5, 6, 6, 7, 7, 6, 6, 5],
        [8, 8, 8, 8, 8, 8, 8, 8],
        [8, 8, 8, 8, 8, 8, 8, 8]
    ])

    KNIGHT_TABLE = np.array([
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 3, 3, 3, 3, 2, 1],
        [1, 2, 3, 4, 4, 3, 2, 1],
        [1, 2, 3, 4, 4, 3, 2, 1],
        [1, 2, 3, 3, 3, 3, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 1],
        [1, 1, 1, 1, 1, 1, 1, 1]
    ])

    BISHOP_TABLE = np.array([
        [4, 3, 2, 1, 1, 2, 3, 4],
        [3, 4, 3, 2, 2, 3, 4, 3],
        [2, 3, 4, 3, 3, 4, 3, 2],
        [1, 2, 3, 4, 4, 3, 2, 1],
        [1, 2, 3, 4, 4, 3, 2, 1],
        [2, 3, 4, 3, 3, 4, 3, 2],
        [3, 4, 3, 2, 2, 3, 4, 3],
        [4, 3, 2, 1, 1, 2, 3, 4]
    ])

    ROOK_TABLE = np.array([
        [4, 3, 4, 4, 4, 4, 3, 4],
        [4, 4, 4, 4, 4, 4, 4, 4],
        [1, 1, 2, 3, 3, 2, 1, 1],
        [1, 2, 3, 4, 4, 3, 2, 1],
        [1, 2, 3, 4, 4, 3, 2, 1],
        [1, 1, 2, 3, 3, 2, 1, 1],
        [4, 4, 4, 4, 4, 4, 4, 4],
        [4, 3, 4, 4, 4, 4, 3, 4]
    ])

    QUEEN_TABLE = np.array([
        [1, 1, 1, 3, 1, 1, 1, 1],
        [1, 2, 3, 3, 3, 1, 1, 1],
        [1, 4, 3, 3, 3, 4, 2, 1],
        [1, 2, 3, 3, 3, 2, 2, 1],
        [1, 2, 3, 3, 3, 2, 2, 1],
        [1, 4, 3, 3, 3, 4, 2, 1],
        [1, 2, 3, 3, 3, 1, 1, 1],
        [1, 1, 1, 3, 1, 1, 1, 1]
    ])
    
    def __init__(self, game, color):
        self.game = game
        self.color = color
        self.enemy_color = 'white' if color == 'black' else 'black'
        self.transposition_table = {}
        self.best_score = 0
        self.best_move = None
        self.move_history = []
        self.material_score = 0
        self.control_score = 0
        self.mobility_score = 0
        self.safety_score = 0
        self.low_score = float('inf')
        self.response_move = None
        
    def calculate_move(self, board, depth):
        self.move_history = []
        ai_thread = threading.Thread(target=self.alpha_beta_search, args=(board, depth))
        ai_thread.start()
        return ai_thread
            

    def alpha_beta_search(self, board, depth):
        self.best_score = float('-inf')
        best_move = None

        moves = board.moves_by_color(self.color)
        Piece.sort_moves(moves)
        for move in moves:
            board.move(move.initial.piece, move, testing=True)
            score = self.minimax(board, depth - 1,
                                    float('-inf'), float('inf'), False)
            self.move_history.append((move, score))
            board.undo_move(move.initial.piece, move)
            if score > self.best_score:
                self.best_score = score
                self.best_move = move
                # for move, value in self.move_history:
                #     print(f"VALUE: {value}")
                #     print(f"Move: {move.initial.row}, {move.initial.col} -> {move.final.row}, {move.final.col}")
                # print("______________________________________________________________________")
        # print(f"Start: {best_move.initial.row}, {best_move.initial.col}. End: {best_move.final.row}, {best_move.final.col}. Score: {self.best_score}")
        # print(f"Response Move Start: {self.response_move.initial.row}, {self.response_move.initial.col}, Response Move End: {self.response_move.final.row}, {self.response_move.final.col}")
        # print(f"Material Score: {self.material_score}, Control Score: {self.control_score}, Mobility Score: {self.mobility_score}, Safety Score: {self.safety_score}")
        return  
    def show_best_move(self, surface):
        self.game.show_ai_best_move(surface, self.best_move)
    def minimax(self, board, depth, alpha, beta, maximizing_player):
        key = board.hash()

        if key in self.transposition_table and self.transposition_table[key][0] >= depth:
            return self.transposition_table[key][1]
        color = self.color if maximizing_player else self.enemy_color
        if depth == 0 or board.is_checkmate(color):  # or checkmate
            return self.evaluate(board)

        if maximizing_player:
            value = float('-inf')
            moves = board.moves_by_color(color)
            Piece.sort_moves(moves)
            for move in moves:
                board.move(move.initial.piece, move, testing=True)
                value = max(value, self.minimax(
                    board, depth - 1, alpha, beta, False))
                board.undo_move(move.initial.piece, move)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
        else:
            value = float('inf')
            moves = board.moves_by_color(color)
            Piece.sort_moves(moves)
            for move in moves:
                board.move(move.initial.piece, move, testing=True)
                value = min(value, self.minimax(
                    board, depth - 1, alpha, beta, True))
                board.undo_move(move.initial.piece, move)
                self.move_history.append((move, value))
                beta = min(value, beta)
                    # if value < self.low_score:
                    #     self.low_score = value
                    #     self.response_move = move
                    #     print(f"MIN VALUE: {value}")
                    #     for i, move in enumerate(self.move_history):
                    #         print(f"Move {i + 1}: {move.initial.row}, {move.initial.col} -> {move.final.row}, {move.final.col}")
                    #     print("_______________________________________")
                if beta <= alpha:
                    break
        self.transposition_table[key] = (depth, value)
        return value
    
    def get_piece_position_score(self, board, piece_type, table, second_table=None):
        white = 0
        black = 0
        for row in range(ROWS):
            for col in range(COLS):
                piece = board.squares[row][col].piece
                if isinstance(piece, piece_type):
                    if piece.color == self.color:
                        black += table[row][col]
                    else:
                        if second_table is not None:
                            white += second_table[row][col]
                        else:
                            white += table[row][col]
        return black - white
    
    def evaluate(self, board):
        material_score = 0
        mobility_score = 0
        safety_score = 0
        
        pawns = self.get_piece_position_score(board, Pawn, AI.BLACK_PAWN_TABLE, second_table=AI.WHITE_PAWN_TABLE)
        knights = self.get_piece_position_score(board, Knight, AI.KNIGHT_TABLE)
        bishops = self.get_piece_position_score(board, Bishop, AI.BISHOP_TABLE)
        rooks = self.get_piece_position_score(board, Rook, AI.ROOK_TABLE)
        queens = self.get_piece_position_score(board, Queen, AI.QUEEN_TABLE)
        
        control_score = pawns + knights + bishops + rooks + queens

        # incorporate way to get piece scores for white and black
        for row in range(ROWS):
            for col in range(COLS):
                if board.squares[row][col].has_piece():
                    piece = board.squares[row][col].piece
                    value = piece.value
                    material_score -= value
                    board.possible_moves(piece, row, col)
                    
                    if piece.color == 'white':
                        if isinstance(piece, King):
                            # calculate safety score
                            safety_score += board.attackers(piece)
                        mobility_score -= len(piece.moves)
                    else:
                        if isinstance(piece, King):
                            safety_score -= board.attackers(piece)
                        mobility_score += len(piece.moves)

        # need to determine weights for each factor
        material_weight = 2
        control_weight = 0.2
        mobility_weight = 0.02
        safety_weight = 1

        total_score = (material_score * material_weight + control_score * control_weight)
        # + mobility_score * mobility_weight + safety_score * safety_weight
        if total_score > self.best_score:
            self.material_score = material_score * material_weight
            self.control_score = control_score * control_weight
            # self.mobility_score = mobility_score * mobility_weight
            # self.safety_score = safety_score * safety_weight

        # return scores * weights
        return total_score
    