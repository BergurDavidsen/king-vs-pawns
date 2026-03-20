import os
import time

from board import Board
from game import Game
from human_player import HumanPlayer
from minimax_player import MinimaxPlayer
from random_player import RandomPlayer
from renderer import render
from svg_to_gif import create_gif

def explore_states(board:Board, seen_states):
    state = (tuple(board.board), board.turn)

    if state in seen_states:
        return

    seen_states.add(state)

    moves = board.get_legal_moves()

    for move in moves:
        new_board = board.copy()
        new_board.move_piece(*move)

        explore_states(new_board, seen_states)

def get_state_space_size():
    b = Board()
    
    # place king
    b.set_piece(0, 3, b.KING)

    # place pawns
    b.set_piece(0, 7, b.PAWN)
    b.set_piece(2, 7, b.PAWN)
    b.set_piece(4, 7, b.PAWN)
    b.set_piece(6, 7, b.PAWN)

    b.print_board()

    seen_states = set()
    
    explore_states(b, seen_states)
    
    print("Total states:", len(seen_states))

def to_square(pos):
    x, y = pos
    file = chr(ord('a') + x)
    rank = str(y + 1)
    return file + rank

def moves_to_notation(history):
    moves_str = []

    for i, (f, t) in enumerate(history):
        move_str = f"{to_square(f)}->{to_square(t)}"
        
        if i % 2 == 0:
            moves_str.append(f"{i//2 + 1}. {move_str}")
        else:
            moves_str[-1] += f" {move_str}"

    return " ".join(moves_str)

def main():
    b = Board()
    king_player = MinimaxPlayer("minimax")
    pawns_player = MinimaxPlayer("minimax")
    
    g = Game(king_player, pawns_player)
    
    b.reset_board()

    start = time.time()
    history, result = g.play_optimal_game(b)
    end = time.time()
    
    print(moves_to_notation(history))
    
    print(f"{pawns_player.name if result==-1 else king_player.name} wins\nCompute time: {round(end-start, 3)}ms")
    b.reset_board()
    
    frames, out_dir = render(b, history)
    
    # png_files = convert_svgs_to_pngs(frames, out_dir)
    
    # create_gif(out_dir, os.path.join(out_dir, "game.gif"))
        
if __name__ == "__main__":
    main()
