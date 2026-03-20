from board import Board
from player import Player
  
class Game:
    def __init__(self, king_player:Player, pawns_player:Player):
        self.king_player = king_player
        self.pawns_player = pawns_player
          
    def play_optimal_game(self, board: Board):
        history = []
        
        while True:
            moves = board.get_legal_moves()
            result =  board.is_terminal(moves)
            
            if result != 0:
                break
            
            if board.turn == board.KING:
                move = self.king_player.get_best_move(board)
                history.append(move)
            else:
                move = self.pawns_player.get_best_move(board)
                history.append(move)
                
            board.move_piece(*move)
            
        return history, result