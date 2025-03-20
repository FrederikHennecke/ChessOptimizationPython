//
// Created by frederik on 3/19/25.
//
#include <cassert>
#include <iostream>

#include "chess.hpp"


void print_board(std::vector<std::vector<int>> board) {
    std::cout << "--------------" << std::endl;
    for (int i = 0; i < board.size(); i++) {
        for (int j = 0; j < board[i].size(); j++) {
            std::cout << board[i][j] << " ";
        }
        std::cout << std::endl;
    }
}

void test_initial_position() {
    Board board;
    board.reset();

    // Test pawn positions
    for(int col = 0; col < 8; col++) {
        assert(board._board[1][col] == BLACK*PAWN);
        assert(board._board[6][col] == WHITE*PAWN);
    }

    // Test back ranks
    assert(board._board[0][0] == BLACK*ROOK);
    assert(board._board[0][4] == BLACK*KING);
    assert(board._board[7][7] == WHITE*ROOK);
    assert(board._board[7][3] == WHITE*QUEEN);
}

void test_pawn_move() {
    Board board;
    board.reset();

    // Push e2e4
    board.push_uci("e2e4");

    // Verify move
    assert(board._board[6][4] == 0);          // e2 empty
    assert(board._board[4][4] == WHITE*PAWN); // e4 has pawn
    assert(board.turn == BLACK);

    // Pop move
    board.pop();
    assert(board._board[6][4] == WHITE*PAWN); // e2 restored
    assert(board._board[4][4] == 0);          // e4 empty
    assert(board.turn == WHITE);
}

void test_capture() {
    Board board;
    board.set_fen("4k3/8/8/3p4/4P3/8/8/4K3 w - - 0 1");

    // Push e4d5
    board.push_uci("e4d5");

    // Verify capture
    assert(board._board[4][3] == 0);          // e4 empty
    assert(board._board[3][3] == WHITE*PAWN); // d5 has white pawn
    assert(board._board[3][3] == WHITE*PAWN); // Black pawn captured

    // Pop should restore both pieces
    board.pop();
    assert(board._board[4][4] == WHITE*PAWN); // e4 restored
    assert(board._board[3][3] == BLACK*PAWN); // d5 restored
}

void test_legal_moves() {
    Board board;
    board.set_fen("4k3/8/8/8/8/8/4P3/4K3 w - - 0 1");

    auto moves = board.legal_moves();
    assert(moves.size() == 6); // King: 3 moves, Pawn: 2 moves

    // Verify pawn moves
    bool found_e3 = false, found_e4 = false;
    for(const auto& move : moves) {
        if(move.from_square == std::pair(6,4)) { // e2
            if(move.to_square == std::pair(5,4)) found_e3 = true;
            if(move.to_square == std::pair(4,4)) found_e4 = true;
        }
    }
    assert(found_e3);
    assert(found_e4);
}

void test_capture_restoration() {
    Board board;
    board.set_fen("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1");

    // White pawn captures black pawn
    board.push_uci("e4d5");

    // Verify capture
    assert(board._board[3][3] == WHITE*PAWN);  // d5
    assert(board._board[4][4] == 0);           // e4

    // Undo move
    board.pop();

    // Verify restoration
    assert(board._board[4][4] == WHITE*PAWN);  // e4
    assert(board._board[3][3] == BLACK*PAWN);  // d5
    assert(board.turn == WHITE);
}

void test_basic_push_pop() {
    Board board;
    board.reset();

    // Initial pawn position
    assert(board._board[6][4] == WHITE*PAWN); // e2
    assert(board.turn == WHITE);

    // Push e2e4
    board.push_uci("e2e4");
    assert(board._board[6][4] == 0);          // e2 empty
    assert(board._board[4][4] == WHITE*PAWN); // e4 has pawn
    assert(board.turn == BLACK);

    // Pop move
    board.pop();
    assert(board._board[6][4] == WHITE*PAWN); // e2 restored
    assert(board._board[4][4] == 0);          // e4 empty
    assert(board.turn == WHITE);
}

void test_capture_restoration2() {
    Board board;
    board.set_fen("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1");

    // Verify initial state
    assert(board._board[4][4] == WHITE*PAWN); // e4
    assert(board._board[3][3] == BLACK*PAWN); // d5

    // Capture pawn
    board.push_uci("e4d5");
    assert(board._board[4][4] == 0);          // e4 empty
    assert(board._board[3][3] == WHITE*PAWN); // d5 has white pawn
    assert(board.turn == BLACK);

    // Undo capture
    board.pop();
    assert(board._board[4][4] == WHITE*PAWN); // e4 restored
    assert(board._board[3][3] == BLACK*PAWN); // d5 restored
    assert(board.turn == WHITE);
}

void test_multiple_move_rollback() {
    Board board;
    board.reset();

    // Sequence: 1. e4 2. e5 3. Nf3
    board.push_uci("e2e4");  // White
    board.push_uci("e7e5");  // Black
    board.push_uci("g1f3");  // White

    // Verify final state
    assert(board._board[4][4] == WHITE*PAWN);
    assert(board._board[3][4] == BLACK*PAWN);
    assert(board._board[5][5] == WHITE*KNIGHT);
    assert(board.turn == BLACK);

    // Rollback all moves
    board.pop();  // Nf3
    board.pop();  // e5
    board.pop();  // e4

    // Verify initial state
    assert(board._board[6][4] == WHITE*PAWN);
    assert(board._board[1][4] == BLACK*PAWN);
    assert(board._board[7][6] == WHITE*KNIGHT);
    assert(board.turn == WHITE);
}

void test_check_state_rollback() {
    Board board;
    board.set_fen("4k3/4r3/8/8/8/8/4R3/4K3 w - - 0 1");

    // Push check
    board.push_uci("e2e7");  // Rook capture + check
    assert(board.is_checkmate() == false);
    assert(board.is_square_attacked({4,4}, WHITE)); // e8 is {0,4}?

    // Undo check
    board.pop();
    assert(board._board[6][4] == WHITE*ROOK);  // e2 restored
    assert(board._board[1][4] == BLACK*ROOK);   // e7 restored
    assert(board.is_square_attacked({4,4}, BLACK) == true);
}

void test_fen_roundtrip() {
    Board board;
    std::string original_fen = "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1";
    board.set_fen(original_fen);
    auto tmp = board._board;

    // Make and undo moves
    board.push_uci("e4c5");  // Capture
    board.push_uci("g1f3");  // Knight move
    board.pop();
    board.pop();

    // Verify FEN matches original
    assert(board._board == tmp);
}

void test_stack_underflow_protection() {
    Board board;
    board.reset();

    try {
        board.pop();  // Should throw
        assert(false); // Shouldn't reach here
    } catch (const std::runtime_error& e) {
        assert(std::string(e.what()) == "No moves to pop");
    }
}

void test_multiple_consecutive_captures() {
    Board board;
    // Initial position: White can capture 3 black pieces in sequence
    board.set_fen("2k5/2p5/3n4/3R4/4P3/5b2/8/2K5 w - - 0 1");

    print_board(board._board);

    // First capture: pawn takes pawn (d5xc6)
    board.push_uci("d5d6");
    print_board(board._board);
    assert(board._board[3][3] == 0);          // d5 empty
    assert(board._board[2][3] == WHITE*ROOK); // c6 now has white pawn
    assert(board._board[1][2] == BLACK*PAWN); // c7 still has black pawn
    assert(board.turn == BLACK);

    // Second capture: pawn takes knight (c6xd7)
    board.push_uci("d6d7");
    print_board(board._board);
    assert(board._board[2][2] == 0);          // c6 empty
    assert(board._board[1][3] == WHITE*ROOK); // d7 now has white pawn
    assert(board._board[5][3] == 0);          // d6 empty
    assert(board.turn == WHITE);

    // Third capture: pawn takes bishop (e4xf3)
    board.push_uci("f3e4");
    print_board(board._board);
    assert(board._board[3][4] == 0);          // e4 empty
    assert(board._board[4][4] == BLACK*BISHOP); // f3 now has white pawn
    assert(board._board[2][5] == 0);           // Original bishop gone
    assert(board.turn == BLACK);

    // Undo all moves
    board.pop(); // Undo e4xf3
    print_board(board._board);
    assert(board._board[4][4] == WHITE*PAWN); // e4 restored
    assert(board._board[5][5] == BLACK*BISHOP); // f3 bishop restored
    assert(board.turn == WHITE);

    board.pop(); // Undo c6xd7
    print_board(board._board);
    assert(board._board[2][3] == WHITE*ROOK); // c6 restored
    assert(board._board[1][3] == 0);          // d7 empty
    assert(board.turn == BLACK);

    board.pop(); // Undo d5xc6
    print_board(board._board);
}

int main() {
    test_initial_position();
    test_pawn_move();
    test_capture();
    test_legal_moves();
    test_capture_restoration();

    test_basic_push_pop();
    test_capture_restoration2();
    test_multiple_move_rollback();
    test_check_state_rollback();
    test_fen_roundtrip();
    test_stack_underflow_protection();

    test_multiple_consecutive_captures();

    std::cout << "All basic board tests passed!" << std::endl;
    return 0;
}