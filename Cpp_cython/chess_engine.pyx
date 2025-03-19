from default.chess import QUEEN, ROOK, BISHOP
# cython: language_level=3
cimport cython
from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp.pair cimport pair
from libcpp cimport bool as cpp_bool

cdef extern from "chess.hpp" namespace "chess":
    cdef cppclass CppBoard:
        CppBoard() except +
        void reset()
        void set_fen(string fen)
        void push_uci(string uci)
        vector[CppMove] legal_moves()
        cpp_bool is_move_legal(CppMove move, int color)
        int turn

    cdef struct CppMove:
        pair[int, int] from_square
        pair[int, int] to_square
        int promotion

cdef extern from "engine.hpp" namespace "chess":
    CppMove cpp_next_move(CppBoard& board, double time_limit, string name,
                          string position_history, cpp_bool debug) except +

# Python wrapper for C++ Move
cdef class Move:
    cdef CppMove _move
    def __init__(self):
        self._move.from_square = pair[int, int](-1, -1)
        self._move.to_square = pair[int, int](-1, -1)
        self._move.promotion = 0

    @property
    def uci(self):
        return self.uci()

# Python wrapper for C++ Board
cdef class Board:
    cdef CppBoard * _thisptr  # Pointer to C++ instance

    def __cinit__(self):
        self._thisptr = new CppBoard()

    def __dealloc__(self):
        del self._thisptr

    def reset(self):
        self._thisptr.reset()

    def set_fen(self, fen):
        self._thisptr.set_fen(fen.encode())

    def push_uci(self, uci_str):
        self._thisptr.push_uci(uci_str.encode())

    def legal_moves(self):
        cdef vector[CppMove] moves = self._thisptr.legal_moves()
        cdef list py_moves = []
        cdef CppMove move
        for move in moves:
            py_move = Move()
            py_move._move = move
            py_moves.append(py_move)
        return py_moves

    @property
    def turn(self):
        return self._thisptr.turn

def next_move(board: Board, time_limit: float, name: str,
              position_history: str, debug=True) -> Move:
    cdef CppMove cmove = cpp_next_move(board._thisptr[0], time_limit,
                                       name.encode(), position_history.encode(),
                                       debug)
    py_move = Move()
    py_move._move = cmove
    return py_move