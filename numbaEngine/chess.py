from typing import Tuple
import numpy as np
from queue import LifoQueue
from numba import njit

# Constants
WHITE = 1
BLACK = -1
PAWN = 1
KNIGHT = 2
BISHOP = 3
ROOK = 4
QUEEN = 5
KING = 6

class Move:
    def __init__(self):
        self.to_square = None
        self.from_square = None
        self.promotion = None

    def __str__(self):
        if self.from_square is None or self.to_square is None:
            return "Invalid move"
        def square_to_notation(square):
            x, y = square
            file = chr(ord('a') + y)
            rank = str(8 - x)
            return file + rank
        from_notation = square_to_notation(self.from_square)
        to_notation = square_to_notation(self.to_square)
        if self.promotion:
            promotion_piece = ""
            if self.promotion == QUEEN:
                promotion_piece = "q"
            elif self.promotion == ROOK:
                promotion_piece = "r"
            elif self.promotion == BISHOP:
                promotion_piece = "b"
            elif self.promotion == KNIGHT:
                promotion_piece = "n"
            return from_notation + to_notation + promotion_piece
        else:
            return from_notation + to_notation

class Piece:
    def __init__(self, color=None, piece_type=None):
        self.color = color
        self.piece_type = piece_type

@njit
def is_square_attacked_numba(board, square_x, square_y, enemy_color):
    # Check pawn attacks
    pawn_directions = [(1, -1), (1, 1)] if enemy_color == WHITE else [(-1, -1), (-1, 1)]
    for dx, dy in pawn_directions:
        x = square_x + dx
        y = square_y + dy
        if 0 <= x < 8 and 0 <= y < 8:
            if board[x, y] == PAWN * enemy_color:
                return True

    # Check knight attacks
    knight_moves = [(-2, -1), (-1, -2), (1, -2), (2, -1),
                    (2, 1), (1, 2), (-1, 2), (-2, 1)]
    for dx, dy in knight_moves:
        x = square_x + dx
        y = square_y + dy
        if 0 <= x < 8 and 0 <= y < 8:
            if board[x, y] == KNIGHT * enemy_color:
                return True

    # Check king attacks
    king_moves = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1), (0, 1),
                  (1, -1), (1, 0), (1, 1)]
    for dx, dy in king_moves:
        x = square_x + dx
        y = square_y + dy
        if 0 <= x < 8 and 0 <= y < 8:
            if board[x, y] == KING * enemy_color:
                return True

    # Check sliding pieces
    sliding_directions = [
        (BISHOP, [(-1, -1), (-1, 1), (1, -1), (1, 1)]),
        (ROOK, [(-1, 0), (1, 0), (0, -1), (0, 1)]),
        (QUEEN, [(-1, -1), (-1, 1), (1, -1), (1, 1),
                 (-1, 0), (1, 0), (0, -1), (0, 1)])
    ]

    for piece_type, directions in sliding_directions:
        for dx, dy in directions:
            x, y = square_x + dx, square_y + dy
            while 0 <= x < 8 and 0 <= y < 8:
                if board[x, y] != 0:
                    if board[x, y] == piece_type * enemy_color:
                        return True
                    break
                x += dx
                y += dy

    return False

@njit
def is_move_legal_numba(board, from_x, from_y, to_x, to_y, promotion_piece, color):
    board_copy = board.copy()
    moving_piece = board_copy[from_x, from_y]
    board_copy[to_x, to_y] = moving_piece
    board_copy[from_x, from_y] = 0

    if promotion_piece != 0:
        board_copy[to_x, to_y] = promotion_piece * color

    king_found = False
    king_x, king_y = -1, -1
    for x in range(8):
        for y in range(8):
            if board_copy[x, y] == KING * color:
                king_x, king_y = x, y
                king_found = True
                break
        if king_found:
            break

    if king_x == -1 or king_y == -1:
        return False

    return not is_square_attacked_numba(board_copy, king_x, king_y, -color)

@njit
def generate_pawn_moves(board, x, y, color):
    moves = []
    direction = -color
    start_row = 6 if color == WHITE else 1
    promotion_row = 0 if color == WHITE else 7

    # Single move
    new_x = x + direction
    if 0 <= new_x < 8 and board[new_x, y] == 0:
        if new_x == promotion_row:
            for promo in [QUEEN, ROOK, BISHOP, KNIGHT]:
                moves.append((x, y, new_x, y, promo))
        else:
            moves.append((x, y, new_x, y, 0))

    # Double move
    if x == start_row and board[x + direction, y] == 0 and board[x + 2 * direction, y] == 0:
        new_x = x + 2 * direction
        moves.append((x, y, new_x, y, 0))

    # Captures
    for dy in (-1, 1):
        new_x = x + direction
        new_y = y + dy
        if 0 <= new_x < 8 and 0 <= new_y < 8:
            if board[new_x, new_y] * color < 0:
                if new_x == promotion_row:
                    for promo in [QUEEN, ROOK, BISHOP, KNIGHT]:
                        moves.append((x, y, new_x, new_y, promo))
                else:
                    moves.append((x, y, new_x, new_y, 0))

    return moves

@njit
def generate_knight_moves(board, x, y, color):
    moves = []
    knight_moves = [(-2, -1), (-1, -2), (1, -2), (2, -1),
                    (2, 1), (1, 2), (-1, 2), (-2, 1)]
    for dx, dy in knight_moves:
        new_x = x + dx
        new_y = y + dy
        if 0 <= new_x < 8 and 0 <= new_y < 8:
            if board[new_x, new_y] * color <= 0:
                moves.append((x, y, new_x, new_y, 0))
    return moves

@njit
def generate_sliding_moves(board, x, y, color, piece_type):
    moves = []
    if piece_type == BISHOP:
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    elif piece_type == ROOK:
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    elif piece_type == QUEEN:
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1),
                      (-1, 0), (1, 0), (0, -1), (0, 1)]
    else:
        return moves

    for dx, dy in directions:
        step = 1
        while True:
            new_x = x + dx * step
            new_y = y + dy * step
            if not (0 <= new_x < 8 and 0 <= new_y < 8):
                break
            target = board[new_x, new_y]
            if target * color > 0:
                break
            moves.append((x, y, new_x, new_y, 0))
            if target * color < 0:
                break
            step += 1
    return moves

@njit
def generate_king_moves(board, x, y, color):
    moves = []
    king_moves = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1), (0, 1),
                  (1, -1), (1, 0), (1, 1)]
    for dx, dy in king_moves:
        new_x = x + dx
        new_y = y + dy
        if 0 <= new_x < 8 and 0 <= new_y < 8:
            if board[new_x, new_y] * color <= 0:
                moves.append((x, y, new_x, new_y, 0))
    return moves

class Board:
    def __init__(self):
        self.turn = WHITE
        self._board = np.array([[-4,-2,-3,-5,-6,-3,-2,-4],
                               [-1,-1,-1,-1,-1,-1,-1,-1],
                               [0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0],
                               [1,1,1,1,1,1,1,1],
                               [4,2,3,5,6,3,2,4]], dtype=np.int64)
        self.event = LifoQueue()

    def reset(self):
        self.__init__()

    def set_fen(self, fen: str):
        piece_map = {
            'P': (WHITE, PAWN),
            'N': (WHITE, KNIGHT),
            'B': (WHITE, BISHOP),
            'R': (WHITE, ROOK),
            'Q': (WHITE, QUEEN),
            'K': (WHITE, KING),
            'p': (BLACK, PAWN),
            'n': (BLACK, KNIGHT),
            'b': (BLACK, BISHOP),
            'r': (BLACK, ROOK),
            'q': (BLACK, QUEEN),
            'k': (BLACK, KING)
        }
        self._board = np.zeros((8, 8), dtype=int)
        parts = fen.split(' ')
        piece_placement = parts[0]
        row = 0
        col = 0
        for char in piece_placement:
            if char == '/':
                row += 1
                col = 0
            elif char.isdigit():
                col += int(char)
            else:
                color, piece_type = piece_map[char]
                self._board[row, col] = piece_type if color == WHITE else -piece_type
                col += 1
        self.turn = WHITE if parts[1] == "w" else BLACK

    def push_uci(self, move: str):
        from_square = (8 - int(move[1]), ord(move[0]) - ord('a'))
        to_square = (8 - int(move[3]), ord(move[2]) - ord('a'))
        promotion = None
        if len(move) == 5:
            promotion = move[4].lower()
            promotion_map = {'q': QUEEN, 'r': ROOK, 'b': BISHOP, 'n': KNIGHT}
            promotion = promotion_map.get(promotion, None)
        piece = self._board[from_square[0], from_square[1]]
        if abs(piece) == KING and abs(from_square[1] - to_square[1]) == 2:
            if to_square[1] > from_square[1]:
                rook_from = (from_square[0], 7)
                rook_to = (from_square[0], 5)
            else:
                rook_from = (from_square[0], 0)
                rook_to = (from_square[0], 3)
            rook_piece = self._board[rook_from[0], rook_from[1]]
            self._board[rook_to[0], rook_to[1]] = rook_piece
            self._board[rook_from[0], rook_from[1]] = 0
        old_piece = self._board[to_square[0], to_square[1]]
        if old_piece != 0:
            self.event.put(old_piece)
        self._board[to_square[0], to_square[1]] = piece
        self._board[from_square[0], from_square[1]] = 0
        if np.sign(old_piece) == np.sign(piece):
            self._board[from_square[0], from_square[1]] = old_piece
        if promotion:
            self._board[to_square[0], to_square[1]] = promotion * self.turn
        self.turn = -self.turn

    def legal_moves(self):
        moves = []
        board = self._board
        color = self.turn
        for x in range(8):
            for y in range(8):
                piece = board[x, y]
                if piece == 0 or np.sign(piece) != color:
                    continue
                piece_type = abs(piece)
                if piece_type == PAWN:
                    pawn_moves = generate_pawn_moves(board, x, y, color)
                    for move in pawn_moves:
                        if is_move_legal_numba(board, move[0], move[1], move[2], move[3], move[4], color):
                            moves.append(move)
                elif piece_type == KNIGHT:
                    knight_moves = generate_knight_moves(board, x, y, color)
                    for move in knight_moves:
                        if is_move_legal_numba(board, move[0], move[1], move[2], move[3], 0, color):
                            moves.append(move)
                elif piece_type in [BISHOP, ROOK, QUEEN]:
                    sliding_moves = generate_sliding_moves(board, x, y, color, piece_type)
                    for move in sliding_moves:
                        if is_move_legal_numba(board, move[0], move[1], move[2], move[3], 0, color):
                            moves.append(move)
                elif piece_type == KING:
                    king_moves = generate_king_moves(board, x, y, color)
                    for move in king_moves:
                        if is_move_legal_numba(board, move[0], move[1], move[2], move[3], 0, color):
                            moves.append(move)
        for move_tuple in moves:
            move = Move()
            move.from_square = (move_tuple[0], move_tuple[1])
            move.to_square = (move_tuple[2], move_tuple[3])
            move.promotion = move_tuple[4] if move_tuple[4] != 0 else None
            yield move

    def _is_move_legal(self, move: Move, color: int):
        from_sq = move.from_square
        to_sq = move.to_square
        promotion = move.promotion if move.promotion else 0
        return is_move_legal_numba(
            self._board,
            from_sq[0], from_sq[1],
            to_sq[0], to_sq[1],
            promotion,
            color
        )

    def push(self, move: Move):
        self.event.put(move)
        self.push_uci(str(move))

    def pop(self):
        if self.event.empty():
            raise IndexError("No moves to pop")
        event = self.event.get()
        if isinstance(event, Move):
            last_move = self.retractMove(event)
        else:
            last_move = self.retractMove(self.event.get())
            self._board[last_move.to_square[0], last_move.to_square[1]] = event
        return last_move

    def is_numeric(self, ev) -> bool:
        attrs = ['__add__', '__sub__', '__mul__', '__truediv__', '__pow__']
        return all(hasattr(ev, attr) for attr in attrs)

    def retractMove(self, event):
        last_move = event
        from_sq = last_move.from_square
        to_sq = last_move.to_square
        moving_piece = self._board[to_sq[0], to_sq[1]]
        self._board[from_sq[0], from_sq[1]] = moving_piece
        self._board[to_sq[0], to_sq[1]] = 0
        if abs(moving_piece) == KING and abs(from_sq[1] - to_sq[1]) == 2:
            if to_sq[1] > from_sq[1]:
                rook_from = (from_sq[0], 5)
                rook_to = (from_sq[0], 7)
            else:
                rook_from = (from_sq[0], 3)
                rook_to = (from_sq[0], 0)
            rook_piece = self._board[rook_from[0], rook_from[1]]
            self._board[rook_to[0], rook_to[1]] = rook_piece
            self._board[rook_from[0], rook_from[1]] = 0
        if last_move.promotion:
            original_color = -self.turn
            self._board[from_sq[0], from_sq[1]] = PAWN * original_color
        self.turn = -self.turn
        return last_move

    def can_claim_draw(self):
        pieces = np.abs(self._board).flatten()
        if np.sum(pieces == PAWN) == 0 and np.sum(pieces == QUEEN) == 0 and np.sum(pieces == ROOK) == 0:
            if np.sum(pieces == BISHOP) + np.sum(pieces == KNIGHT) <= 1:
                return True
        return False

    def is_checkmate(self):
        king_position = None
        for x in range(8):
            for y in range(8):
                if self._board[x, y] == KING * -self.turn:
                    king_position = (x, y)
                    break
            if king_position:
                break
        if not self.is_square_attacked(king_position, self.turn):
            return False
        for move in self.legal_moves():
            original_piece = self._board[move.to_square[0], move.to_square[1]]
            self._board[move.to_square[0], move.to_square[1]] = self._board[move.from_square[0], move.from_square[1]]
            self._board[move.from_square[0], move.from_square[1]] = 0
            king_pos_new = move.to_square if move.from_square == king_position else king_position
            if not self.is_square_attacked(king_pos_new, self.turn):
                self._board[move.from_square[0], move.from_square[1]] = self._board[move.to_square[0], move.to_square[1]]
                self._board[move.to_square[0], move.to_square[1]] = original_piece
                return False
            self._board[move.from_square[0], move.from_square[1]] = self._board[move.to_square[0], move.to_square[1]]
            self._board[move.to_square[0], move.to_square[1]] = original_piece
        return True

    def is_square_attacked(self, square: Tuple, enemy_color: int):
        if square is None:
            return False
        return is_square_attacked_numba(self._board, square[0], square[1], enemy_color)

    def is_game_over(self):
        if self.is_checkmate():
            return True
        if not any(self.legal_moves()):
            return True
        if self.can_claim_draw():
            return True
        return False

    def piece_at(self, from_square: Tuple):
        return self._board[from_square[0], from_square[1]]

    def piece_map(self):
        piece_map = {}
        for x in range(8):
            for y in range(8):
                piece_value = self._board[x, y]
                if piece_value != 0:
                    piece_map[(x, y)] = piece_value
        return piece_map

if __name__ == "__main__":
    board = Board()
    board.set_fen("rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2")
    print(board._board)
    print(board.turn)

"""
/home/frederik/repos/cutechess/build/cutechess-cli -variant 3check -engine name=default proto=uci cmd=/home/frederik/.pyenv/versions/3.12.8/bin/python arg=/home/frederik/PycharmProjects/ChessOptimizationPython/main.py arg=--name=default -engine name=3.13 proto=uci cmd=/home/frederik/.pyenv/versions/3.13.1_gil/bin/python arg=/home/frederik/PycharmProjects/ChessOptimizationPython/main.py arg=--name=python3.13 -each tc=10+3 -concurrency 1 -games 10 -repeat -recover -ratinginterval 2 -sprt elo0=0 elo1=10 alpha=0.05 beta=0.05 -openings file=/home/frederik/PycharmProjects/ChessOptimizationPython/Openings/Balsa_Special.pgn -debug
e2e4 e7e5 g1f3 b8c6 f1b5 g8f6 e1g1 f6e4 f1e1 e4d6 f3e5 f8e7 b5f1 c6e5 e1e5 e8g8 e5e7 d8e7 d2d3 c7c6 c2c3 f7f6 f2f3 a7a6 a2a3 b7b6 b2b3 g7g6 g2g3 h7h6 c1h6 d6e4 h6f8 e7f8 d3e4 f8a3 a1a3 d7d6 d1d6 c6c5 d6c5 b6c5 a3a6 a8a6 f1a6 c8a6 h2h3 g6g5 e4e5 f6e5 c3c4 a6c4 b3c4 g8g7 b1c3 e5e4 c3d5 e4f3 d5e3 g5g4 h3g4 g7f6 e3d5 f6e5 d5e3 e5e4 e3f1 e4d4 f1d2 d4e5 d2b3 e5d6 b3d2 d6e5 d2f3 e5d6 f3d2
d6d5
"""