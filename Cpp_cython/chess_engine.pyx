# chess_engine.pyx
# distutils: language = c++
# distutils: sources = chess.cpp movegeneration.cpp

from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp.pair cimport pair
from libcpp cimport bool as cbool

# ===== C++ Interface Declarations =====
cdef extern from "chess.hpp":
    cdef cppclass CMove "Move":
        CMove() except +
        pair[int, int] from_square
        pair[int, int] to_square
        int promotion
        string uci()

    cdef cppclass CBoard "Board":
        CBoard() except +
        void reset()
        void set_fen(string fen)
        void push_uci(string move_str)
        void push(const CMove& move)
        void pop()
        vector[CMove] legal_moves()
        int turn
        cbool is_move_legal(const CMove& move, int color)

cdef extern from "movegeneration.hpp":
    CMove cpp_next_move "next_move"(CBoard& board, double time_limit, string name, cbool debug) except +

# ===== Python Wrappers =====
cdef class Move:
    cdef CMove c_move

    def __init__(self, uci_str=None):
        if uci_str:
            self.from_uci(uci_str)

    property from_square:
        def __get__(self):
            return (self.c_move.from_square.first, self.c_move.from_square.second)

    property to_square:
        def __get__(self):
            return (self.c_move.to_square.first, self.c_move.to_square.second)

    property promotion:
        def __get__(self):
            return self.c_move.promotion

    def uci(self):
        return self.c_move.uci().decode('utf-8')

    def from_uci(self, uci_str):
        cdef string s = uci_str.encode('utf-8')
        if s.length() < 4:
            raise ValueError("Invalid UCI string")

        # Convert UCI notation to C++ coordinates
        cdef int from_file = ord(s[0]) - ord('a')  # a-h -> 0-7
        cdef int from_rank = 8 - int(s[1])  # 1-8 -> 7-0
        cdef int to_file = ord(s[2]) - ord('a')
        cdef int to_rank = 8 - int(s[3])

        self.c_move.from_square = pair[int, int](from_rank, from_file)
        self.c_move.to_square = pair[int, int](to_rank, to_file)

        if s.length() == 5:
            promo_piece = s[4]
            self.c_move.promotion = {
                'q': 5, 'r': 4,
                'b': 3, 'n': 2
            }[promo_piece.lower()]

    def __repr__(self):
        return f"Move({self.uci()})"

cdef class Board:
    cdef CBoard c_board

    def __init__(self, fen=None):
        if fen:
            self.set_fen(fen)
        else:
            self.reset()

    def reset(self):
        self.c_board.reset()

    def set_fen(self, fen):
        self.c_board.set_fen(fen.encode('utf-8'))

    def push_uci(self, uci_str):
        self.c_board.push_uci(uci_str.encode('utf-8'))

    def push(self, Move move):
        self.c_board.push(move.c_move)

    def pop(self):
        self.c_board.pop()

    def legal_moves(self):
        cdef vector[CMove] moves = self.c_board.legal_moves()
        return [self._convert_move(m) for m in moves]

    def is_move_legal(self, Move move):
        return self.c_board.is_move_legal(move.c_move, self.turn)

    property turn:
        def __get__(self):
            return self.c_board.turn

    cdef _convert_move(self, CMove cmove):
        py_move = Move()
        py_move.c_move = cmove
        return py_move

    def debug_print(self):
        """Helper method to inspect board state"""
        for row in range(8):
            line = []
            for col in range(8):
                piece = self.c_board.turn
                if piece == 0:
                    line.append('.')
                else:
                    color = 'w' if piece > 0 else 'b'
                    typ = abs(piece)
                    line.append(color + ['', 'P', 'N', 'B', 'R', 'Q', 'K'][typ])
            print(' '.join(line))

def next_move(Board board, double time_limit, str name, debug=True):
    cdef CMove cpp_move = cpp_next_move(board.c_board, time_limit, name.encode('utf-8'), debug)
    return board._convert_move(cpp_move)

# Add debug helpers
cdef extern from *:
    """
    #include <iostream>
    void debug_board(const Board& b) {
        for (int row = 0; row < 8; row++) {
            for (int col = 0; col < 8; col++) {
                int piece = b._board[row][col];
                if (piece == 0) std::cout << ". ";
                else std::cout << (piece > 0 ? "w" : "b")
                             << "PRNBQK"[abs(piece)] << " ";
            }
            std::cout << std::endl;
        }
    }
    """
    void debug_board(const CBoard& b)

def debug_cpp_board(Board board):
    """Call this from Python to see C++ board state"""
    debug_board(board.c_board)