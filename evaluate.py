import numpy as np

import chess

# Piece values indexed by piece type (1-6)
PIECE_VALUE = [0] * 7
PIECE_VALUE[chess.PAWN] = 100
PIECE_VALUE[chess.KNIGHT] = 320
PIECE_VALUE[chess.BISHOP] = 330
PIECE_VALUE[chess.ROOK] = 500
PIECE_VALUE[chess.QUEEN] = 900
PIECE_VALUE[chess.KING] = 20000

# Piece-square tables (flipped vertically for black pieces)
PAWN_WHITE = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, -20, -20, 10, 10, 5,
    5, -5, -10, 0, 0, -10, -5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, 5, 10, 25, 25, 10, 5, 5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0
]
PAWN_BLACK = PAWN_WHITE[::-1]

KNIGHT_TABLE = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

BISHOP_WHITE = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]
BISHOP_BLACK = BISHOP_WHITE[::-1]

ROOK_WHITE = [
    0, 0, 0, 5, 5, 0, 0, 0,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    5, 10, 10, 10, 10, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0
]
ROOK_BLACK = ROOK_WHITE[::-1]

QUEEN_TABLE = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -5, 0, 5, 5, 5, 5, 0, -5,
    0, 0, 5, 5, 5, 5, 0, -5,
    -10, 5, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20
]

KING_WHITE = [
    20, 30, 10, 0, 0, 10, 30, 20,
    20, 20, 0, 0, 0, 0, 20, 20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30
]
KING_BLACK = KING_WHITE[::-1]

KING_ENDGAME_WHITE = [
    50, -30, -30, -30, -30, -30, -30, -50,
    -30, -30, 0, 0, 0, 0, -30, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -20, -10, 0, 0, -10, -20, -30,
    -50, -40, -30, -20, -20, -30, -40, -50
]
KING_ENDGAME_BLACK = KING_ENDGAME_WHITE[::-1]

# Precomputed tables for non-king pieces
NON_KING_TABLES = {
    chess.PAWN: (PAWN_WHITE, PAWN_BLACK),
    chess.KNIGHT: (KNIGHT_TABLE, KNIGHT_TABLE),
    chess.BISHOP: (BISHOP_WHITE, BISHOP_BLACK),
    chess.ROOK: (ROOK_WHITE, ROOK_BLACK),
    chess.QUEEN: (QUEEN_TABLE, QUEEN_TABLE),
}


def move_value(board: chess.Board, move: chess.Move, endgame: bool) -> float:
    """Calculate the score for a given move."""
    if move.promotion:
        return float("inf") if board.turn else -float("inf")

    from_piece = board.piece_at(move.from_square)
    to_piece = board.piece_at(move.to_square)

    position_score = 0
    if from_piece:
        position_score = evaluate_piece(from_piece, move.to_square, endgame)
        position_score += evaluate_piece(from_piece, move.from_square, endgame)

    capture_value = PIECE_VALUE[abs(to_piece)] if to_piece else 0
    total = capture_value + position_score

    return total * board.turn


def evaluate_piece(piece: int, square: tuple, endgame: bool) -> int:
    """Calculate the positional score for a piece on a given square."""
    piece_type = abs(piece)
    color = np.sign(piece)

    if piece_type == chess.KING:
        if color == chess.WHITE:
            table = KING_ENDGAME_WHITE if endgame else KING_WHITE
        else:
            table = KING_ENDGAME_BLACK if endgame else KING_BLACK
    else:
        table_white, table_black = NON_KING_TABLES.get(piece_type, (None, None))
        if not table_white:
            return 0
        table = table_white if color == chess.WHITE else table_black

    return table[8*square[0]+square[1]]


def evaluate_board(board: chess.Board) -> int:
    """Evaluate the current board position."""
    total_score = 0
    endgame = check_end_game(board)

    for square, piece in board.piece_map().items():
        piece_score = evaluate_piece(piece, square, endgame)
        value = PIECE_VALUE[abs(piece)]
        total_score += piece_score + value if np.sign(piece) else -(piece_score + value)

    return total_score


def check_end_game(board: chess.Board) -> bool:
    """Determine if the current position is an endgame."""
    queens = 0
    minors = 0

    for piece in board.piece_map().values():
        pt = abs(piece)
        if pt == chess.QUEEN:
            queens += 1
        elif pt in {chess.BISHOP, chess.KNIGHT}:
            minors += 1

    return queens == 0 or (queens == 2 and minors <= 1)