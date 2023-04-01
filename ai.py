import numpy

class Move:

    def __init__(self, xfrom, yfrom, xto, yto):
        self.xfrom = xfrom
        self.yfrom = yfrom
        self.xto = xto
        self.yto = yto

    # Returns true iff (xfrom,yfrom) and (xto,yto) are the same.
    def equals(self, other_move):
        return self.xfrom == other_move.xfrom and self.yfrom == other_move.yfrom and self.xto == other_move.xto and self.yto == other_move.yto

    def to_string(self):
        return "(" + str(self.xfrom) + ", " + str(self.yfrom) + ") -> (" + str(self.xto) + ", " + str(self.yto) + ")"

class Piece():
    WHITE = "W"
    BLACK = "B"

    def __init__(self, x, y, color, piece_type, value):
        self.x = x
        self.y = y
        self.color = color
        self.piece_type = piece_type
        self.value = value

    # Returns all diagonal moves for this piece. This should therefore only
    # be used by the Bishop and Queen since they are the only pieces that can
    # move diagonally.
    def get_possible_diagonal_moves(self, board):
        moves = []

        for i in range(1, 8):
            if (not board.in_bounds(self.x + i, self.y + i)):
                break

            piece = board.get_piece(self.x + i, self.y + i)
            moves.append(self.get_move(board, self.x + i, self.y + i))
            if (piece != 0):
                break

        for i in range(1, 8):
            if (not board.in_bounds(self.x + i, self.y - i)):
                break

            piece = board.get_piece(self.x + i, self.y - i)
            moves.append(self.get_move(board, self.x + i, self.y - i))
            if (piece != 0):
                break

        for i in range(1, 8):
            if (not board.in_bounds(self.x - i, self.y - i)):
                break

            piece = board.get_piece(self.x - i, self.y - i)
            moves.append(self.get_move(board, self.x - i, self.y - i))
            if (piece != 0):
                break

        for i in range(1, 8):
            if (not board.in_bounds(self.x - i, self.y + i)):
                break

            piece = board.get_piece(self.x - i, self.y + i)
            moves.append(self.get_move(board, self.x - i, self.y + i))
            if (piece != 0):
                break

        return self.remove_null_from_list(moves)

    # Returns all horizontal moves for this piece. This should therefore only
    # be used by the Rooks and Queen since they are the only pieces that can
    # move horizontally.
    def get_possible_horizontal_moves(self, board):
        moves = []

        # Moves to the right of the piece.
        for i in range(1, 8 - self.x):
            piece = board.get_piece(self.x + i, self.y)
            moves.append(self.get_move(board, self.x + i, self.y))

            if (piece != 0):
                break

        # Moves to the left of the piece.
        for i in range(1, self.x + 1):
            piece = board.get_piece(self.x - i, self.y)
            moves.append(self.get_move(board, self.x - i, self.y))
            if (piece != 0):
                break

        # Downward moves.
        for i in range(1, 8 - self.y):
            piece = board.get_piece(self.x, self.y + i)
            moves.append(self.get_move(board, self.x, self.y + i))
            if (piece != 0):
                break

        # Upward moves.
        for i in range(1, self.y + 1):
            piece = board.get_piece(self.x, self.y - i)
            moves.append(self.get_move(board, self.x, self.y - i))
            if (piece != 0):
                break

        return self.remove_null_from_list(moves)

    # Returns a Move object with (xfrom, yfrom) set to the piece current position.
    # (xto, yto) is set to the given position. If the move is not valid 0 is returned.
    # A move is not valid if it is out of bounds, or a piece of the same color is
    # being eaten.
    def get_move(self, board, xto, yto):
        move = 0
        if (board.in_bounds(xto, yto)):
            piece = board.get_piece(xto, yto)
            if (piece != 0):
                if (piece.color != self.color):
                    move = Move(self.x, self.y, xto, yto)
            else:
                move = Move(self.x, self.y, xto, yto)
        return move

    # Returns the list of moves cleared of all the 0's.
    def remove_null_from_list(self, l):
        return [move for move in l if move != 0]

    def to_string(self):
        return self.color + self.piece_type + " "


class Rook(Piece):
    PIECE_TYPE = "R"
    VALUE = 500

    def __init__(self, x, y, color):
        super(Rook, self).__init__(x, y, color, Rook.PIECE_TYPE, Rook.VALUE)

    def get_possible_moves(self, board):
        return self.get_possible_horizontal_moves(board)

    def clone(self):
        return Rook(self.x, self.y, self.color)


class Knight(Piece):
    PIECE_TYPE = "N"
    VALUE = 320

    def __init__(self, x, y, color):
        super(Knight, self).__init__(x, y, color, Knight.PIECE_TYPE, Knight.VALUE)

    def get_possible_moves(self, board):
        moves = []

        moves.append(self.get_move(board, self.x + 2, self.y + 1))
        moves.append(self.get_move(board, self.x - 1, self.y + 2))
        moves.append(self.get_move(board, self.x - 2, self.y + 1))
        moves.append(self.get_move(board, self.x + 1, self.y - 2))
        moves.append(self.get_move(board, self.x + 2, self.y - 1))
        moves.append(self.get_move(board, self.x + 1, self.y + 2))
        moves.append(self.get_move(board, self.x - 2, self.y - 1))
        moves.append(self.get_move(board, self.x - 1, self.y - 2))

        return self.remove_null_from_list(moves)

    def clone(self):
        return Knight(self.x, self.y, self.color)


class Bishop(Piece):
    PIECE_TYPE = "B"
    VALUE = 330

    def __init__(self, x, y, color):
        super(Bishop, self).__init__(x, y, color, Bishop.PIECE_TYPE, Bishop.VALUE)

    def get_possible_moves(self, board):
        return self.get_possible_diagonal_moves(board)

    def clone(self):
        return Bishop(self.x, self.y, self.color)


class Queen(Piece):
    PIECE_TYPE = "Q"
    VALUE = 900

    def __init__(self, x, y, color):
        super(Queen, self).__init__(x, y, color, Queen.PIECE_TYPE, Queen.VALUE)

    def get_possible_moves(self, board):
        diagonal = self.get_possible_diagonal_moves(board)
        horizontal = self.get_possible_horizontal_moves(board)
        return horizontal + diagonal

    def clone(self):
        return Queen(self.x, self.y, self.color)


class King(Piece):
    PIECE_TYPE = "K"
    VALUE = 20000

    def __init__(self, x, y, color):
        super(King, self).__init__(x, y, color, King.PIECE_TYPE, King.VALUE)

    def get_possible_moves(self, board):
        moves = []

        moves.append(self.get_move(board, self.x + 1, self.y))
        moves.append(self.get_move(board, self.x + 1, self.y + 1))
        moves.append(self.get_move(board, self.x, self.y + 1))
        moves.append(self.get_move(board, self.x - 1, self.y + 1))
        moves.append(self.get_move(board, self.x - 1, self.y))
        moves.append(self.get_move(board, self.x - 1, self.y - 1))
        moves.append(self.get_move(board, self.x, self.y - 1))
        moves.append(self.get_move(board, self.x + 1, self.y - 1))

        moves.append(self.get_castle_kingside_move(board))
        moves.append(self.get_castle_queenside_move(board))

        return self.remove_null_from_list(moves)

    # Only checks for castle kingside
    def get_castle_kingside_move(self, board):
        # Are we looking at a valid rook
        piece_in_corner = board.get_piece(self.x + 3, self.y)
        if (piece_in_corner == 0 or piece_in_corner.piece_type != Rook.PIECE_TYPE):
            return 0

        # If the rook in the corner is not our color we cannot castle (duh).
        if (piece_in_corner.color != self.color):
            return 0

        # If the king has moved, we cannot castle
        if (self.color == Piece.WHITE and board.white_king_moved):
            return 0

        if (self.color == Piece.BLACK and board.black_king_moved):
            return 0

        # If there are pieces in between the king and rook we cannot castle
        if (board.get_piece(self.x + 1, self.y) != 0 or board.get_piece(self.x + 2, self.y) != 0):
            return 0

        return Move(self.x, self.y, self.x + 2, self.y)

    def get_castle_queenside_move(self, board):
        # Are we looking at a valid rook
        piece_in_corner = board.get_piece(self.x - 4, self.y)
        if (piece_in_corner == 0 or piece_in_corner.piece_type != Rook.PIECE_TYPE):
            return 0

        # If the rook in the corner is not our color we cannot castle (duh).
        if (piece_in_corner.color != self.color):
            return 0

        # If the king has moved, we cannot castle
        if (self.color == Piece.WHITE and board.white_king_moved):
            return 0

        if (self.color == Piece.BLACK and board.black_king_moved):
            return 0

        # If there are pieces in between the king and rook we cannot castle
        if (board.get_piece(self.x - 1, self.y) != 0 or board.get_piece(self.x - 2, self.y) != 0 or board.get_piece(
                self.x - 3, self.y) != 0):
            return 0

        return Move(self.x, self.y, self.x - 2, self.y)

    def clone(self):
        return King(self.x, self.y, self.color)


class Pawn(Piece):
    PIECE_TYPE = "P"
    VALUE = 100

    def __init__(self, x, y, color):
        super(Pawn, self).__init__(x, y, color, Pawn.PIECE_TYPE, Pawn.VALUE)

    def is_starting_position(self):
        if (self.color == Piece.BLACK):
            return self.y == 1
        else:
            return self.y == 8 - 2

    def get_possible_moves(self, board):
        moves = []

        # Direction the pawn can move in.
        direction = -1
        if (self.color == Piece.BLACK):
            direction = 1

        # The general 1 step forward move.
        if (board.get_piece(self.x, self.y + direction) == 0):
            moves.append(self.get_move(board, self.x, self.y + direction))

        # The Pawn can take 2 steps as the first move.
        if (self.is_starting_position() and board.get_piece(self.x, self.y + direction) == 0 and board.get_piece(self.x,
                                                                                                                 self.y + direction * 2) == 0):
            moves.append(self.get_move(board, self.x, self.y + direction * 2))

        # Eating pieces.
        piece = board.get_piece(self.x + 1, self.y + direction)
        if (piece != 0):
            moves.append(self.get_move(board, self.x + 1, self.y + direction))

        piece = board.get_piece(self.x - 1, self.y + direction)
        if (piece != 0):
            moves.append(self.get_move(board, self.x - 1, self.y + direction))

        return self.remove_null_from_list(moves)

    def clone(self):
        return Pawn(self.x, self.y, self.color)

class Board:
    WIDTH = 8
    HEIGHT = 8

    def __init__(self, chesspieces, white_king_moved, black_king_moved):
        self.chesspieces = chesspieces
        self.white_king_moved = white_king_moved
        self.black_king_moved = black_king_moved

    @classmethod
    def clone(cls, chessboard):
        chesspieces = [[0 for x in range(Board.WIDTH)] for y in range(Board.HEIGHT)]
        for x in range(Board.WIDTH):
            for y in range(Board.HEIGHT):
                piece = chessboard.chesspieces[x][y]
                if (piece != 0):
                    chesspieces[x][y] = piece.clone()
        return cls(chesspieces, chessboard.white_king_moved, chessboard.black_king_moved)

    @classmethod
    def new(cls):
        chess_pieces = [[0 for x in range(Board.WIDTH)] for y in range(Board.HEIGHT)]
        # Create pawns.
        for x in range(Board.WIDTH):
            chess_pieces[x][Board.HEIGHT - 2] = Pawn(x, Board.HEIGHT - 2, Piece.WHITE)
            chess_pieces[x][1] = Pawn(x, 1, Piece.BLACK)

        # Create rooks.
        chess_pieces[0][Board.HEIGHT - 1] = Rook(0, Board.HEIGHT - 1, Piece.WHITE)
        chess_pieces[Board.WIDTH - 1][Board.HEIGHT - 1] = Rook(Board.WIDTH - 1, Board.HEIGHT - 1,
                                                                Piece.WHITE)
        chess_pieces[0][0] = Rook(0, 0, Piece.BLACK)
        chess_pieces[Board.WIDTH - 1][0] = Rook(Board.WIDTH - 1, 0, Piece.BLACK)

        # Create Knights.
        chess_pieces[1][Board.HEIGHT - 1] = Knight(1, Board.HEIGHT - 1, Piece.WHITE)
        chess_pieces[Board.WIDTH - 2][Board.HEIGHT - 1] = Knight(Board.WIDTH - 2, Board.HEIGHT - 1,
                                                                       Piece.WHITE)
        chess_pieces[1][0] = Knight(1, 0, Piece.BLACK)
        chess_pieces[Board.WIDTH - 2][0] = Knight(Board.WIDTH - 2, 0, Piece.BLACK)

        # Create Bishops.
        chess_pieces[2][Board.HEIGHT - 1] = Bishop(2, Board.HEIGHT - 1, Piece.WHITE)
        chess_pieces[Board.WIDTH - 3][Board.HEIGHT - 1] = Bishop(Board.WIDTH - 3, Board.HEIGHT - 1,
                                                                        Piece.WHITE)
        chess_pieces[2][0] = Bishop(2, 0, Piece.BLACK)
        chess_pieces[Board.WIDTH - 3][0] = Bishop(Board.WIDTH - 3, 0, Piece.BLACK)

        # Create King & Queen.
        chess_pieces[4][Board.HEIGHT - 1] = King(4, Board.HEIGHT - 1, Piece.WHITE)
        chess_pieces[3][Board.HEIGHT - 1] = Queen(3, Board.HEIGHT - 1, Piece.WHITE)
        chess_pieces[4][0] = King(4, 0, Piece.BLACK)
        chess_pieces[3][0] = Queen(3, 0, Piece.BLACK)

        return cls(chess_pieces, False, False)

    def get_possible_moves(self, color):
        moves = []
        for x in range(Board.WIDTH):
            for y in range(Board.HEIGHT):
                piece = self.chesspieces[x][y]
                if (piece != 0):
                    if (piece.color == color):
                        moves += piece.get_possible_moves(self)

        return moves

    def perform_move(self, move):
        piece = self.chesspieces[move.xfrom][move.yfrom]
        self.move_piece(piece, move.xto, move.yto)

        # If a pawn reaches the end, upgrade it to a queen.
        if (piece.piece_type == Pawn.PIECE_TYPE):
            if (piece.y == 0 or piece.y == Board.HEIGHT - 1):
                self.chesspieces[piece.x][piece.y] = Queen(piece.x, piece.y, piece.color)

        if (piece.piece_type == King.PIECE_TYPE):
            # Mark the king as having moved.
            if (piece.color == Piece.WHITE):
                self.white_king_moved = True
            else:
                self.black_king_moved = True

            # Check if king-side castling
            if (move.xto - move.xfrom == 2):
                rook = self.chesspieces[piece.x + 1][piece.y]
                self.move_piece(rook, piece.x + 1, piece.y)
            # Check if queen-side castling
            if (move.xto - move.xfrom == -2):
                rook = self.chesspieces[piece.x - 2][piece.y]
                self.move_piece(rook, piece.x + 1, piece.y)

    def move_piece(self, piece, xto, yto):
        self.chesspieces[piece.x][piece.y] = 0
        piece.x = xto
        piece.y = yto

        self.chesspieces[xto][yto] = piece

    # Returns if the given color is checked.
    def is_check(self, color):
        other_color = Piece.WHITE
        if (color == Piece.WHITE):
            other_color = Piece.BLACK

        for move in self.get_possible_moves(other_color):
            copy = Board.clone(self)
            copy.perform_move(move)

            king_found = False
            for x in range(Board.WIDTH):
                for y in range(Board.HEIGHT):
                    piece = copy.chesspieces[x][y]
                    if (piece != 0):
                        if (piece.color == color and piece.piece_type == King.PIECE_TYPE):
                            king_found = True

            if (not king_found):
                return True

        return False

    # Returns piece at given position or 0 if: No piece or out of bounds.
    def get_piece(self, x, y):
        if (not self.in_bounds(x, y)):
            return 0

        return self.chesspieces[x][y]

    def in_bounds(self, x, y):
        return (x >= 0 and y >= 0 and x < Board.WIDTH and y < Board.HEIGHT)

    def to_string(self):
        string = "    A  B  C  D  E  F  G  H\n"
        string += "    -----------------------\n"
        for y in range(Board.HEIGHT):
            string += str(8 - y) + " | "
            for x in range(Board.WIDTH):
                piece = self.chesspieces[x][y]
                if (piece != 0):
                    string += piece.to_string()
                else:
                    string += ". "
            string += "\n"





class Heuristics:

    # The tables denote the points scored for the position of the chess pieces on the board.

    PAWN_TABLE = numpy.array([
        [ 0,  0,  0,  0,  0,  0,  0,  0],
        [ 5, 10, 10,-20,-20, 10, 10,  5],
        [ 5, -5,-10,  0,  0,-10, -5,  5],
        [ 0,  0,  0, 20, 20,  0,  0,  0],
        [ 5,  5, 10, 25, 25, 10,  5,  5],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [ 0,  0,  0,  0,  0,  0,  0,  0]
    ])

    KNIGHT_TABLE = numpy.array([
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20,   0,   5,   5,   0, -20, -40],
        [-30,   5,  10,  15,  15,  10,   5, -30],
        [-30,   0,  15,  20,  20,  15,   0, -30],
        [-30,   5,  15,  20,  20,  15,   0, -30],
        [-30,   0,  10,  15,  15,  10,   0, -30],
        [-40, -20,   0,   0,   0,   0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -40, -50]
    ])

    BISHOP_TABLE = numpy.array([
        [-20, -10, -10, -10, -10, -10, -10, -20],
        [-10,   5,   0,   0,   0,   0,   5, -10],
        [-10,  10,  10,  10,  10,  10,  10, -10],
        [-10,   0,  10,  10,  10,  10,   0, -10],
        [-10,   5,   5,  10,  10,   5,   5, -10],
        [-10,   0,   5,  10,  10,   5,   0, -10],
        [-10,   0,   0,   0,   0,   0,   0, -10],
        [-20, -10, -10, -10, -10, -10, -10, -20]
    ])

    ROOK_TABLE = numpy.array([
        [ 0,  0,  0,  5,  5,  0,  0,  0],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [ 5, 10, 10, 10, 10, 10, 10,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  0]
    ])

    QUEEN_TABLE = numpy.array([
        [-20, -10, -10, -5, -5, -10, -10, -20],
        [-10,   0,   5,  0,  0,   0,   0, -10],
        [-10,   5,   5,  5,  5,   5,   0, -10],
        [  0,   0,   5,  5,  5,   5,   0,  -5],
        [ -5,   0,   5,  5,  5,   5,   0,  -5],
        [-10,   0,   5,  5,  5,   5,   0, -10],
        [-10,   0,   0,  0,  0,   0,   0, -10],
        [-20, -10, -10, -5, -5, -10, -10, -20]
    ])

    @staticmethod
    def evaluate(board):
        material = Heuristics.get_material_score(board)

        pawns = Heuristics.get_piece_position_score(board, Pawn.PIECE_TYPE, Heuristics.PAWN_TABLE)
        knights = Heuristics.get_piece_position_score(board, Knight.PIECE_TYPE, Heuristics.KNIGHT_TABLE)
        bishops = Heuristics.get_piece_position_score(board, Bishop.PIECE_TYPE, Heuristics.BISHOP_TABLE)
        rooks = Heuristics.get_piece_position_score(board, Rook.PIECE_TYPE, Heuristics.ROOK_TABLE)
        queens = Heuristics.get_piece_position_score(board, Queen.PIECE_TYPE, Heuristics.QUEEN_TABLE)

        return material + pawns + knights + bishops + rooks + queens

    # Returns the score for the position of the given type of piece.
    # A piece type can for example be: pieces.Pawn.PIECE_TYPE.
    # The table is the 2d numpy array used for the scoring. Example: Heuristics.PAWN_TABLE
    @staticmethod
    def get_piece_position_score(board, piece_type, table):
        white = 0
        black = 0
        for x in range(8):
            for y in range(8):
                piece = board.chesspieces[x][y]
                if (piece != 0):
                    if (piece.piece_type == piece_type):
                        if (piece.color == Piece.WHITE):
                            white += table[x][y]
                        else:
                            black += table[7 - x][y]

        return white - black

    @staticmethod
    def get_material_score(board):
        white = 0
        black = 0
        for x in range(8):
            for y in range(8):
                piece = board.chesspieces[x][y]
                if (piece != 0):
                    if (piece.color == Piece.WHITE):
                        white += piece.value
                    else:
                        black += piece.value

        return white - black

def get_ai_move(chessboard, invalid_moves):
        best_move = 0
        best_score = INFINITE
        for move in chessboard.get_possible_moves(Piece.BLACK):
            if (is_invalid_move(move, invalid_moves)):
                continue

            copy = Board.clone(chessboard)
            copy.perform_move(move)

            score = alphabeta(copy, 2, -INFINITE, INFINITE, True)
            if (score < best_score):
                best_score = score
                best_move = move

        # Checkmate.
        if (best_move == 0):
            return 0

        copy = Board.clone(chessboard)
        copy.perform_move(best_move)
        if (copy.is_check(Piece.BLACK)):
            invalid_moves.append(best_move)
            return get_ai_move(chessboard, invalid_moves)

        return best_move



INFINITE = 10000000


def is_invalid_move(move, invalid_moves):
    for invalid_move in invalid_moves:
        if (invalid_move.equals(move)):
            return True
    return False


def minimax(board, depth, maximizing):
    if (depth == 0):
        return Heuristics.evaluate(board)

    if (maximizing):
        best_score = -INFINITE
        for move in board.get_possible_moves(Piece.WHITE):
            copy = Board.clone(board)
            copy.perform_move(move)
            score = minimax(copy, depth-1, False)
            best_score = max(best_score, score)

        return best_score
    else:
        best_score = INFINITE
        for move in board.get_possible_moves(Piece.BLACK):
            copy = board.clone(board)
            copy.perform_move(move)
            score = minimax(copy, depth-1, True)
            best_score = min(best_score, score)
            return best_score


def alphabeta(chessboard, depth, a, b, maximizing):
    if (depth == 0):
        return Heuristics.evaluate(chessboard)

    if (maximizing):
        best_score = -INFINITE
        for move in chessboard.get_possible_moves(Piece.WHITE):
            copy = board.clone(chessboard)
            copy.perform_move(move)

            best_score = max(best_score, alphabeta(copy, depth-1, a, b, False))
            a = max(a, best_score)
            if (b <= a):
                break
        return best_score
    else:
        best_score = INFINITE
        for move in chessboard.get_possible_moves(Piece.BLACK):
            copy = board.clone(chessboard)
            copy.perform_move(move)

            best_score = min(best_score, alphabeta(copy, depth-1, a, b, True))
            b = min(b, best_score)
            if (b <= a):
                break
        return best_score

# Returns a move object based on the users input. Does not check if the move is valid.
def get_user_move(s):
    
    move_str = s
    temp=move_str[0]+move_str[1]+","+move_str[2]+move_str[3]
    
    
        
    

    try:
        xfrom = letter_to_xpos(move_str[0:1])
        yfrom = 8 - int(move_str[1:2]) # The board is drawn "upside down", so flip the y coordinate.
        xto = letter_to_xpos(move_str[2:3])
        yto = 8 - int(move_str[3:4]) # The board is drawn "upside down", so flip the y coordinate.
        return Move(xfrom, yfrom, xto, yto)
    except ValueError:
        print("Invalid format. Example: A2 A4")
        return get_user_move()

# Returns a valid move based on the users input.
def get_valid_user_move(board,s):
    while True:
        move = get_user_move(s)
        valid = False
        possible_moves = board.get_possible_moves(Piece.WHITE)
        # No possible moves
        if (not possible_moves):
            return 0

        for possible_move in possible_moves:
            if (move.equals(possible_move)):
                valid = True
                break

        if (valid):
            break
        else:
            return "invalid move"
    return move

# Converts a letter (A-H) to the x position on the chess board.
def letter_to_xpos(letter):
    letter = letter.upper()
    if letter == 'A':
        return 0
    if letter == 'B':
        return 1
    if letter == 'C':
        return 2
    if letter == 'D':
        return 3
    if letter == 'E':
        return 4
    if letter == 'F':
        return 5
    if letter == 'G':
        return 6
    if letter == 'H':
        return 7

    raise ValueError("Invalid letter.")

#
# Entry point.
#

board=Board.new()

def amove(s,board):
    if board=="-1":
        board = Board.new()
    
    move = get_valid_user_move(board,s)
    if (move == 0):
        if (board.is_check(Piece.WHITE)):
            return("Checkmate. Black Wins.")
            
        else:
            return("Stalemate.")
        
    if move!="invalid move":    
        board.perform_move(move)
    else:
        return "invalid move"

    
    

    ai_move = get_ai_move(board, [])
    if (ai_move == 0):
        if (b.is_check(Piece.BLACK)):
            return("Checkmate. White wins.")
            
        else:
            return("Stalemate.")
            
    kl=[["a8","a7","a6","a5","a4","a3","a2","a1"],["b8","b7","b6","b5","b4","b3","b2","b1"],["c8","c7","c6","c5","c4","c3","c2","c1"],["d8","d7","d6","d5","d4","d3","d2","d1"],["e8","e7","e6","e5","e4","e3","e2","e1"],["f8","f7","f6","f5","f4","f3","f2","f1"],["g8","g7","g6","g5","g4","g3","g2","g1"],["h8","h7","h6","h5","h4","h3","h2","h1"]]    
    
        
    board.perform_move(ai_move)
    s=kl[int(ai_move.to_string()[1])][int(ai_move.to_string()[4])]
    s+=kl[int(ai_move.to_string()[11])][int(ai_move.to_string()[14])]
    h=[s,board]
    return h

