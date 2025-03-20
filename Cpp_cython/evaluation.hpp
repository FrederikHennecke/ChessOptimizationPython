//
// Created by Frederik on 19.03.2025.
//

#ifndef CYTHON_EVALUATION_H
#define CYTHON_EVALUATION_H
#include "chess.hpp"
#include <map>

int move_value(const Board& board, const Move& move, bool endgame);
int evaluate_board(const std::vector<std::vector<int>>& board, bool endgame);
bool check_end_game(const std::vector<std::vector<int>>& board);
int evaluate_piece(int piece, std::pair<int, int> square, bool endgame);


#endif //CYTHON_EVALUATION_H
