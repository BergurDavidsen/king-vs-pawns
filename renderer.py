import chess
import chess.svg
from game import Board
import os
import time

def create_output_dir():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    path = f"outputs/run_{timestamp}"
    os.makedirs(path, exist_ok=True)
    return path

def render(b: Board, history):
    out_dir = create_output_dir()
    
    frames = []
    for i, move in enumerate(history):
        print("Applying:", move)

        success = b.move_piece(*move)

        print("Move success:", success)

        fen = b.to_fen()
        board = chess.Board(fen)
        svg = chess.svg.board(board=board)
        filename = os.path.join(out_dir, f"frame_{i:03d}.svg")
        with open(filename, "w") as f:
            f.write(svg)
        frames.append(filename)
    return frames, out_dir
    