# movegeneration.pxd
from chess cimport Board, Move

cdef struct MoveOrderEntry:
    double score
    int from_x
    int from_y
    int to_x
    int to_y
    int promotion

cdef double minimax(
    int depth,
    Board board,
    double alpha,
    double beta,
    bint is_maximizing,
    double start_time,
    double time_limit
)

cpdef Move next_move(
    Board board,
    double time_limit,
    unicode engine_name,
    bint debug
)