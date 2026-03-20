from game import Board
from player import Player
import random

class RandomPlayer(Player):

    def get_best_move(self, board:Board):
        moves = board.get_legal_moves()
        return random.choice(moves)