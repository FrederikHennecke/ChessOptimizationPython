//
// Created by Frederik on 19.03.2025.
//

#ifndef CYTHON_MOVEGENERATION_H
#define CYTHON_MOVEGENERATION_H

#include <chrono>
#include "chess.h"

// Forward declarations
float evaluate_board(const Board& board);
int move_value(const Board& board, const Move& move, bool endgame);
bool check_end_game(const Board& board);
Move minimax_root(int max_depth, Board& board, const std::chrono::time_point<std::chrono::high_resolution_clock>& start_time,
                  double time_limit);
std::vector<Move> order_moves(Board& board);

[[maybe_unused]] Move next_move(Board& board, double time_limit, const std::string& name,
               bool debug = true);
float minimax(int depth, Board& board, float alpha, float beta, bool is_maximizing,
              const std::chrono::time_point<std::chrono::high_resolution_clock>& start_time, double time_limit);
void log_info(const std::string& message);


#endif //CYTHON_MOVEGENERATION_H
