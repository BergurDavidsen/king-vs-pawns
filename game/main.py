import os
import time

from game.board import Board
from game.game import Game
from game.players.minimax_player import MinimaxPlayer
from game.players.random_player import RandomPlayer


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
    king_player = RandomPlayer("King")
    pawns_player = MinimaxPlayer("Pawns")
    
    #king_player.set_q_table("chess_variant_qtable.json")
    #pawns_player.set_q_table("chess_variant_qtable.json")
    
    g = Game(king_player, pawns_player)
    
    b.reset_board()
    
    b.move_piece((3, 0), (4,1))
    
    b.print_board()
    
    b.undo()
    
    print()
    
    b.print_board()


    # start = time.time()
    # history, result = g.play_optimal_game(b)
    # end = time.time()
    
    # print(moves_to_notation(history))
    
    # print(f"{pawns_player.name if result<0 else king_player.name} wins\nCompute time: {round(end-start, 3)}ms")
    # #pawns_player.save_memo()
    # b.reset_board()
    
    # frames, out_dir = render(b, history)
    
    # png_files = convert_svgs_to_pngs(frames, out_dir)
    
    # create_gif(out_dir, os.path.join(out_dir, "game.gif"))
        
if __name__ == "__main__":
    main()
