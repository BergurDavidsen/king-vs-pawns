from flask import Flask, render_template, jsonify, request, session
import os

from game import Board
from minimax_player import MinimaxPlayer


app = Flask(__name__)
app.secret_key = os.urandom(24) # Needed for session

board = Board()
ai = MinimaxPlayer("AI")

@app.route('/')
def index():
    board.reset_board()
    return render_template('index.html')

@app.route('/select_side', methods=['POST'])
def select_side():
    side = request.json.get('side') # 2 for King, 1 for Pawns
    session['human_side'] = int(side)
    board.reset_board()
    
    # If human is Pawns, AI (King) moves first
    if session['human_side'] == board.PAWN:
        ai_move = ai.get_best_move(board)
        if ai_move:
            board.move_piece(*ai_move)
            
    return get_state()

@app.route('/evaluate', methods=['GET'])
def evaluate():
    # compute evaluation from current board
    minimax = MinimaxPlayer("minimax")

    value = minimax.minimax(board)
    best_move = minimax.get_best_move(board)

    return jsonify({
        "evaluation": value,
        "best_move": best_move
    })
@app.route('/move', methods=['POST'])
def move():
    if 'human_side' not in session:
        return jsonify({'error': 'Select a side first'}), 400
    
    data = request.json
    from_pos = tuple(data['from'])
    to_pos = tuple(data['to'])
    
    # 1. Check if it's actually the human's turn
    if board.turn != session['human_side']:
        return get_state()

    # 2. Check if the human is moving their own piece
    piece_at_src = board.get_piece(from_pos[0], from_pos[1])
    if piece_at_src != session['human_side']:
        return get_state()

    # 3. Execute Human Move
    if board.move_piece(from_pos, to_pos):
        # 4. Check if game ended
        res = board.is_terminal(board.get_legal_moves())
        if res == 0:
            # 5. Trigger AI Move
            ai_move = ai.get_best_move(board)
            if ai_move:
                board.move_piece(*ai_move)
                
    return get_state()

@app.route('/state', methods=['GET'])
def get_state():
    moves = board.get_legal_moves()
    winner = board.is_terminal(moves)
    return jsonify({
        'fen': board.to_fen(),
        'turn': board.turn,
        'winner': winner,
        'human_side': session.get('human_side')
    })
if __name__ == '__main__':
    app.run(debug=True)
