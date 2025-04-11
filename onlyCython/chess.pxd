# chess.pxd
cimport numpy as np

ctypedef np.int32_t DTYPE_t

# Piece type constants
cdef enum PieceType:
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6

cdef enum Color:
    WHITE = 1
    BLACK = -1

cdef class Move:
    cdef public int from_x
    cdef public int from_y
    cdef public int to_x
    cdef public int to_y
    cdef public int promotion


cdef class Board:
    cdef public DTYPE_t[:, ::1] _board_array
    cdef public DTYPE_t[:, ::1] _board_view
    cdef public int turn
    cdef public list event

    # Core functionality
    cpdef void reset(self)
    cpdef void set_fen(self, unicode fen)
    cpdef void push_uci(self, unicode uci_move)
    cpdef void push(self, Move move)
    cpdef Move pop(self)
    cdef Move _retract_move(self, Move move)

    # Move generation
    cpdef list legal_moves(self)
    cpdef bint _is_move_legal(self, Move move)

    # Game state checks
    cpdef bint is_checkmate(self)
    cpdef bint is_game_over(self)
    cpdef bint can_claim_draw(self)
    cpdef bint _is_square_attacked(self, tuple square, int color)
    cpdef tuple _find_king(self, int color)

    cpdef dict piece_map(self)
    cpdef int piece_at(self, tuple square)