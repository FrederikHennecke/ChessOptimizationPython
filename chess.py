import numpy as np
from queue import LifoQueue

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
        """
        Convert the move to UCI format.
        Example: "e2e4" or "e7e8q".
        """
        if self.from_square is None or self.to_square is None:
            return "Invalid move"

        # Convert (x, y) coordinates to algebraic notation
        def square_to_notation(square):
            x, y = square
            file = chr(ord('a') + y)  # Convert y to file (a-h)
            rank = str(8 - x)         # Convert x to rank (1-8)
            return file + rank

        from_notation = square_to_notation(self.from_square)
        to_notation = square_to_notation(self.to_square)

        # Add promotion if applicable
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
                               [4,2,3,5,6,3,2,4]],dtype=np.int64).copy()
        self.event = LifoQueue()

    def reset(self):
        self.__init__()

    def set_fen(self, fen):
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

        # Initialize an empty 8x8 board
        self._board = np.zeros((8, 8), dtype=int)

        # Split the FEN string into parts
        parts = fen.split(' ')
        piece_placement = parts[0]

        # Parse the piece placement
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

        self.turn = WHITE if parts[1]=="w" else BLACK

    def push_uci(self, move):
        # Convert UCI move to coordinates
        from_square = (8 - int(move[1]), ord(move[0]) - ord('a'))
        to_square = (8 - int(move[3]), ord(move[2]) - ord('a'))
        promotion = None

        # Check if the move is a promotion
        if len(move) == 5:
            promotion = move[4].lower()
            promotion_map = {
                'q': QUEEN,
                'r': ROOK,
                'b': BISHOP,
                'n': KNIGHT
            }
            promotion = promotion_map.get(promotion, None)

        # Get the piece at the from_square
        piece = self._board[from_square[0], from_square[1]]

        # Handle castling
        if abs(piece) == KING and abs(from_square[1] - to_square[1]) == 2:
            # Determine if it's kingside or queenside castling
            if to_square[1] > from_square[1]:  # Kingside castling
                rook_from = (from_square[0], 7)  # h-file
                rook_to = (from_square[0], 5)  # f-file
            else:  # Queenside castling
                rook_from = (from_square[0], 0)  # a-file
                rook_to = (from_square[0], 3)  # d-file

            # Move the rook
            rook_piece = self._board[rook_from[0], rook_from[1]]
            self._board[rook_to[0], rook_to[1]] = rook_piece
            self._board[rook_from[0], rook_from[1]] = 0

        # Get the piece at the to_square
        old_piece = self._board[to_square[0], to_square[1]]
        if old_piece != 0:
            self.event.put(old_piece)

        # Move the piece
        self._board[to_square[0], to_square[1]] = piece
        self._board[from_square[0], from_square[1]] = 0

        if np.sign(old_piece) == np.sign(piece):
            self._board[from_square[0], from_square[1]] = old_piece

        # Handle promotion
        if promotion:
            self._board[to_square[0], to_square[1]] = promotion * self.turn

        # Switch turns
        self.turn = -self.turn

    def legal_moves(self):
        """
        Generate all legal moves for the current turn, ensuring the king is not left in check.
        """
        for x in range(8):
            for y in range(8):
                piece = self._board[x, y]
                if piece == 0 or np.sign(piece) != self.turn:
                    continue

                piece_type = abs(piece)

                if piece_type == PAWN:
                    # Pawn moves
                    direction = -self.turn
                    start_row = 6 if self.turn == WHITE else 1
                    promotion_row = 0 if self.turn == WHITE else 7

                    # Single move forward
                    if 0 <= x + direction < 8 and self._board[x + direction, y] == 0:
                        if x + direction == promotion_row:
                            for promo in [QUEEN, ROOK, BISHOP, KNIGHT]:
                                move = Move()
                                move.from_square = (x, y)
                                move.to_square = (x + direction, y)
                                move.promotion = promo
                                if self._is_move_legal(move, self.turn):
                                    yield move
                        else:
                            move = Move()
                            move.from_square = (x, y)
                            move.to_square = (x + direction, y)
                            if self._is_move_legal(move, self.turn):
                                yield move

                    # Double move from starting position
                    if x == start_row and self._board[x + direction, y] == 0 and self._board[x + 2 * direction, y] == 0:
                        move = Move()
                        move.from_square = (x, y)
                        move.to_square = (x + 2 * direction, y)
                        if self._is_move_legal(move, self.turn):
                            yield move

                    # Captures
                    for dy in [-1, 1]:
                        if 0 <= y + dy < 8 and 0 <= x + direction < 8:
                            if self._board[x + direction, y + dy] * self.turn < 0:
                                if x + direction == promotion_row:
                                    for promo in [QUEEN, ROOK, BISHOP, KNIGHT]:
                                        move = Move()
                                        move.from_square = (x, y)
                                        move.to_square = (x + direction, y + dy)
                                        move.promotion = promo
                                        if self._is_move_legal(move, self.turn):
                                            yield move
                                else:
                                    move = Move()
                                    move.from_square = (x, y)
                                    move.to_square = (x + direction, y + dy)
                                    if self._is_move_legal(move, self.turn):
                                        yield move

                elif piece_type == KNIGHT:
                    # Knight moves
                    for dx, dy in [(-2, -1), (-1, -2), (1, -2), (2, -1),
                                   (2, 1), (1, 2), (-1, 2), (-2, 1)]:
                        x2, y2 = x + dx, y + dy
                        if 0 <= x2 < 8 and 0 <= y2 < 8:
                            if self._board[x2, y2] * self.turn <= 0:
                                move = Move()
                                move.from_square = (x, y)
                                move.to_square = (x2, y2)
                                if self._is_move_legal(move, self.turn):
                                    yield move

                elif piece_type in [BISHOP, ROOK, QUEEN]:
                    # Sliding moves
                    directions = []
                    if piece_type == BISHOP or piece_type == QUEEN:
                        directions.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])
                    if piece_type == ROOK or piece_type == QUEEN:
                        directions.extend([(-1, 0), (1, 0), (0, -1), (0, 1)])

                    for dx, dy in directions:
                        x2, y2 = x + dx, y + dy
                        while 0 <= x2 < 8 and 0 <= y2 < 8:
                            if self._board[x2, y2] * self.turn <= 0:
                                move = Move()
                                move.from_square = (x, y)
                                move.to_square = (x2, y2)
                                if self._is_move_legal(move, self.turn):
                                    yield move
                            if self._board[x2, y2] != 0:
                                break
                            x2 += dx
                            y2 += dy

                elif piece_type == KING:
                    # King moves
                    for dx, dy in [(-1, -1), (-1, 0), (-1, 1),
                                   (0, -1), (0, 1),
                                   (1, -1), (1, 0), (1, 1)]:
                        x2, y2 = x + dx, y + dy
                        if 0 <= x2 < 8 and 0 <= y2 < 8:
                            if self._board[x2, y2] * self.turn <= 0:
                                move = Move()
                                move.from_square = (x, y)
                                move.to_square = (x2, y2)
                                if self._is_move_legal(move, self.turn):
                                    yield move

    def _is_move_legal(self, move, color):
        """
        Check if a move is legal (does not leave the king in check).
        """
        # Simulate the move
        original_piece = self._board[move.to_square[0], move.to_square[1]]
        self._board[move.to_square[0], move.to_square[1]] = self._board[move.from_square[0], move.from_square[1]]
        self._board[move.from_square[0], move.from_square[1]] = 0

        # Find the king's position
        king_position = None
        for x in range(8):
            for y in range(8):
                if self._board[x, y] == KING * color:
                    king_position = (x, y)
                    break
            if king_position:
                break

        # Check if the king is in check
        is_legal = not self.is_square_attacked(king_position, -color)

        # Undo the move
        self._board[move.from_square[0], move.from_square[1]] = self._board[move.to_square[0], move.to_square[1]]
        self._board[move.to_square[0], move.to_square[1]] = original_piece

        return is_legal

    def push(self, move: Move):
        """
        Add a move to the move stack and update the board.
        """
        self.event.put(move)
        self.push_uci(str(move))  # Apply the move to the board



    def pop(self):
        """
        Remove the last move from the move stack and revert the board state.
        """
        if not self.event:
            raise IndexError("No moves to pop")

        last_move = None

        # Get the last move
        event = self.event.get()
        if isinstance(event, Move):
            last_move = self.retractMove(event)
        elif self.is_numeric(event):
            last_move = self.retractMove(self.event.get())
            self._board[last_move.to_square[0], last_move.to_square[1]] = event
        return last_move

    def is_numeric(self, ev) -> bool:
        attrs = ['__add__', '__sub__', '__mul__', '__truediv__', '__pow__']
        return all(hasattr(ev, attr) for attr in attrs)

    def retractMove(self, event):
        last_move = event
        # Revert the move
        self._board[last_move.from_square[0], last_move.from_square[1]] = self._board[
            last_move.to_square[0], last_move.to_square[1]]
        self._board[last_move.to_square[0], last_move.to_square[1]] = 0
        # Handle promotion reversal
        if last_move.promotion:
            # Revert the promoted piece to a pawn
            self._board[last_move.from_square[0], last_move.from_square[1]] = PAWN * self.turn
        # Switch turns back
        self.turn = -self.turn
        return last_move

    def can_claim_draw(self):
        """
        Check if a draw can be claimed based on threefold repetition, fifty-move rule, or insufficient material.
        """
        # Insufficient material
        pieces = np.abs(self._board).flatten()
        if np.sum(pieces == PAWN) == 0 and np.sum(pieces == QUEEN) == 0 and np.sum(pieces == ROOK) == 0:
            # Only kings and minor pieces (bishops, knights) remain
            if np.sum(pieces == BISHOP) + np.sum(pieces == KNIGHT) <= 1:
                return True

        return False

    def is_checkmate(self):
        """
        Check if the current player is in checkmate.
        """
        # Find the king's position
        king_position = None
        for x in range(8):
            for y in range(8):
                if self._board[x, y] == KING * -self.turn:
                    king_position = (x, y)
                    break
            if king_position:
                break

        # Check if the king is in check
        if not self.is_square_attacked(king_position, self.turn):
            return False

        # Check if there are any legal moves
        for move in self.legal_moves():
            # Simulate the move
            original_piece = self._board[move.to_square[0], move.to_square[1]]
            self._board[move.to_square[0], move.to_square[1]] = self._board[move.from_square[0], move.from_square[1]]
            self._board[move.from_square[0], move.from_square[1]] = 0

            # Check if the king is still in check
            king_position_new = move.to_square if move.from_square == king_position else king_position
            if not self.is_square_attacked(king_position_new, self.turn):
                # Undo the move
                self._board[move.from_square[0], move.from_square[1]] = self._board[move.to_square[0], move.to_square[1]]
                self._board[move.to_square[0], move.to_square[1]] = original_piece
            else:
                return False

            # Undo the move
            self._board[move.from_square[0], move.from_square[1]] = self._board[move.to_square[0], move.to_square[1]]
            self._board[move.to_square[0], move.to_square[1]] = original_piece

        return True

    def is_square_attacked(self, square, enemy_color):
        """
        Check if a square is attacked by any piece of the given color.
        """
        if square is None:
            return False

        # Directions for non-sliding pieces
        pawn_directions = [(-1, -1), (-1, 1)] if enemy_color == WHITE else [(1, -1), (1, 1)]
        knight_directions = [(-2, -1), (-1, -2), (1, -2), (2, -1),
                             (2, 1), (1, 2), (-1, 2), (-2, 1)]
        king_directions = [(-1, -1), (-1, 0), (-1, 1),
                           (0, -1), (0, 1),
                           (1, -1), (1, 0), (1, 1)]

        # Check for pawn attacks
        for dx, dy in pawn_directions:
            x, y = square[0] + dx, square[1] + dy
            if 0 <= x < 8 and 0 <= y < 8:
                if self._board[x, y] == PAWN * enemy_color:
                    return True

        # Check for knight attacks
        for dx, dy in knight_directions:
            x, y = square[0] + dx, square[1] + dy
            if 0 <= x < 8 and 0 <= y < 8:
                if self._board[x, y] == KNIGHT * enemy_color:
                    return True

        # Check for king attacks
        for dx, dy in king_directions:
            x, y = square[0] + dx, square[1] + dy
            if 0 <= x < 8 and 0 <= y < 8:
                if self._board[x, y] == KING * enemy_color:
                    return True

        # Directions for sliding pieces (bishop, rook, queen)
        sliding_directions = {
            BISHOP: [(-1, -1), (-1, 1), (1, -1), (1, 1)],  # Diagonal
            ROOK: [(-1, 0), (1, 0), (0, -1), (0, 1)],  # Straight
            QUEEN: [(-1, -1), (-1, 1), (1, -1), (1, 1),  # Diagonal + Straight
                    (-1, 0), (1, 0), (0, -1), (0, 1)]
        }

        # Check for sliding piece attacks
        for piece_type, directions in sliding_directions.items():
            for dx, dy in directions:
                x, y = square[0] + dx, square[1] + dy
                while 0 <= x < 8 and 0 <= y < 8:
                    if self._board[x, y] != 0:  # Stop if we hit a piece
                        if self._board[x, y] == piece_type * enemy_color:
                            return True
                        break  # Stop searching in this direction
                    x += dx
                    y += dy

        return False

    def is_game_over(self):
        """
        Check if the game is over (checkmate, stalemate, or draw).
        """
        # Check for checkmate
        if self.is_checkmate():
            return True

        # Check for stalemate
        if not any(self.legal_moves()):
            return True

        # Check for draw conditions
        if self.can_claim_draw():
            return True

        return False

    def piece_at(self, from_square):
        return self._board[from_square[0], from_square[1]]

    def piece_map(self):
        """
        Return a dictionary mapping squares (x, y) to Piece objects.
        """
        piece_map = {}
        for x in range(8):
            for y in range(8):
                piece_value = self._board[x, y]
                if piece_value != 0:
                    color = WHITE if piece_value > 0 else BLACK
                    piece_type = abs(piece_value)
                    piece_map[(x, y)] = color * piece_type
        return piece_map

if __name__ == "__main__":
    board = Board()
    board.set_fen("rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2")
    print(board._board)
    print(board.turn)

"""
/home/frederik/repos/cutechess/build/cutechess-cli -variant 3check -engine name=Default proto=uci cmd=/home/frederik/.pyenv/versions/3.12.8/bin/python arg=/home/frederik/PycharmProjects/ChessOptimizationPython/main.py arg=--name=default -engine name=3.13 proto=uci cmd=/home/frederik/.pyenv/versions/3.13.1_gil/bin/python arg=/home/frederik/PycharmProjects/ChessOptimizationPython/main.py arg=--name=python3.13 -each tc=10+3 -concurrency 1 -games 10 -repeat -recover -ratinginterval 2 -sprt elo0=0 elo1=10 alpha=0.05 beta=0.05 -openings file=/home/frederik/PycharmProjects/ChessOptimizationPython/Openings/Balsa_Special.pgn -debug
e2e4 e7e5 g1f3 b8c6 f1b5 g8f6 e1g1 f6e4 f1e1 e4d6 f3e5 f8e7 b5f1 c6e5 e1e5 e8g8 e5e7 d8e7 d2d3 c7c6 c2c3 f7f6 f2f3 a7a6 a2a3 b7b6 b2b3 g7g6 g2g3 h7h6 c1h6 d6e4 h6f8 e7f8 d3e4 f8a3 a1a3 d7d6 d1d6 c6c5 d6c5 b6c5 a3a6 a8a6 f1a6 c8a6 h2h3 g6g5 e4e5 f6e5 c3c4 a6c4 b3c4 g8g7 b1c3 e5e4 c3d5 e4f3 d5e3 g5g4 h3g4 g7f6 e3d5 f6e5 d5e3 e5e4 e3f1 e4d4 f1d2 d4e5 d2b3 e5d6 b3d2 d6e5 d2f3 e5d6 f3d2
d6d5
"""