//
// Created by Frederik on 19.03.2025.
//

#include "evaluation.hpp"

// Piece values indexed by piece type (1-6)
const std::vector<int> PIECE_VALUE = {0, 100, 320, 330, 500, 900, 20000};

// Piece-square tables (flipped vertically for black pieces)
const std::vector<int> PAWN_WHITE = {
        0, 0, 0, 0, 0, 0, 0, 0,
        5, 10, 10, -20, -20, 10, 10, 5,
        5, -5, -10, 0, 0, -10, -5, 5,
        0, 0, 0, 20, 20, 0, 0, 0,
        5, 5, 10, 25, 25, 10, 5, 5,
        10, 10, 20, 30, 30, 20, 10, 10,
        50, 50, 50, 50, 50, 50, 50, 50,
        0, 0, 0, 0, 0, 0, 0, 0
};
const std::vector<int> PAWN_BLACK = {
        0, 0, 0, 0, 0, 0, 0, 0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5, 5, 10, 25, 25, 10, 5, 5,
        0, 0, 0, 20, 20, 0, 0, 0,
        5, -5, -10, 0, 0, -10, -5, 5,
        5, 10, 10, -20, -20, 10, 10, 5,
        0, 0, 0, 0, 0, 0, 0, 0
};

const std::vector<int> KNIGHT_TABLE = {
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20, 0, 0, 0, 0, -20, -40,
        -30, 0, 10, 15, 15, 10, 0, -30,
        -30, 5, 15, 20, 20, 15, 5, -30,
        -30, 0, 15, 20, 20, 15, 0, -30,
        -30, 5, 10, 15, 15, 10, 5, -30,
        -40, -20, 0, 5, 5, 0, -20, -40,
        -50, -40, -30, -30, -30, -30, -40, -50
};

const std::vector<int> BISHOP_WHITE = {
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10, 5, 0, 0, 0, 0, 5, -10,
        -10, 10, 10, 10, 10, 10, 10, -10,
        -10, 0, 10, 10, 10, 10, 0, -10,
        -10, 5, 5, 10, 10, 5, 5, -10,
        -10, 0, 5, 10, 10, 5, 0, -10,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -20, -10, -10, -10, -10, -10, -10, -20
};
const std::vector<int> BISHOP_BLACK = {
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 10, 10, 5, 0, -10,
        -10, 5, 5, 10, 10, 5, 5, -10,
        -10, 0, 10, 10, 10, 10, 0, -10,
        -10, 10, 10, 10, 10, 10, 10, -10,
        -10, 5, 0, 0, 0, 0, 5, -10,
        -20, -10, -10, -10, -10, -10, -10, -20
};

const std::vector<int> ROOK_WHITE = {
        0, 0, 0, 5, 5, 0, 0, 0,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        5, 10, 10, 10, 10, 10, 10, 5,
        0, 0, 0, 0, 0, 0, 0, 0
};
const std::vector<int> ROOK_BLACK = {
        0, 0, 0, 0, 0, 0, 0, 0,
        5, 10, 10, 10, 10, 10, 10, 5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        0, 0, 0, 5, 5, 0, 0, 0
};

const std::vector<int> QUEEN_TABLE = {
        -20, -10, -10, -5, -5, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 5, 5, 5, 0, -10,
        -5, 0, 5, 5, 5, 5, 0, -5,
        0, 0, 5, 5, 5, 5, 0, -5,
        -10, 5, 5, 5, 5, 5, 0, -10,
        -10, 0, 5, 0, 0, 0, 0, -10,
        -20, -10, -10, -5, -5, -10, -10, -20
};

const std::vector<int> KING_WHITE = {
        20, 30, 10, 0, 0, 10, 30, 20,
        20, 20, 0, 0, 0, 0, 20, 20,
        -10, -20, -20, -20, -20, -20, -20, -10,
        20, -30, -30, -40, -40, -30, -30, -20,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30
};
const std::vector<int> KING_BLACK = {
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        20, -30, -30, -40, -40, -30, -30, -20,
        -10, -20, -20, -20, -20, -20, -20, -10,
        20, 20, 0, 0, 0, 0, 20, 20,
        20, 30, 10, 0, 0, 10, 30, 20
};

const std::vector<int> KING_ENDGAME_WHITE = {
        50, -30, -30, -30, -30, -30, -30, -50,
        -30, -30, 0, 0, 0, 0, -30, -30,
        -30, -10, 20, 30, 30, 20, -10, -30,
        -30, -10, 30, 40, 40, 30, -10, -30,
        -30, -10, 30, 40, 40, 30, -10, -30,
        -30, -10, 20, 30, 30, 20, -10, -30,
        -30, -20, -10, 0, 0, -10, -20, -30,
        -50, -40, -30, -20, -20, -30, -40, -50
};
const std::vector<int> KING_ENDGAME_BLACK = {
        -50, -40, -30, -20, -20, -30, -40, -50,
        -30, -20, -10, 0, 0, -10, -20, -30,
        -30, -10, 20, 30, 30, 20, -10, -30,
        -30, -10, 30, 40, 40, 30, -10, -30,
        -30, -10, 30, 40, 40, 30, -10, -30,
        -30, -10, 20, 30, 30, 20, -10, -30,
        -30, -30, 0, 0, 0, 0, -30, -30,
        50, -30, -30, -30, -30, -30, -30, 50
};

// Precomputed tables for non-king pieces
const std::map<int, std::pair<std::vector<int>, std::vector<int>>> NON_KING_TABLES = {
        {PAWN, {PAWN_WHITE, PAWN_BLACK}},
        {KNIGHT, {KNIGHT_TABLE, KNIGHT_TABLE}},
        {BISHOP, {BISHOP_WHITE, BISHOP_BLACK}},
        {ROOK, {ROOK_WHITE, ROOK_BLACK}},
        {QUEEN, {QUEEN_TABLE, QUEEN_TABLE}},
};

// Function to evaluate a piece's positional score
int evaluate_piece(int piece, std::pair<int, int> square, bool endgame) {
    int piece_type = abs(piece);
    int color = (piece > 0) ? WHITE : BLACK;

    if (piece_type == KING) {
        if (color == WHITE) {
            return endgame ? KING_ENDGAME_WHITE[square.first * 8 + square.second] : KING_WHITE[square.first * 8 + square.second];
        } else {
            return endgame ? KING_ENDGAME_BLACK[square.first * 8 + square.second] : KING_BLACK[square.first * 8 + square.second];
        }
    } else {
        auto tables = NON_KING_TABLES.find(piece_type);
        if (tables != NON_KING_TABLES.end()) {
            const std::vector<int>& table = (color == WHITE) ? tables->second.first : tables->second.second;
            return table[square.first * 8 + square.second];
        }
    }
    return 0;
}

// Function to evaluate the board
int evaluate_board(const std::vector<std::vector<int>>& board, bool endgame) {
    int total_score = 0;
    for (int x = 0; x < 8; ++x) {
        for (int y = 0; y < 8; ++y) {
            int piece = board[x][y];
            if (piece != 0) {
                int piece_score = evaluate_piece(piece, {x, y}, endgame);
                int value = PIECE_VALUE[abs(piece)];
                total_score += (piece > 0) ? (piece_score + value) : -(piece_score + value);
            }
        }
    }
    return total_score;
}

int move_value(const Board& board, const Move& move, bool endgame) {
    // Handle promotion case
    if (move.promotion != 0) {
        return PIECE_VALUE.at(QUEEN) * static_cast<int>(board.turn);
    }

    // Get pieces at from and to squares
    auto _board = board._board;
    int from_piece = _board.at(move.from_square.first).at(move.from_square.second);
    int to_piece = _board.at(move.to_square.first).at(move.to_square.second);

    int position_score = 0;
    if (from_piece != 0) {  // Valid moving piece exists
        // Calculate positional score difference
        position_score = evaluate_piece(from_piece, move.to_square, endgame)
                       - evaluate_piece(from_piece, move.from_square, endgame);
    }

    // Calculate capture value
    int capture_value = 0;
    if (to_piece != 0) {
        int captured_type = std::abs(to_piece);
        capture_value = PIECE_VALUE.at(captured_type);
    }

    // Calculate total value with turn multiplier
    return (capture_value + position_score) * static_cast<int>(board.turn);
}


