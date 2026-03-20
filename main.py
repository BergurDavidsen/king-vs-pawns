import time

from engine import minimax, play_optimal_game
from game import Board
from renderer import render

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
    
    b.reset_board()
    # place king
    b.set_piece(3, 0, b.KING)

    # place pawns
    b.set_piece(0, 7, b.PAWN)
    b.set_piece(2, 7, b.PAWN)
    b.set_piece(4, 7, b.PAWN)
    b.set_piece(6, 7, b.PAWN)

    b.print_board()

    start = time.time()
    history, result = play_optimal_game(b)
    end = time.time()
    
    print(moves_to_notation(history))
    
    print(f"{"Pawns win" if result==-1 else "King wins"}\nCompute time: {round(end-start, 3)}ms")
    b.reset_board()
    render(b, history)
        
        
if __name__ == "__main__":
    main()
