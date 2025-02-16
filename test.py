import unittest
import numpy as np
import chess

class TestBoard(unittest.TestCase):
    def setUp(self):
        """Initialize a Board object for testing."""
        self.board = chess.Board()

    def test_initial_board(self):
        """Test that the initial board is set up correctly."""
        expected_board = np.array([
            [-4, -2, -3, -5, -6, -3, -2, -4],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [4, 2, 3, 5, 6, 3, 2, 4]
        ], dtype=np.int64)
        np.testing.assert_array_equal(self.board._board, expected_board)

    def test_set_fen(self):
        """Test setting the board from a FEN string."""
        fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
        self.board.set_fen(fen)
        expected_board = np.array([
            [-4, -2, -3, -5, -6, -3, -2, -4],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [4, 2, 3, 5, 6, 3, 2, 4]
        ], dtype=np.int64)
        np.testing.assert_array_equal(self.board._board, expected_board)
        self.assertEqual(self.board.turn, chess.BLACK)

    def test_push_uci(self):
        """Test applying a move in UCI notation."""
        self.board.push_uci("e2e4")
        expected_board = np.array([
            [-4, -2, -3, -5, -6, -3, -2, -4],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [4, 2, 3, 5, 6, 3, 2, 4]
        ], dtype=np.int64)
        np.testing.assert_array_equal(self.board._board, expected_board)
        self.assertEqual(self.board.turn, chess.BLACK)

    def test_push_uci2(self):
        """Test applying a move in UCI notation."""
        self.board.push_uci("d7d5")
        expected_board = np.array([
            [-4, -2, -3, -5, -6, -3, -2, -4],
            [-1, -1, -1, 0, -1, -1, -1, -1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, -1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [4, 2, 3, 5, 6, 3, 2, 4]
        ], dtype=np.int64)
        np.testing.assert_array_equal(self.board._board, expected_board)
        self.assertEqual(self.board.turn, chess.BLACK)

    def test_push_and_pop(self):
        """Test pushing and popping a move."""
        m1 = chess.Move()
        m1.from_square = (6, 4)
        m1.to_square = (4, 4)
        m2 = chess.Move()
        m2.from_square = (1, 4)
        m2.to_square = (3, 4)
        self.board.push(m1)
        self.board.push(m2)
        self.board.pop()
        expected_board = np.array([
            [-4, -2, -3, -5, -6, -3, -2, -4],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [4, 2, 3, 5, 6, 3, 2, 4]
        ], dtype=np.int64)
        np.testing.assert_array_equal(self.board._board, expected_board)
        self.assertEqual(self.board.turn, chess.BLACK)

    def test_legal_moves(self):
        """Test generating legal moves."""
        self.board.set_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        moves = list(self.board.legal_moves())
        self.assertEqual(len(moves), 20)  # Starting position has 20 legal moves

    def test_is_checkmate(self):
        """Test checkmate detection."""
        self.board.set_fen("8/8/8/8/8/8/q7/K7 b - - 0 1")  # Black king in checkmate
        print(self.board._board)
        self.assertTrue(self.board.is_checkmate())

    def test_is_game_over(self):
        """Test game over detection."""
        self.board.set_fen("8/8/8/8/8/8/8/R7 b - - 0 1")  # Black king in checkmate
        self.assertTrue(self.board.is_game_over())

    def test_can_claim_draw(self):
        """Test draw claim detection."""
        self.board.set_fen("8/8/8/8/8/8/8/4k3 w - - 0 1")  # Insufficient material
        self.assertTrue(self.board.can_claim_draw())

    def test_piece_map(self):
        """Test the piece map generation."""
        self.board.set_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        piece_map = self.board.piece_map()
        self.assertEqual(len(piece_map), 32)  # Starting position has 32 pieces
        self.assertEqual(piece_map[(0, 0)], -4)  # Black rook at a8
        self.assertEqual(piece_map[(7, 4)], 6)  # White king at e1

    def test_piece_at(self):
        """Test retrieving a piece at a specific square."""
        self.board.set_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        self.assertEqual(self.board.piece_at((0, 0)), -4)  # Black rook at a8
        self.assertEqual(self.board.piece_at((7, 4)), 6)  # White king at e1

    def test_push_pop_single_move(self):
        """Test pushing and popping a single move."""
        # Create a move from e2 to e4
        move = chess.Move()
        move.from_square = (6, 4)  # e2
        move.to_square = (4, 4)  # e4

        # Push the move
        self.board.push(move)
        expected_board_after_push = np.array([
            [-4, -2, -3, -5, -6, -3, -2, -4],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],  # Pawn moved to e4
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],  # Pawn removed from e2
            [4, 2, 3, 5, 6, 3, 2, 4]
        ], dtype=np.int64)
        np.testing.assert_array_equal(self.board._board, expected_board_after_push)
        self.assertEqual(self.board.turn, chess.BLACK)  # Turn switched to Black

        # Pop the move
        popped_move = self.board.pop()
        expected_board_after_pop = np.array([
            [-4, -2, -3, -5, -6, -3, -2, -4],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],  # Pawn reverted to e2
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],  # Pawn restored to e2
            [4, 2, 3, 5, 6, 3, 2, 4]
        ], dtype=np.int64)
        np.testing.assert_array_equal(self.board._board, expected_board_after_pop)
        self.assertEqual(self.board.turn, chess.WHITE)  # Turn switched back to White
        self.assertEqual(popped_move.from_square, move.from_square)
        self.assertEqual(popped_move.to_square, move.to_square)

    def test_push_pop_multiple_moves(self):
        """Test pushing and popping multiple moves."""
        # Create moves
        move1 = chess.Move()
        move1.from_square = (6, 4)  # e2
        move1.to_square = (4, 4)  # e4

        move2 = chess.Move()
        move2.from_square = (1, 4)  # e7
        move2.to_square = (3, 4)  # e5

        # Push move1
        self.board.push(move1)
        expected_board_after_move1 = np.array([
            [-4, -2, -3, -5, -6, -3, -2, -4],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],  # Pawn moved to e4
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],  # Pawn removed from e2
            [4, 2, 3, 5, 6, 3, 2, 4]
        ], dtype=np.int64)
        np.testing.assert_array_equal(self.board._board, expected_board_after_move1)
        self.assertEqual(self.board.turn, chess.BLACK)  # Turn switched to Black

        # Push move2
        self.board.push(move2)
        expected_board_after_move2 = np.array([
            [-4, -2, -3, -5, -6, -3, -2, -4],
            [-1, -1, -1, -1, 0, -1, -1, -1],  # Pawn removed from e7
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, -1, 0, 0, 0],  # Pawn moved to e5
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [4, 2, 3, 5, 6, 3, 2, 4]
        ], dtype=np.int64)
        np.testing.assert_array_equal(self.board._board, expected_board_after_move2)
        self.assertEqual(self.board.turn, chess.WHITE)  # Turn switched to White

        # Pop move2
        popped_move2 = self.board.pop()
        np.testing.assert_array_equal(self.board._board, expected_board_after_move1)
        self.assertEqual(self.board.turn, chess.BLACK)  # Turn switched back to Black
        self.assertEqual(popped_move2.from_square, move2.from_square)
        self.assertEqual(popped_move2.to_square, move2.to_square)

        # Pop move1
        popped_move1 = self.board.pop()
        expected_board_after_pop = np.array([
            [-4, -2, -3, -5, -6, -3, -2, -4],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],  # Pawn reverted to e2
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],  # Pawn restored to e2
            [4, 2, 3, 5, 6, 3, 2, 4]
        ], dtype=np.int64)

        np.testing.assert_array_equal(self.board._board, expected_board_after_pop)
        self.assertEqual(self.board.turn, chess.WHITE)  # Turn switched back to White
        self.assertEqual(popped_move1.from_square, move1.from_square)
        self.assertEqual(popped_move1.to_square, move1.to_square)

    def test_is_square_attacked_by_pawn(self):
        """Test if a square is attacked by a pawn."""
        self.board.set_fen("8/8/8/8/8/3p4/8/8 w - - 0 1")  # Black pawn at d3
        self.assertTrue(self.board.is_square_attacked((4, 4), chess.BLACK))  # e4 is attacked by d3 pawn
        self.assertFalse(self.board.is_square_attacked((4, 3), chess.BLACK))  # e5 is not attacked

    def test_is_square_attacked_by_knight(self):
        """Test if a square is attacked by a knight."""
        self.board.set_fen("8/8/8/8/3N4/8/8/8 w - - 0 1")  # White knight at d4
        self.assertFalse(self.board.is_square_attacked((5, 2), chess.WHITE))  # f3 is attacked by d4 knight
        self.assertTrue(self.board.is_square_attacked((5, 1), chess.WHITE))  # f4 is not attacked

    def test_is_square_attacked_by_bishop(self):
        """Test if a square is attacked by a bishop."""
        self.board.set_fen("8/8/8/8/8/2b5/8/8 w - - 0 1")  # Black bishop at c3
        print(self.board._board)
        self.assertTrue(self.board.is_square_attacked((4, 1), chess.BLACK))  # f6 is attacked by c3 bishop
        self.assertFalse(self.board.is_square_attacked((4, 2), chess.BLACK))  # g6 is not attacked
        self.assertTrue(self.board.is_square_attacked((7, 0), chess.BLACK))

    def test_is_square_attacked_by_rook(self):
        """Test if a square is attacked by a rook."""
        self.board.set_fen("8/8/8/8/8/8/8/R7 w - - 0 1")  # White rook at a1
        print(self.board._board)
        self.assertFalse(self.board.is_square_attacked((0, 7), chess.WHITE))  # h8 is attacked by a1 rook
        self.assertTrue(self.board.is_square_attacked((5, 0), chess.WHITE))  # b2 is not attacked

    def test_is_square_attacked_by_queen(self):
        """Test if a square is attacked by a queen."""
        self.board.set_fen("8/8/8/8/8/8/8/Q7 w - - 0 1")  # White queen at a1
        print(self.board._board)
        self.assertTrue(self.board.is_square_attacked((7, 7), chess.WHITE))  # h8 is attacked by a1 queen
        self.assertFalse(self.board.is_square_attacked((1, 1), chess.WHITE))  # b2 is not attacked

    def test_is_square_attacked_by_king(self):
        """Test if a square is attacked by a king."""
        self.board.set_fen("8/8/8/8/8/8/8/4k3 w - - 0 1")  # Black king at e1
        self.assertFalse(self.board.is_square_attacked((1, 4), chess.BLACK))  # e2 is attacked by e1 king
        self.assertTrue(self.board.is_square_attacked((6, 4), chess.BLACK))  # e3 is not attacked

    def test_is_checkmate_simple(self):
        """Test a simple checkmate position."""
        self.board.set_fen("8/8/8/8/8/8/q7/K7 b - - 0 1")  # Black king in checkmate
        print(self.board._board)
        self.assertTrue(self.board.is_checkmate())

    def test_is_checkmate_not_in_check(self):
        """Test a position where the king is not in checkmate."""
        self.board.set_fen("8/8/8/8/8/8/8/4k3 w - - 0 1")  # Black king not in checkmate
        self.assertFalse(self.board.is_checkmate())

    def test_is_checkmate_stalemate(self):
        """Test a stalemate position (not checkmate)."""
        self.board.set_fen("8/8/8/8/8/8/8/4k3 w - - 0 1")  # Black king in stalemate
        self.assertFalse(self.board.is_checkmate())

    def test_is_checkmate_king_can_escape(self):
        """Test a position where the king can escape check."""
        self.board.set_fen("8/8/8/8/8/8/8/4k3 w - - 0 1")  # Black king can escape
        self.assertFalse(self.board.is_checkmate())

    def test_is_checkmate_king_surrounded(self):
        """Test a position where the king is surrounded by its own pieces."""
        self.board.set_fen("8/8/8/8/8/8/8/4k3 w - - 0 1")  # Black king surrounded by its own pieces
        self.assertFalse(self.board.is_checkmate())

if __name__ == "__main__":
    unittest.main()