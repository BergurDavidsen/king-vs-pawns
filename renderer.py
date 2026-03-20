import chess
import chess.svg
from game import Board

def render(b: Board, history):
    
    for i, move in enumerate(history):
        b.move_piece(*move)

        fen = b.to_fen()
        board = chess.Board(fen)
        svg = chess.svg.board(board=board)

        with open(f"board_images/frame_{i}.svg", "w") as f:
            f.write(svg)
    