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
    data = request.json
    side = data.get('side') # 2, 1, or 'pvp'
    board.reset_board()
    
    if side == 'pvp':
        session['human_side'] = 'pvp'
    else:
        session['human_side'] = int(side)
        # If human plays Pawns, AI (King) moves first
        if session['human_side'] == board.PAWN:
            ai_move = ai.get_best_move(board)
            if ai_move:
                board.move_piece(*ai_move)
            
    return get_state()

@app.route('/legal_moves', methods=['POST'])
def legal_moves():
    data = request.json
    x, y = data["pos"]

    moves = board.get_legal_moves()

    legal = [
        m for m in moves if m[0] == (x, y)
    ]

    return jsonify({
        "moves": [m[1] for m in legal]
    })

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
    is_pvp = session.get('human_side') == 'pvp'
    
    # In PvP, any side can move. In Solo, check turn.
    if not is_pvp and board.turn != session['human_side']:
        return get_state()

    # Execute Move
    if board.move_piece(from_pos, to_pos):
        res = board.is_terminal(board.get_legal_moves())
        # Only trigger AI if NOT in PvP mode and game isn't over
        if not is_pvp and res == 0:
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
