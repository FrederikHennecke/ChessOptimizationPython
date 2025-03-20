//
// Created by Frederik on 19.03.2025.
//

#include "chess.hpp"

#include <vector>
#include <stack>
#include <map>
#include <string>
#include <stdexcept>
#include <utility>

bool Board::is_square_attacked(std::pair<int, int> square, int enemy_color) {
    if (square.first < 0 || square.first >= 8 || square.second < 0 || square.second >= 8)
        return false;

    // Pawn attacks
    int pawn_dir = (enemy_color == WHITE) ? 1 : -1;
    std::vector<std::pair<int, int>> pawn_deltas = {{pawn_dir, -1},
                                                    {pawn_dir, 1}};
    for (auto &delta: pawn_deltas) {
        int x = square.first + delta.first;
        int y = square.second + delta.second;
        if (x >= 0 && x < 8 && y >= 0 && y < 8 && _board[x][y] == PAWN * enemy_color)
            return true;
    }

    // Knight attacks
    std::vector<std::pair<int, int>> knight_deltas = {{-2, -1},
                                                      {-1, -2},
                                                      {1,  -2},
                                                      {2,  -1},
                                                      {2,  1},
                                                      {1,  2},
                                                      {-1, 2},
                                                      {-2, 1}};
    for (auto &delta: knight_deltas) {
        int x = square.first + delta.first;
        int y = square.second + delta.second;
        if (x >= 0 && x < 8 && y >= 0 && y < 8 && _board[x][y] == KNIGHT * enemy_color)
            return true;
    }

    // King attacks
    std::vector<std::pair<int, int>> king_deltas = {{-1, -1},
                                                    {-1, 0},
                                                    {-1, 1},
                                                    {0,  -1},
                                                    {0,  1},
                                                    {1,  -1},
                                                    {1,  0},
                                                    {1,  1}};
    for (auto &delta: king_deltas) {
        int x = square.first + delta.first;
        int y = square.second + delta.second;
        if (x >= 0 && x < 8 && y >= 0 && y < 8 && _board[x][y] == KING * enemy_color)
            return true;
    }

    // Sliding attacks
    std::vector<std::pair<int, int>> directions = {{-1, -1},
                                                   {-1, 1},
                                                   {1,  -1},
                                                   {1,  1},
                                                   {-1, 0},
                                                   {1,  0},
                                                   {0,  -1},
                                                   {0,  1}};
    for (auto &dir: directions) {
        int x = square.first + dir.first;
        int y = square.second + dir.second;
        while (x >= 0 && x < 8 && y >= 0 && y < 8) {
            if (_board[x][y] != 0) {
                int piece = _board[x][y];
                if ((dir.first == 0 || dir.second == 0) &&
                    (abs(piece) == ROOK || abs(piece) == QUEEN) && piece * enemy_color > 0)
                    return true;
                if ((dir.first != 0 && dir.second != 0) &&
                    (abs(piece) == BISHOP || abs(piece) == QUEEN) && piece * enemy_color > 0)
                    return true;
                break;
            }
            x += dir.first;
            y += dir.second;
        }
    }
    return false;
}

void Board::retractMove(const Move &move) {
    auto &from = move.from_square;
    auto &to = move.to_square;
    int piece = _board[to.first][to.second];
    _board.at(from.first).at(from.second) = piece;
    _board.at(to.first).at(to.second) = 0;

    // Undo castling
    if (abs(piece) == KING && abs(from.second - to.second) == 2) {
        int rook_from_col = (to.second > from.second) ? 5 : 3;
        int rook_to_col = (to.second > from.second) ? 7 : 0;
        int row = from.first;
        int rook = _board.at(row).at(rook_from_col);
        _board.at(row).at(rook_to_col) = rook;
        _board.at(row).at(rook_from_col) = 0;
    }

    // Undo promotion
    if (move.promotion)
        _board.at(from.first).at(from.second) = PAWN * -turn;

    turn = -turn;
}

Board::Board() { reset(); }

void Board::reset() {
    int initial[8][8] = {
            {-4, -2, -3, -5, -6, -3, -2, -4},
            {-1, -1, -1, -1, -1, -1, -1, -1},
            {0,  0,  0,  0,  0,  0,  0,  0},
            {0,  0,  0,  0,  0,  0,  0,  0},
            {0,  0,  0,  0,  0,  0,  0,  0},
            {0,  0,  0,  0,  0,  0,  0,  0},
            {1,  1,  1,  1,  1,  1,  1,  1},
            {4,  2,  3,  5,  6,  3,  2,  4}
    };
    _board = std::vector(8, std::vector(8, 0));
    for (int i = 0; i < 8; ++i){
    _board.at(i) = std::vector(initial[i], initial[i] + 8);
        for (int j=0;j<8;j++) {
            _board.at(i).at(j) = initial[i][j];
        }

    }
    turn = WHITE;
    while (!event_stack.empty()) event_stack.pop();
}

[[maybe_unused]] void Board::set_fen(const std::string &fen) {
    std::map<char, std::pair<int, int>> piece_map = {
            {'P', {WHITE, PAWN}},
            {'N', {WHITE, KNIGHT}},
            {'B', {WHITE, BISHOP}},
            {'R', {WHITE, ROOK}},
            {'Q', {WHITE, QUEEN}},
            {'K', {WHITE, KING}},
            {'p', {BLACK, PAWN}},
            {'n', {BLACK, KNIGHT}},
            {'b', {BLACK, BISHOP}},
            {'r', {BLACK, ROOK}},
            {'q', {BLACK, QUEEN}},
            {'k', {BLACK, KING}}
    };

    for (auto &row: _board)
        row = std::vector<int>(8, 0);

    size_t space = fen.find(' ');
    std::string placement = fen.substr(0, space);
    std::string turn_str = fen.substr(space + 1, 1);

    int row = 0, col = 0;
    for (char c: placement) {
        if (c == '/') {
            row++;
            col = 0;
        }
        else if (isdigit(c)) col += c - '0';
        else {
            auto &p = piece_map[c];
            _board.at(row).at(col) = p.first == WHITE ? p.second : -p.second;
            col++;
        }
    }

    turn = (turn_str == "w") ? WHITE : BLACK;
}

void Board::push_uci(const std::string &move_str) {
    Move move;
    move.from_square = {8 - (move_str[1] - '0'), move_str[0] - 'a'};
    move.to_square = {8 - (move_str[3] - '0'), move_str[2] - 'a'};
    if (move_str.size() == 5) {
        char promo = move_str[4];
        move.promotion = promo == 'q' ? QUEEN : promo == 'r' ? ROOK :
                                                promo == 'b' ? BISHOP : KNIGHT;
    }

    int &piece = _board.at(move.from_square.first).at(move.from_square.second);
    int &target = _board.at(move.to_square.first).at(move.to_square.second);

    // Handle castling
    if (abs(piece) == KING && abs(move.from_square.second - move.to_square.second) == 2) {
        int rook_from_col = move.to_square.second > move.from_square.second ? 7 : 0;
        int rook_to_col = move.to_square.second > move.from_square.second ? 5 : 3;
        std::pair rook_from = {move.from_square.first, rook_from_col};
        std::pair rook_to = {move.from_square.first, rook_to_col};
        int rook = _board.at(rook_from.first).at(rook_from.second);
        _board.at(rook_to.first).at(rook_to.second) = rook;
        _board.at(rook_from.first).at(rook_from.second) = 0;
    }

    event_stack.emplace(move);
    if (target != 0)
        event_stack.emplace(target);


    target = piece;
    piece = 0;

    if (move.promotion)
        target = move.promotion * turn;

    turn = -turn;
}

bool Board::is_move_legal(const Move& move, int color) {
    // Save original state
    int original_from = _board.at(move.from_square.first).at(move.from_square.second);
    int original_to = _board.at(move.to_square.first).at(move.to_square.second);

    // Simulate move
    _board.at(move.to_square.first).at(move.to_square.second) = original_from;
    _board.at(move.from_square.first).at(move.from_square.second) = 0;

    // Handle promotion
    if (move.promotion)
        _board[move.to_square.first][move.to_square.second] = move.promotion * color;

    // Find king's position
    std::pair<int, int> king_pos;
    bool found = false;
    for (int i = 0; i < 8 && !found; ++i) {
        for (int j = 0; j < 8; ++j) {
            if (_board[i][j] == KING * color) {
                king_pos = {i, j};
                found = true;
                break;
            }
        }
    }

    // Check safety
    bool safe = !is_square_attacked(king_pos, -color);

    // Restore board
    _board[move.from_square.first][move.from_square.second] = original_from;
    _board[move.to_square.first][move.to_square.second] = original_to;

    return safe;
}

void Board::push(const Move &move) {
    event_stack.emplace(move);
    push_uci(move.uci());
}

std::vector<Move> Board::legal_moves() {
    std::vector<Move> moves;

    for (int x = 0; x < 8; ++x) {
        for (int y = 0; y < 8; ++y) {
            int piece = _board[x][y];
            if (piece == 0 || piece * turn <= 0) continue; // Skip empty or opponent's pieces

            int piece_type = abs(piece);

            // Pawn moves
            if (piece_type == PAWN) {
                int direction = -turn;
                int start_row = (turn == WHITE) ? 6 : 1;
                int promotion_row = (turn == WHITE) ? 0 : 7;

                // Single move forward
                int new_x = x + direction;
                if (new_x >= 0 && new_x < 8 && _board[new_x][y] == 0) {
                    if (new_x == promotion_row) {
                        for (int promo : {QUEEN, ROOK, BISHOP, KNIGHT}) {
                            Move move;
                            move.from_square = {x, y};
                            move.to_square = {new_x, y};
                            move.promotion = promo;
                            if (is_move_legal(move, turn))
                                moves.push_back(move);
                        }
                    } else {
                        Move move;
                        move.from_square = {x, y};
                        move.to_square = {new_x, y};
                        if (is_move_legal(move, turn))
                            moves.push_back(move);
                    }
                }

                // Double move from start row
                if (x == start_row) {
                    int new_x2 = x + 2 * direction;
                    if (new_x2 >= 0 && new_x2 < 8 &&
                        _board[x + direction][y] == 0 && _board[new_x2][y] == 0) {
                        Move move;
                        move.from_square = {x, y};
                        move.to_square = {new_x2, y};
                        if (is_move_legal(move, turn))
                            moves.push_back(move);
                    }
                }

                // Captures
                for (int dy : {-1, 1}) {
                    int new_x = x + direction;
                    int new_y = y + dy;
                    if (new_x >= 0 && new_x < 8 && new_y >= 0 && new_y < 8) {
                        if (_board[new_x][new_y] * turn < 0) { // Enemy piece
                            if (new_x == promotion_row) {
                                for (int promo : {QUEEN, ROOK, BISHOP, KNIGHT}) {
                                    Move move;
                                    move.from_square = {x, y};
                                    move.to_square = {new_x, new_y};
                                    move.promotion = promo;
                                    if (is_move_legal(move, turn))
                                        moves.push_back(move);
                                }
                            } else {
                                Move move;
                                move.from_square = {x, y};
                                move.to_square = {new_x, new_y};
                                if (is_move_legal(move, turn))
                                    moves.push_back(move);
                            }
                        }
                    }
                }
            }

                // Knight moves
            else if (piece_type == KNIGHT) {
                std::vector<std::pair<int, int>> deltas = {
                        {-2, -1}, {-1, -2}, {1, -2}, {2, -1},
                        {2, 1}, {1, 2}, {-1, 2}, {-2, 1}
                };
                for (auto& delta : deltas) {
                    int x2 = x + delta.first;
                    int y2 = y + delta.second;
                    if (x2 >= 0 && x2 < 8 && y2 >= 0 && y2 < 8) {
                        if (_board[x2][y2] * turn <= 0) { // Empty or enemy
                            Move move;
                            move.from_square = {x, y};
                            move.to_square = {x2, y2};
                            if (is_move_legal(move, turn))
                                moves.push_back(move);
                        }
                    }
                }
            }

                // Bishop/Rook/Queen moves
            else if (piece_type == BISHOP || piece_type == ROOK || piece_type == QUEEN) {
                std::vector<std::pair<int, int>> directions;
                if (piece_type == BISHOP || piece_type == QUEEN)
                    directions.insert(directions.end(), {{-1,-1}, {-1,1}, {1,-1}, {1,1}});
                if (piece_type == ROOK || piece_type == QUEEN)
                    directions.insert(directions.end(), {{-1,0}, {1,0}, {0,-1}, {0,1}});

                for (auto& dir : directions) {
                    int x2 = x + dir.first;
                    int y2 = y + dir.second;
                    while (x2 >= 0 && x2 < 8 && y2 >= 0 && y2 < 8) {
                        if (_board[x2][y2] * turn <= 0) { // Empty or enemy
                            Move move;
                            move.from_square = {x, y};
                            move.to_square = {x2, y2};
                            if (is_move_legal(move, turn))
                                moves.push_back(move);
                        }
                        if (_board[x2][y2] != 0) break; // Blocked
                        x2 += dir.first;
                        y2 += dir.second;
                    }
                }
            }

                // King moves
            else if (piece_type == KING) {
                std::vector<std::pair<int, int>> deltas = {
                        {-1,-1}, {-1,0}, {-1,1},
                        {0,-1},         {0,1},
                        {1,-1},  {1,0},  {1,1}
                };
                for (auto& delta : deltas) {
                    int x2 = x + delta.first;
                    int y2 = y + delta.second;
                    if (x2 >= 0 && x2 < 8 && y2 >= 0 && y2 < 8) {
                        if (_board[x2][y2] * turn <= 0) { // Empty or enemy
                            Move move;
                            move.from_square = {x, y};
                            move.to_square = {x2, y2};
                            if (is_move_legal(move, turn))
                                moves.push_back(move);
                        }
                    }
                }
            }
        }
    }

    return moves;
}

void Board::pop() {
    if (event_stack.empty()) throw std::runtime_error("No moves to pop");

    auto top = event_stack.top();
    event_stack.pop();

    if (std::holds_alternative<int>(top)) {
        // Handle capture: [Move, CapturedPiece] in stack
        int captured = std::get<int>(top);
        Move move = std::get<Move>(event_stack.top());
        event_stack.pop();

        this->retractMove(move);
        _board[move.to_square.first][move.to_square.second] = captured;
    } else {
        // Handle non-capture
        Move move = std::get<Move>(top);
        this->retractMove(move);
    }
}

bool Board::can_claim_draw() {
    int pawns = 0, queens = 0, rooks = 0, bishops = 0, knights = 0;
    for (auto &row: _board) {
        for (int p: row) {
            int abs_p = abs(p);
            if (abs_p == PAWN) pawns++;
            else if (abs_p == QUEEN) queens++;
            else if (abs_p == ROOK) rooks++;
            else if (abs_p == BISHOP) bishops++;
            else if (abs_p == KNIGHT) knights++;
        }
    }
    return pawns + queens + rooks == 0 && bishops + knights <= 1;
}

bool Board::is_checkmate() {
    // Find king
    std::pair<int, int> king_pos;
    bool found = false;
    for (int i = 0; i < 8 && !found; ++i)
        for (int j = 0; j < 8; ++j)
            if (_board[i][j] == KING * turn) {
                king_pos = {i, j};
                found = true;
                break;
            }
    if (!found) return false;

    if (!is_square_attacked(king_pos, -turn)) return false;
    return legal_moves().empty();
}

bool Board::is_game_over() {
    return is_checkmate() || legal_moves().empty() || can_claim_draw();
}
