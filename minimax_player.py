import math

from game import Board
from player import Player


class MinimaxPlayer(Player):
    
    
    MEMO = {}
        
    def minimax(self, board: Board):
        state = (tuple(board.board), board.turn)
        
        if state in self.MEMO:
            return self.MEMO[state]
        
        moves = board.get_legal_moves()
        result = board.is_terminal(moves)
        if result != 0:
            self.MEMO[state] = result
            return result
        
        
        if board.turn == board.KING:
            value = -math.inf
            for move in moves:
                b_copy = board.copy()
                b_copy.move_piece(*move)
                value = max(value, self.minimax(b_copy))
                
                if value == 1:
                    break
        else:
            value = math.inf
            for move in moves:
                b_copy = board.copy()
                b_copy.move_piece(*move)
                value = min(value, self.minimax(b_copy))
                    
                if value == -1:
                    break
        self.MEMO[state] = value
        return value

    def get_best_move(self, board):
        moves = board.get_legal_moves()
        best_move = None

        if board.turn == board.KING:
            best_value = -math.inf
            for move in moves:
                b_copy = board.copy()
                b_copy.move_piece(*move)

                val = self.minimax(b_copy)

                if val > best_value:
                    best_value = val
                    best_move = move
        else:
            best_value = math.inf
            for move in moves:
                b_copy = board.copy()
                b_copy.move_piece(*move)

                val = self.minimax(b_copy)

                if val < best_value:
                    best_value = val
                    best_move = move

        return best_move