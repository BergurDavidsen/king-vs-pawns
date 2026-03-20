from game import Board
from player import Player

def to_square(pos):
    x, y = pos
    file = chr(ord('a') + x)
    rank = str(y + 1)
    return file + rank

class HumanPlayer(Player):

    def get_best_move(self, board:Board):
        board.print_board()
        moves = board.get_legal_moves()

        print("Chose a move")
        for i, (f, t) in enumerate(moves):
            print(f"{i}: {to_square(f)}->{to_square(t)}")
            
        choice = int(input("> "))
        
        return moves[choice]