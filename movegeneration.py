import os
from typing import Dict, List, Any
import chess
import time
import numpy as np
from evaluate import evaluate_board, move_value, check_end_game

debug_info: Dict[str, Any] = {"engine": "pypy"}

MATE_SCORE = 1000000000
MATE_THRESHOLD = 999000000


def next_move(depth: int, board: chess.Board, time_limit: float, name: str, debug=True) -> chess.Move:
    """
    What is the next best move?
    Stops calculation if time_limit is reached.
    """
    debug_info.clear()
    debug_info["nodes"] = 0
    debug_info["engine"] = name
    t0 = time.time()

    move = minimax_root_with_time(depth, board, time_limit, t0)

    debug_info["time"] = time.time() - t0
    if debug:
        log_info(f"info {debug_info}")
    log_info(f"Total moves calculated: {debug_info['nodes']}")
    return move


def order_moves(board: chess.Board) -> List[chess.Move]:
    """Generate legal moves sorted by heuristic value."""
    endgame = check_end_game(board)
    is_white = board.turn == chess.WHITE

    moves = []
    for move in board.legal_moves:
        score = move_value(board, move, endgame)
        moves.append((score, move))

    return [m for _, m in sorted(moves, key=lambda x: x[0], reverse=is_white)]


def minimax_root_with_time(depth: int, board: chess.Board, time_limit: float, start_time: float) -> chess.Move:
    """
    What is the highest value move per our evaluation function?
    Stops calculation if time_limit is reached.
    """
    maximize = board.turn == chess.WHITE
    best_value = -float("inf") if maximize else float("inf")
    best_move_found = None

    moves = order_moves(board)

    for move in moves:
        if time.time() - start_time >= time_limit:
            break

        board.push(move)
        if board.can_claim_draw():
            value = 0.0
        else:
            value = minimax_with_time(depth - 1, board, -float("inf"), float("inf"), not maximize, time_limit,
                                      start_time)
        board.pop()

        if maximize and value > best_value:
            best_value = value
            best_move_found = move
        elif not maximize and value < best_value:
            best_value = value
            best_move_found = move

    return best_move_found if best_move_found else moves[0]


def minimax_with_time(
        depth: int,
        board: chess.Board,
        alpha: float,
        beta: float,
        is_maximising_player: bool,
        time_limit: float,
        start_time: float
) -> float:
    """
    Core minimax logic with time constraint.
    """
    debug_info["nodes"] += 1

    if time.time() - start_time >= time_limit:
        return 0  # Return a neutral evaluation if time runs out

    if board.is_checkmate():
        return -MATE_SCORE if is_maximising_player else MATE_SCORE
    elif board.is_game_over():
        return 0

    if depth == 0:
        return evaluate_board(board)

    moves = order_moves(board)
    if is_maximising_player:
        max_eval = -float("inf")
        for move in moves:
            if time.time() - start_time >= time_limit:
                break

            board.push(move)
            eval = minimax_with_time(depth - 1, board, alpha, beta, False, time_limit, start_time)
            board.pop()

            max_eval = max(max_eval, eval)
            alpha = max(alpha, max_eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float("inf")
        for move in moves:
            if time.time() - start_time >= time_limit:
                break

            board.push(move)
            eval = minimax_with_time(depth - 1, board, alpha, beta, True, time_limit, start_time)
            board.pop()

            min_eval = min(min_eval, eval)
            beta = min(beta, min_eval)
            if beta <= alpha:
                break
        return min_eval


def log_info(message: str) -> None:
    """
    Logs a message to a file.
    """
    LOG_FILE = rf"/home/frederik/PycharmProjects/ChessOptimizationPython/logs/chess_engine_log_{debug_info['engine']}.txt"  # Path to the log file
    with open(LOG_FILE, "a") as log_file:
        log_file.write(message + "\n")

