//
// Created by Frederik on 19.03.2025.
//

#ifndef CYTHON_CHESS_H
#define CYTHON_CHESS_H

#include <vector>
#include <stack>
#include <string>
#include <variant>

// Constants for piece types and colors
const int WHITE = 1;
const int BLACK = -1;
const int PAWN = 1;
const int KNIGHT = 2;
const int BISHOP = 3;
const int ROOK = 4;
const int QUEEN = 5;
const int KING = 6;


struct Move {
    std::pair<int, int> from_square;
    std::pair<int, int> to_square;
    int promotion = 0;

    bool operator==(const Move& other) const {
        return from_square == other.from_square && to_square == other.to_square && promotion == other.promotion;
    }

    [[nodiscard]] std::string uci() const {
        auto to_uci = [](const std::pair<int, int>& square) {
            char file = 'a' + square.second;
            int rank = 8 - square.first;
            return std::string() + file + std::to_string(rank);
        };
        std::string result = to_uci(from_square) + to_uci(to_square);
        if (promotion) {
            char promo = 'q';
            switch (promotion) {
                case ROOK: promo = 'r'; break;
                case BISHOP: promo = 'b'; break;
                case KNIGHT: promo = 'n'; break;
            }
            result += promo;
        }
        return result;
    }
};

// Board class to represent the chess board
class Board {
private:
    std::vector<std::vector<int>> board;
    std::stack<std::variant<Move, int>> event_stack;
public:
    Board();

    void reset();

    [[maybe_unused]] void set_fen(const std::string& fen);

    void retractMove(const Move& move);

    bool can_claim_draw();

    void push_uci(const std::string& move_str);

    bool is_square_attacked(std::pair<int, int> square, int enemy_color);

    std::vector<Move> legal_moves();

    void push(const Move& move);

    void pop();

    bool is_game_over();

    bool is_checkmate();

    bool is_move_legal(const Move &move, int color);

    int turn;
};

#endif //CYTHON_CHESS_H
