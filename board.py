class Board:

    EMPTY = 0
    PAWN = 1
    KING = 2

    def __init__(self):
        self.board = [0]*64
        self.directions = [
            (1, 1), (1, -1),
            (-1, 1), (-1, -1)
        ]
        self.turn = self.KING
        self.history = []

        
    def index(self, x, y):
        return y*8+x

    def in_bounds(self, x, y):
        return 0 <= x < 8 and 0 <= y < 8
    
    def copy(self):
        new_board = Board()
        new_board.board = self.board[:]
        new_board.turn = self.turn
        return new_board
    
    def undo(self):
        if not self.history:
            return False
        
        old_board, old_turn = self.history.pop()
        self.board = old_board
        self.turn = old_turn
        return True
        
    def set_piece(self, x, y, v):
        self.board[self.index(x, y)] = v

    def get_piece(self, x, y):
        if not self.in_bounds(x, y):
            return None
        return self.board[self.index(x, y)]
    
    def find_king(self):
        for i in range(64):
            if self.board[i] == self.KING:
                return (i % 8, i // 8)
        return None

    def find_pawns(self):
        pawns = []
        for i in range(64):
            if self.board[i] == self.PAWN:
                pawns.append((i % 8, i // 8))
        return pawns
    
   
    def get_legal_moves(self):
        if self.turn == self.KING:
            return self.get_king_moves()
        else:
            return self.get_pawn_moves()
    
    def get_king_moves(self):
        moves = []
        
        # king
        kx, ky = self.find_king()
        
        for dx, dy in self.directions:
            nx, ny = kx + dx, ky + dy
            
            if self.in_bounds(nx, ny) and self.get_piece(nx, ny) == self.EMPTY:
                moves.append(((kx, ky), (nx, ny)))
        
        return moves
    def get_pawn_moves(self):
        moves = []
        for y in range(8):
            for x in range(8):
                if self.get_piece(x, y) == self.PAWN:
                    for dx, dy in [(1,-1), (-1, -1)]:
                        nx, ny = x+ dx, y+dy
                        
                        if self.in_bounds(nx, ny) and self.get_piece(nx, ny) == self.EMPTY:
                            moves.append(((x, y), (nx, ny)))
        return moves
        
    def move_piece(self, from_pos, to_pos):
        
        if (from_pos, to_pos) not in self.get_legal_moves():
            return False
        fx, fy = from_pos
        tx, ty = to_pos
        
        piece = self.get_piece(fx, fy)
        
        if piece == self.EMPTY:
            return False
        
        legal_moves = self.get_legal_moves()
        
        if (from_pos, to_pos) not in legal_moves:
            return False
        
        self.history.append((self.board[:], self.turn))
        
        self.set_piece(tx, ty, piece)
        self.set_piece(fx, fy, self.EMPTY)
        
        self.turn = self.PAWN if self.turn == self.KING else self.KING
        
        return True
    
    def is_terminal(self, moves):
        kx, ky = self.find_king()
        
        if ky == 7:
            return 100
        
        if len(moves)==0:
            return -100 if self.turn == self.KING else 100
        
        return 0
    def get_state(self):
        return(tuple(self.board), self.turn)
    
    def reset_board(self):
        b = Board()
        
        # king
        b.set_piece(3, 0, b.KING)
        
        # pawns
        b.set_piece(0, 7, b.PAWN)
        b.set_piece(2, 7, b.PAWN)
        b.set_piece(4, 7, b.PAWN)
        b.set_piece(6, 7, b.PAWN)
        
        self.board = b.board[:]
        self.turn = self.KING
        self.history = []

    def print_board(self):
       for y in range(7, -1, -1):
            row = []
            for x in range(8):
                row.append(self.get_piece(x, y))
            print(row)
            
    def to_fen(self):
        rows = []

        for y in range(7, -1, -1):
            empty = 0
            row = ""

            for x in range(8):
                piece = self.get_piece(x, y)

                if piece == self.EMPTY:
                    empty += 1
                else:
                    if empty > 0:
                        row += str(empty)
                        empty = 0

                    if piece == self.KING:
                        row += "K"
                    elif piece == self.PAWN:
                        row += "p"

            if empty > 0:
                row += str(empty)

            rows.append(row)

        # minimal FEN (rest doesn't matter for rendering)
        return "/".join(rows) + " w - - 0 1"