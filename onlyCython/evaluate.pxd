# evaluate.pxd
from chess cimport Board, Move

# Piece values
cdef int[7] PIECE_VALUE

# Piece-square tables
cdef int[64] PAWN_WHITE
cdef int[64] PAWN_BLACK
cdef int[64] KNIGHT_TABLE
cdef int[64] BISHOP_WHITE
cdef int[64] BISHOP_BLACK
cdef int[64] ROOK_WHITE
cdef int[64] ROOK_BLACK
cdef int[64] QUEEN_TABLE
cdef int[64] KING_WHITE
cdef int[64] KING_BLACK
cdef int[64] KING_ENDGAME_WHITE
cdef int[64] KING_ENDGAME_BLACK

# Core evaluation functions
cpdef int evaluate_board(Board board)
cpdef int move_value(Board board, Move move, bint endgame)
cpdef bint check_end_game(Board board)

# Internal helper functions
cdef int evaluate_piece(int piece, int x, int y, bint endgame)