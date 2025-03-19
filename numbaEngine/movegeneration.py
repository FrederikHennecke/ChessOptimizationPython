from typing import Dict, List, Any, Optional
import chess
import time
from evaluate import evaluate_board, move_value, check_end_game
import random

debug_info: Dict[str, Any] = {"engine": "pypy"}

MATE_SCORE = 1000000000
MATE_THRESHOLD = 999000000


def next_move(
        board: chess.Board,
        time_limit: float,
        name: str,
        debug=True
) -> chess.Move:
    """
    Uses iterative deepening to search deeper until time runs out.
    """
    debug_info.clear()
    debug_info["nodes"] = 0
    debug_info["engine"] = name
    t0 = time.perf_counter()
    best_move = None
    depth = 1

    while time.perf_counter() - t0 < time_limit:
        current_move = minimax_root(
            depth,
            board,
            t0,
            time_limit
        )
        if current_move is not None:
            best_move = current_move
            # Log progress for each completed depth
        depth += 1

    debug_info["time"] = time.perf_counter() - t0
    if debug:
        log_info(f"Final stats: {debug_info}")
    return best_move if best_move else random.choice(list(board.legal_moves()))


def minimax_root(
        max_depth: int,
        board: chess.Board,
        start_time: float,
        time_limit: float,
) -> Optional[chess.Move]:
    """
    Iterative deepening root with node counting.
    """
    best_value = -float("inf") if board.turn == chess.WHITE else float("inf")
    best_move = None
    moves = order_moves(board)

    for move in moves:
        if time.perf_counter() - start_time >= time_limit:
            return None

        board.push(move)
        value = minimax(
            max_depth - 1,
            board,
            -float("inf"),
            float("inf"),
            board.turn == chess.WHITE,
            start_time,
            time_limit
        )
        board.pop()

        if (board.turn == chess.WHITE and value > best_value) or \
                (board.turn == chess.BLACK and value < best_value):
            best_value = value
            best_move = move

    return best_move


def order_moves(board: chess.Board) -> List[chess.Move]:
    """Generate legal moves sorted by heuristic value."""
    endgame = check_end_game(board._board)
    is_white = board.turn == chess.WHITE

    moves = []
    for move in board.legal_moves():
        score = move_value(board._board, move, endgame)
        moves.append((score, move))

    return [m for _, m in sorted(moves, key=lambda x: x[0], reverse=is_white)]


def minimax(
        depth: int,
        board: chess.Board,
        alpha: float,
        beta: float,
        is_maximizing: bool,
        start_time: float,
        time_limit: float,
) -> float:
    """
    Updated minimax with proper node counting.
    """
    debug_info["nodes"] += 1  # Increment node count here

    if time.perf_counter() - start_time >= time_limit:
        return 0

    if board.is_checkmate():
        return -MATE_SCORE if is_maximizing else MATE_SCORE
    elif board.is_game_over():
        return 0

    if depth == 0:
        return evaluate_board(board._board)

    moves = order_moves(board)
    if is_maximizing:
        max_eval = -float("inf")
        for move in moves:
            board.push(move)
            eval = minimax(depth - 1, board, alpha, beta, False, start_time, time_limit)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float("inf")
        for move in moves:
            board.push(move)
            eval = minimax(depth - 1, board, alpha, beta, True, start_time, time_limit)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


def log_info(message: str) -> None:
    """
    Logs a message to a file.
    """
    LOG_FILE = rf"/home/frederik/repos/ChessOptimizationPython/logs/chess_engine_log_{debug_info['engine']}.txt"  # Path to the log file
    with open(LOG_FILE, "a") as log_file:
        log_file.write(message + "\n")
