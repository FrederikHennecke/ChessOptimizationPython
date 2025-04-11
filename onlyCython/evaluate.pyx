# cython: language_level=3
cimport numpy as np
from chess cimport Board, Move

ctypedef np.int32_t DTYPE_t

# Piece type constants from previous implementation
cdef enum:
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6
    WHITE = 1
    BLACK = -1

# Piece values (index 0 unused)
PIECE_VALUE = [0, 100, 320, 330, 500, 900, 20000]

# Piece-square tables
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

for i in range(64):
    PAWN_BLACK[i] = PAWN_WHITE[63 - i]

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

for i in range(64):
    BISHOP_BLACK[i] = BISHOP_WHITE[63 - i]

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

for i in range(64):
    ROOK_BLACK[i] = ROOK_WHITE[63 - i]

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

KING_WHITE= [
    20, 30, 10, 0, 0, 10, 30, 20,
    20, 20, 0, 0, 0, 0, 20, 20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30
]

for i in range(64):
    KING_BLACK[i] = KING_WHITE[63 - i]

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

for i in range(64):
    KING_ENDGAME_BLACK[i] = KING_ENDGAME_WHITE[63 - i]

cpdef int move_value(Board board, Move move, bint endgame):
    """Calculate the score for a given move (optimized for Cython)."""
    if move.promotion:
        return PIECE_VALUE[QUEEN] * board.turn

    cdef int from_x = move.from_x
    cdef int from_y = move.from_y
    cdef int to_x = move.to_x
    cdef int to_y = move.to_y

    cdef int from_piece = board._board_view[from_x, from_y]
    cdef int to_piece = board._board_view[to_x, to_y]

    cdef int position_score = 0
    if from_piece != 0:
        position_score += evaluate_piece(from_piece, to_x, to_y, endgame)
        position_score -= evaluate_piece(from_piece, from_x, from_y, endgame)

    cdef int capture_value = PIECE_VALUE[abs(to_piece)] if to_piece != 0 else 0
    cdef int total = capture_value + position_score

    return total * board.turn

cdef int evaluate_piece(int piece, int x, int y, bint endgame):
    """Positional evaluation for a single piece (C-only)."""
    cdef int piece_type = abs(piece)
    cdef int color = 1 if piece > 0 else -1
    cdef int idx = 8 * x + y
    cdef int[:] table

    if piece_type == KING:
        if color == WHITE:
            table = KING_ENDGAME_WHITE if endgame else KING_WHITE
        else:
            table = KING_ENDGAME_BLACK if endgame else KING_BLACK
        return table[idx]
    else:
        if piece_type == PAWN:
            table = PAWN_WHITE if color == WHITE else PAWN_BLACK
        elif piece_type == KNIGHT:
            table = KNIGHT_TABLE
        elif piece_type == BISHOP:
            table = BISHOP_WHITE if color == WHITE else BISHOP_BLACK
        elif piece_type == ROOK:
            table = ROOK_WHITE if color == WHITE else ROOK_BLACK
        elif piece_type == QUEEN:
            table = QUEEN_TABLE
        else:
            return 0

    return table[idx]

cpdef int evaluate_board(Board board):
    """Evaluate the entire board position (optimized Cython)."""
    cdef int total_score = 0
    cdef bint endgame = check_end_game(board)
    cdef int x, y, piece, piece_type, value, score

    for x in range(8):
        for y in range(8):
            piece = board._board_view[x, y]
            if piece == 0:
                continue

            piece_type = abs(piece)
            value = PIECE_VALUE[piece_type]
            score = evaluate_piece(piece, x, y, endgame)
            total_score += (value + score) * (1 if piece > 0 else -1)

    return total_score

cpdef bint check_end_game(Board board):
    """Determine if position is endgame (C-optimized)."""
    cdef int queens = 0
    cdef int minors = 0
    cdef int x, y, piece, pt

    for x in range(8):
        for y in range(8):
            piece = board._board_view[x, y]
            if piece == 0:
                continue

            pt = abs(piece)
            if pt == QUEEN:
                queens += 1
            elif pt == BISHOP or pt == KNIGHT:
                minors += 1

    return queens == 0 or (queens == 2 and minors <= 1)