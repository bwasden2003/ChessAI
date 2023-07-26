import pygame

from const import *
from board import Board
from dragger import Dragger
from config import Config
from square import Square


class Game:

    def __init__(self):
        self.next_player = 'white'
        self.hovered_square = None
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()

    def show_bg(self, surface):
        theme = self.config.theme

        for row in range(ROWS):
            for col in range(COLS):
                color = theme.bg.light if (
                    row + col) % 2 == 0 else theme.bg.dark
                rect = (col * SQUARE_SIZE, row * SQUARE_SIZE,
                        SQUARE_SIZE, SQUARE_SIZE)

                pygame.draw.rect(surface, color, rect)

                # board coordinates
                if col == 0:
                    color = theme.bg.dark if row % 2 == 0 else theme.bg.light

                    lbl = self.config.font.render(str(ROWS - row), 1, color)
                    lbl_pos = (5, 5 + row * SQUARE_SIZE)

                    surface.blit(lbl, lbl_pos)
                if row == 7:
                    color = theme.bg.dark if (
                        row + col) % 2 == 0 else theme.bg.light

                    lbl = self.config.font.render(
                        Square.get_alphacol(col), 1, color)
                    lbl_pos = (col * SQUARE_SIZE +
                               SQUARE_SIZE - 20, HEIGHT - 20)

                    surface.blit(lbl, lbl_pos)

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece

                    # show all pieces but the one being dragged (if there is one)
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80)
                        img = pygame.image.load(piece.texture)
                        img_center = col * SQUARE_SIZE + SQUARE_SIZE // 2, row * \
                            SQUARE_SIZE + SQUARE_SIZE // 2
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface):
        theme = self.config.theme

        if self.dragger.dragging:
            piece = self.dragger.piece

            # loop through possible moves
            for move in piece.moves:
                color = theme.moves.light if (
                    move.final.row + move.final.col) % 2 == 0 else theme.moves.dark
                rect = (move.final.col * SQUARE_SIZE, move.final.row *
                        SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(surface, color, rect)

    def show_last_move(self, surface):
        theme = self.config.theme

        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial, final]:
                color = theme.trace.light if (
                    pos.row + pos.col) % 2 == 0 else theme.trace.dark
                rect = (pos.col * SQUARE_SIZE, pos.row *
                        SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.hovered_square:
            color = (180, 180, 180)
            rect = (self.hovered_square.col * SQUARE_SIZE,
                    self.hovered_square.row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(surface, color, rect, width=3)

    def set_hover(self, row, col):
        self.hovered_square = self.board.squares[row][col]

    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def check_checkmate(self):
        self.board.checkmate(self.next_player)

    def change_theme(self):
        self.config.change_theme()

    def sound_effect(self, captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        self.__init__()
