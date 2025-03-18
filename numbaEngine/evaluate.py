import numpy as np
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

# Piece values array
PIECE_VALUE = np.array([0, 100, 320, 330, 500, 900, 20000], dtype=np.int64)

# Piece-square tables as numpy arrays
PAWN_WHITE = np.array([
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, -20, -20, 10, 10, 5,
    5, -5, -10, 0, 0, -10, -5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, 5, 10, 25, 25, 10, 5, 5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0
], dtype=np.int64)
PAWN_BLACK = PAWN_WHITE[::-1].copy()

KNIGHT_TABLE = np.array([
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
], dtype=np.int64)

BISHOP_WHITE = np.array([
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
], dtype=np.int64)
BISHOP_BLACK = BISHOP_WHITE[::-1].copy()

ROOK_WHITE = np.array([
    0, 0, 0, 5, 5, 0, 0, 0,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    5, 10, 10, 10, 10, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0
], dtype=np.int64)
ROOK_BLACK = ROOK_WHITE[::-1].copy()

QUEEN_TABLE = np.array([
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -5, 0, 5, 5, 5, 5, 0, -5,
    0, 0, 5, 5, 5, 5, 0, -5,
    -10, 5, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20
], dtype=np.int64)

KING_WHITE = np.array([
    20, 30, 10, 0, 0, 10, 30, 20,
    20, 20, 0, 0, 0, 0, 20, 20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30
], dtype=np.int64)
KING_BLACK = KING_WHITE[::-1].copy()

KING_ENDGAME_WHITE = np.array([
    50, -30, -30, -30, -30, -30, -30, -50,
    -30, -30, 0, 0, 0, 0, -30, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -20, -10, 0, 0, -10, -20, -30,
    -50, -40, -30, -20, -20, -30, -40, -50
], dtype=np.int64)
KING_ENDGAME_BLACK = KING_ENDGAME_WHITE[::-1].copy()


@njit(nogil=True)
def get_pst_value(piece_type, color, square_x, square_y, endgame):
    idx = square_x * 8 + square_y
    if piece_type == PAWN:
        return PAWN_WHITE[idx] if color == WHITE else PAWN_BLACK[idx]
    elif piece_type == KNIGHT:
        return KNIGHT_TABLE[idx]
    elif piece_type == BISHOP:
        return BISHOP_WHITE[idx] if color == WHITE else BISHOP_BLACK[idx]
    elif piece_type == ROOK:
        return ROOK_WHITE[idx] if color == WHITE else ROOK_BLACK[idx]
    elif piece_type == QUEEN:
        return QUEEN_TABLE[idx]
    elif piece_type == KING:
        if endgame:
            return KING_ENDGAME_WHITE[idx] if color == WHITE else KING_ENDGAME_BLACK[idx]
        return KING_WHITE[idx] if color == WHITE else KING_BLACK[idx]
    return 0


@njit(nogil=True)
def evaluate_piece_numba(piece, square_x, square_y, endgame):
    piece_type = abs(piece)
    color = 1 if piece > 0 else -1
    pst = get_pst_value(piece_type, color, square_x, square_y, endgame)
    return pst + PIECE_VALUE[piece_type]


@njit(nogil=True)
def check_end_game_numba(board):
    queens = 0
    minors = 0
    for x in range(8):
        for y in range(8):
            piece = board[x, y]
            if piece == 0:
                continue
            pt = abs(piece)
            if pt == QUEEN:
                queens += 1
            elif pt in (BISHOP, KNIGHT):
                minors += 1
    return queens == 0 or (queens == 2 and minors <= 1)


@njit(nogil=True)
def evaluate_board_numba(board):
    total = 0
    endgame = check_end_game_numba(board)
    for x in range(8):
        for y in range(8):
            piece = board[x, y]
            if piece == 0:
                continue
            value = evaluate_piece_numba(piece, x, y, endgame)
            total += value if piece > 0 else -value
    return total


@njit(nogil=True)
def move_value_numba(board, from_x, from_y, to_x, to_y, promotion, turn, endgame):
    if promotion:
        return PIECE_VALUE[QUEEN] * turn

    from_piece = board[from_x, from_y]
    to_piece = board[to_x, to_y]

    position_score = 0
    if from_piece != 0:
        position_score += evaluate_piece_numba(from_piece, to_x, to_y, endgame)
        position_score -= evaluate_piece_numba(from_piece, from_x, from_y, endgame)

    capture_value = PIECE_VALUE[abs(to_piece)] if to_piece != 0 else 0
    return (capture_value + position_score) * turn


# Python wrapper functions
def evaluate_board(board: np.ndarray) -> int:
    return evaluate_board_numba(board)


def move_value(board: np.ndarray, move, turn: int) -> float:
    from_sq = (move.from_square[0] // 8, move.from_square[1] % 8)
    to_sq = (move.to_square[0] // 8, move.to_square[1] % 8)
    endgame = check_end_game_numba(board)
    return move_value_numba(
        board,
        from_sq[0], from_sq[1],
        to_sq[0], to_sq[1],
        move.promotion,
        turn,
        endgame
    )


def check_end_game(board: np.ndarray) -> bool:
    return check_end_game_numba(board)