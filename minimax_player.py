import math
import pickle
import os
import time
from game import Board
from player import Player

class MinimaxPlayer(Player):
    def __init__(self, name, memo_file="minimax_memo.pkl"):
        super().__init__(name)
        self.memo_file = memo_file
        self.MEMO = {}
        self.load_memo()

    def get_state_key(self, board: Board):
        return (tuple(board.board), board.turn)

    def load_memo(self):
        if os.path.exists(self.memo_file):
            print(f"Loading knowledge base...")
            try:
                start = time.time()
                with open(self.memo_file, "rb") as f:
                    self.MEMO = pickle.load(f)
                end = time.time()
                print(f"Loaded {len(self.MEMO)} states in {round(end-start, 3)}ms.")
            except:
                self.MEMO = {}
        else:
            self.MEMO = {}

    def save_memo(self):
        with open(self.memo_file, "wb") as f:
            pickle.dump(self.MEMO, f, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"Saved {len(self.MEMO)} states.")

    def minimax(self, board: Board):
        state_key = self.get_state_key(board)

        if state_key in self.MEMO:
            return self.MEMO[state_key]

        moves = board.get_legal_moves()
        result = board.is_terminal(moves)

        if result != 0:
            return result

        if board.turn == board.KING:
            best = -math.inf
            for move in moves:
                b_copy = board.copy()
                b_copy.move_piece(*move)

                val = self.minimax(b_copy)

                # 👇 subtract 1 to prefer faster wins
                if val > 0:
                    val -= 1
                elif val < 0:
                    val += 1

                best = max(best, val)

        else:
            best = math.inf
            for move in moves:
                b_copy = board.copy()
                b_copy.move_piece(*move)

                val = self.minimax(b_copy)

                # 👇 same logic
                if val > 0:
                    val -= 1
                elif val < 0:
                    val += 1

                best = min(best, val)

        self.MEMO[state_key] = best
        return best

    def get_best_move(self, board):
        moves = board.get_legal_moves()
        if not moves: return None
            
        best_move = None
        # Start search at depth 0
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