import pytest
from chess import Board, Move

PAWN = 1
KNIGHT = 2
BISHOP = 3
ROOK = 4
QUEEN = 5
KING = 6

WHITE = 1
BLACK = -1


def create_move(from_x, from_y, to_x, to_y, promotion=0):
    m = Move()
    m.from_x = from_x
    m.from_y = from_y
    m.to_x = to_x
    m.to_y = to_y
    m.promotion = promotion
    return m


def test_initial_position():
    board = Board()
    board.reset()

    for col in range(8):
        assert board._board_view[1, col] == BLACK * PAWN
        assert board._board_view[6, col] == WHITE * PAWN

    assert board._board_view[0, 0] == BLACK * ROOK
    assert board._board_view[0, 4] == BLACK * KING
    assert board._board_view[7, 7] == WHITE * ROOK
    assert board._board_view[7, 3] == WHITE * QUEEN


def test_pawn_move():
    board = Board()
    board.reset()

    # Push e2e4
    m = create_move(6, 4, 4, 4)
    board.push(m)

    assert board._board_view[6, 4] == 0
    assert board._board_view[4, 4] == WHITE * PAWN
    assert board.turn == BLACK

    board.pop()
    assert board._board_view[6, 4] == WHITE * PAWN
    assert board._board_view[4, 4] == 0
    assert board.turn == WHITE


def test_capture():
    board = Board()
    board.set_fen("4k3/8/8/3p4/4P3/8/8/4K3 w - - 0 1")

    # Push e4d5
    m = create_move(4, 4, 3, 3)
    board.push(m)

    assert board._board_view[4, 4] == 0
    assert board._board_view[3, 3] == WHITE * PAWN

    board.pop()
    assert board._board_view[4, 4] == WHITE * PAWN
    assert board._board_view[3, 3] == BLACK * PAWN


def test_legal_moves():
    board = Board()
    for col in range(8):
        for row in range(8):
            print(board._board_view[row, col], end=" ")
        print()
    board.set_fen("4k3/8/8/8/8/8/4P3/4K3 w - - 0 1")
    moves = board.legal_moves()
    for m in moves:
        print(m)
    assert len(moves) == 6  # King moves + pawn moves

    found_e3 = found_e4 = False
    for move in moves:
        if move.from_x == 6 and move.from_y == 4:
            if move.to_x == 5 and move.to_y == 4:
                found_e3 = True
            if move.to_x == 4 and move.to_y == 4:
                found_e4 = True
    assert found_e3
    assert found_e4


def test_capture_restoration():
    board = Board()
    board.set_fen("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1")

    m = create_move(4, 4, 3, 3)  # e4d5
    board.push(m)

    assert board._board_view[3, 3] == WHITE * PAWN
    assert board._board_view[4, 4] == 0

    board.pop()
    assert board._board_view[4, 4] == WHITE * PAWN
    assert board._board_view[3, 3] == BLACK * PAWN
    assert board.turn == WHITE


def test_multiple_move_rollback():
    board = Board()
    board.reset()

    # 1. e4
    board.push(create_move(6, 4, 4, 4))
    # 2. e5
    board.push(create_move(1, 4, 3, 4))
    # 3. Nf3
    board.push(create_move(7, 6, 5, 5))

    assert board._board_view[4, 4] == WHITE * PAWN
    assert board._board_view[3, 4] == BLACK * PAWN
    assert board._board_view[5, 5] == WHITE * KNIGHT
    assert board.turn == BLACK

    board.pop()  # Nf3
    board.pop()  # e5
    board.pop()  # e4

    assert board._board_view[6, 4] == WHITE * PAWN
    assert board._board_view[1, 4] == BLACK * PAWN
    assert board._board_view[7, 6] == WHITE * KNIGHT
    assert board.turn == WHITE


def test_check_state_rollback():
    board = Board()
    board.set_fen("4k3/4r3/8/8/8/8/4R3/4K3 w - - 0 1")

    m = create_move(6, 4, 1, 4)  # Rook e2e7
    board.push(m)

    assert board.is_checkmate() == False
    assert board._is_square_attacked((0, 4), WHITE)  # Black king at (0,4)

    board.pop()
    assert board._board_view[6, 4] == WHITE * ROOK
    assert board._board_view[1, 4] == BLACK * ROOK


def test_fen_roundtrip():
    board = Board()
    original_fen = "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1"
    board.set_fen(original_fen)
    initial_board = board._board_array.copy()

    # Capture c5
    board.push(create_move(4, 4, 3, 2))  # e4c5
    # Knight move (already in position in this FEN)
    board.push(create_move(5, 5, 4, 3))  # Nf3d4
    board.pop()
    board.pop()

    for i in range(len(initial_board)):
        for j in range(len(initial_board)):
            assert (board._board_array[i][j] == initial_board[i][j])


def test_rook_movement():
    board = Board()
    board.set_fen("4k3/8/8/8/2R5/8/8/4K3 w - - 0 1")  # White rook at c4 (x=4, y=2)

    moves = board.legal_moves()
    valid_moves = {(3, 2), (5, 2), (4, 1), (4, 3), (4, 0), (4, 4), (4, 5), (4, 6), (4, 7)}  # All straight moves

    generated = {(m.to_x, m.to_y) for m in moves if m.from_x == 4 and m.from_y == 2}
    assert generated == valid_moves, f"Invalid rook moves: {generated}"

def test_stack_underflow_protection():
    board = Board()
    board.reset()

    with pytest.raises(IndexError):
        board.pop()

def test_whatever():
    # Test 1: Pawn shouldn't capture same color
    board = Board()
    board.set_fen("8/8/8/3P4/4P3/8/8/8 w - - 0 1")
    moves = board.legal_moves()
    assert not any(m.to_x == 4 and m.to_y == 4 for m in moves)  # e5->e4 capture

    # Test 2: King should be in checkmate
    board.set_fen("3k4/3Q3p/8/8/8/8/8/3R1K2 b - - 0 1")
    print()
    for i in range(len(board._board_view)):
        for j in range(len(board._board_view)):
            print(board._board_view[i,j], end="")
        print()

    assert bool(board.is_checkmate())
    assert len(board.legal_moves()) == 0

if __name__ == "__main__":
    pytest.main([__file__])