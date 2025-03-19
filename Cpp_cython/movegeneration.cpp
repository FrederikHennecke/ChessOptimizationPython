//
// Created by Frederik on 19.03.2025.
//

#include "movegeneration.h"

#include <iostream>
#include <vector>
#include <algorithm>
#include <chrono>
#include <cmath>
#include <fstream>
#include <sstream>
#include "chess.h"

// Constants and types
constexpr float MATE_SCORE = 1e9f;
constexpr float MATE_THRESHOLD = 999000000.0f;

// Debug information structure
struct DebugInfo {
    std::string engine;
    int nodes = 0;
    double time = 0.0;

    void clear() {
        engine.clear();
        nodes = 0;
        time = 0.0;
    }
} debug_info;

// Main search function
[[maybe_unused]] Move next_move(Board& board, double time_limit, const std::string& name,
               bool debug) {
    debug_info.clear();
    debug_info.engine = name;

    auto t0 = std::chrono::high_resolution_clock::now();
    std::vector<Move> legal_moves = board.legal_moves();
    Move best_move;
    int depth = 1;

    while (std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - t0).count() < time_limit) {
        Move current_move = minimax_root(depth, board, t0, time_limit);
        if (current_move.from_square.first != -1) { // Valid move check
            best_move = current_move;
        }
        depth++;
    }

    debug_info.time = std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - t0).count();

    if (debug) {
        std::stringstream ss;
        ss << "Final stats: {engine: " << debug_info.engine
           << ", nodes: " << debug_info.nodes
           << ", time: " << debug_info.time << "}";
        log_info(ss.str());
    }
    best_move.from_square.first != -1 ? best_move :
    legal_moves.at(0);

    return best_move;
}

// Minimax root with iterative deepening
Move minimax_root(int max_depth, Board& board, const std::chrono::time_point<std::chrono::high_resolution_clock>& start_time,
                  double time_limit) {
    bool is_maximizing = board.turn == WHITE;
    float best_value = is_maximizing ? -INFINITY : INFINITY;
    Move best_move;

    for (Move move : order_moves(board)) {
        if (std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - start_time).count() >= time_limit)
            return best_move;

        board.push(move);
        float value = minimax(max_depth-1, board, -INFINITY, INFINITY, !is_maximizing,
                              start_time, time_limit);
        board.pop();

        if ((is_maximizing && value > best_value) || (!is_maximizing && value < best_value)) {
            best_value = value;
            best_move = move;
        }
    }
    return best_move;
}

// Move ordering implementation
std::vector<Move> order_moves(Board& board) {
    bool endgame = check_end_game(board);
    std::vector<std::pair<int, Move>> scored_moves;

    for (Move move : board.legal_moves()) {
        scored_moves.emplace_back(move_value(board, move, endgame), move);
    }

    std::sort(scored_moves.begin(), scored_moves.end(),
         [&](const std::pair<int, Move>& a, const std::pair<int, Move>& b) {
             return board.turn == WHITE ? a.first > b.first : a.first < b.first;
         });

    std::vector<Move> ordered;
    transform(scored_moves.begin(), scored_moves.end(), back_inserter(ordered),
              [](const std::pair<int, Move>& p) { return p.second; });
    return ordered;
}

// Core minimax algorithm with alpha-beta pruning
float minimax(int depth, Board& board, float alpha, float beta, bool is_maximizing,
              const std::chrono::time_point<std::chrono::high_resolution_clock>& start_time, double time_limit) {
    debug_info.nodes++;

    if (std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - start_time).count() >= time_limit)
        return 0.0f;

    if (board.is_checkmate()) return is_maximizing ? -MATE_SCORE : MATE_SCORE;
    if (depth == 0) return evaluate_board(board);

    float value = is_maximizing ? -INFINITY : INFINITY;
    for (Move move : order_moves(board)) {
        board.push(move);
        float current = minimax(depth-1, board, alpha, beta, !is_maximizing, start_time, time_limit);
        board.pop();

        if (is_maximizing) {
            value = std::max(value, current);
            alpha = std::max(alpha, value);
        } else {
            value = std::min(value, current);
            beta = std::min(beta, value);
        }

        if (beta <= alpha) break;
    }
    return value;
}

// Logging implementation
void log_info(const std::string& message) {
    std::ofstream log_file("/home/frederik/repos/ChessOptimizationPython/logs/chess_engine_log_" +
                      debug_info.engine + ".txt", std::ios::app);
    if (log_file) log_file << message << std::endl;
}