import math

from game import Board
  
memo = {}      
def minimax(board: Board):
    state = (tuple(board.board), board.turn)
    
    if state in memo:
        return memo[state]
    
    moves = board.get_legal_moves()
    result = board.is_terminal(moves)
    if result != 0:
        memo[state] = result
        return result
    
    
    if board.turn == board.KING:
        value = -math.inf
        for move in moves:
            b_copy = board.copy()
            b_copy.move_piece(*move)
            value = max(value, minimax(b_copy))
            
            if value == 1:
                break
    else:
        value = math.inf
        for move in moves:
            b_copy = board.copy()
            b_copy.move_piece(*move)
            value = min(value, minimax(b_copy))
                
            if value == -1:
                break
    memo[state] = value
    return value

def get_best_move(board):
    moves = board.get_legal_moves()
    best_move = None

    if board.turn == board.KING:
        best_value = -math.inf
        for move in moves:
            b_copy = board.copy()
            b_copy.move_piece(*move)

            val = minimax(b_copy)

            if val > best_value:
                best_value = val
                best_move = move
    else:
        best_value = math.inf
        for move in moves:
            b_copy = board.copy()
            b_copy.move_piece(*move)

            val = minimax(b_copy)

            if val < best_value:
                best_value = val
                best_move = move

    return best_move

def play_optimal_game(board: Board):
    history = []
    
    while True:
        moves = board.get_legal_moves()
        result =  board.is_terminal(moves)
        
        if result != 0:
            break
        
        move = get_best_move(board)
        history.append(move)
        
        board.move_piece(*move)
        
    return history, result