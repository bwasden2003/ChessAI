import pygame
import sys

from const import *
from game import Game
from square import Square
from move import Move
from ai import AI
import copy
import threading
import numpy as np

class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Chess')
        self.game = Game()
        self.ai = AI(self.game, 'black')

    def mainloop(self):

        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger
        done = False

        while not done:
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_hover(screen)

            if game.next_player == 'black':
                pygame.display.update()
                temp_board = copy.deepcopy(board)
                ai_thread = self.ai.calculate_move(temp_board, 2)
                while ai_thread.is_alive():
                    if self.ai.best_move is not None:
                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)
                        game.show_hover(screen)
                        self.ai.show_best_move(screen)
                        pygame.display.update()
                    pygame.time.wait(25)

                move = self.ai.best_move
                self.ai.best_move = None
                piece = board.squares[move.initial.row][move.initial.col].piece
                board.possible_moves(piece, move.initial.row, move.initial.col)
                if board.valid_move(piece, move):
                    captured = board.squares[move.final.row][move.final.col].has_piece(
                    )
                    board.move(piece, move)
                    board.set_true_en_passant(piece)
                    # play sound
                    game.sound_effect(captured)

                    game.show_bg(screen)
                    game.show_pieces(screen)

                    game.next_turn()
                    if board.is_checkmate(game.next_player):
                        font = pygame.font.SysFont('calibri', 75, True, False)
                        text = font.render("Checkmate!", True, (255, 0, 0))
                        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                        screen.blit(text, text_rect.topleft)
                        pygame.display.flip()
                        pygame.time.wait(5000)
                        done = True

            else:
                if dragger.dragging:
                    dragger.update_blit(screen)

                for event in pygame.event.get():

                    # click
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        dragger.update_mouse(event.pos)

                        clicked_row = dragger.mouseY // SQUARE_SIZE
                        clicked_col = dragger.mouseX // SQUARE_SIZE

                        if board.squares[clicked_row][clicked_col].has_piece():
                            piece = board.squares[clicked_row][clicked_col].piece
                            if piece.color == game.next_player:
                                board.possible_moves(
                                    piece, clicked_row, clicked_col, bool=True)
                                dragger.save_initial(event.pos)
                                dragger.drag_piece(piece)

                                game.show_bg(screen)
                                game.show_moves(screen)
                                game.show_pieces(screen)

                    # mouse motion
                    elif event.type == pygame.MOUSEMOTION:
                        hovered_row = event.pos[1] // SQUARE_SIZE
                        hovered_col = event.pos[0] // SQUARE_SIZE

                        game.set_hover(hovered_row, hovered_col)

                        if dragger.dragging:
                            dragger.update_mouse(event.pos)

                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)
                            game.show_hover(screen)

                            dragger.update_blit(screen)

                    # click release
                    elif event.type == pygame.MOUSEBUTTONUP:

                        if dragger.dragging:
                            dragger.update_mouse(event.pos)
                            new_row = dragger.mouseY // SQUARE_SIZE
                            new_col = dragger.mouseX // SQUARE_SIZE

                            initial = Square(dragger.initial_row,
                                             dragger.initial_col)
                            final = Square(new_row, new_col)
                            move = Move(initial, final)

                            if board.valid_move(dragger.piece, move):
                                captured = board.squares[new_row][new_col].has_piece(
                                )

                                board.move(dragger.piece, move)
                                board.set_true_en_passant(dragger.piece)
                                # play sound
                                game.sound_effect(captured)

                                game.show_bg(screen)
                                game.show_pieces(screen)
                                pygame.display.update()

                                game.next_turn()
                                if board.is_checkmate(game.next_player):
                                    font = pygame.font.SysFont('calibri', 75, True, False)
                                    text = font.render("Checkmate!", True, (255, 0, 0))
                                    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                                    screen.blit(text, text_rect.topleft)
                                    pygame.display.flip()
                                    pygame.time.wait(5000)
                                    done = True

                        dragger.undrag_piece()

                    # key press
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_t:
                            game.change_theme()

                        elif event.key == pygame.K_r:
                            game.reset()
                            game = self.game
                            board = self.game.board
                            dragger = self.game.dragger

                    # quit app
                    elif event.type == pygame.QUIT:
                        self.ai.save_transposition_table()
                        pygame.quit()
                        sys.exit()

            pygame.display.update()


main = Main()
main.mainloop()
