# cython: language_level=3
# movegeneration.pyx
from libc.stdlib cimport malloc, free, qsort
from posix.time cimport clock_gettime, timespec, CLOCK_MONOTONIC
from libc.math cimport INFINITY as DBL_MAX
cimport evaluate

cdef:
    double MATE_SCORE = 1000000000.0
    dict debug_info = {}
    int MAX_DEPTH = 64

cdef double perf_counter():
    cdef timespec ts
    clock_gettime(CLOCK_MONOTONIC, &ts)
    return ts.tv_sec + ts.tv_nsec * 1e-9

cpdef Move next_move(
    Board board,
    double time_limit,
    unicode engine_name,
    bint debug
):
    cdef:
        double t0 = perf_counter()
        int depth = 1
        Move best_move = Move()
        Move current_move

    debug_info.clear()
    debug_info[b"nodes"] = 0
    debug_info[b"engine"] = str(engine_name)

    while perf_counter() - t0 < time_limit:
        current_move = minimax_root(depth, board, t0, time_limit)
        if current_move is not None:
            best_move = current_move
        depth += 1
        if depth > MAX_DEPTH:
            break

    debug_info[b"time"] = perf_counter() - t0
    if debug:
        log_info(f"Final stats: {debug_info}")
    return best_move

cdef Move minimax_root(int max_depth, Board board, double start_time, double time_limit):
    cdef:
        double best_value = -DBL_MAX if board.turn == 1 else DBL_MAX
        Move best_move = Move()
        MoveOrderEntry *entries
        int i, num_moves
        list moves = list(board.legal_moves())
        Move current_move

    num_moves = len(moves)
    entries = <MoveOrderEntry *> malloc(num_moves * sizeof(MoveOrderEntry))

    try:
        # Populate entries
        for i in range(num_moves):
            entries[i].score = evaluate.move_value(board, moves[i], evaluate.check_end_game(board))
            entries[i].from_x = moves[i].from_x
            entries[i].from_y = moves[i].from_y
            entries[i].to_x = moves[i].to_x
            entries[i].to_y = moves[i].to_y
            entries[i].promotion = moves[i].promotion

        qsort(entries, num_moves, sizeof(MoveOrderEntry), &compare_entries)

        # Search through ordered moves
        for i in range(num_moves):
            current_move = Move()
            current_move.from_x = entries[i].from_x
            current_move.from_y = entries[i].from_y
            current_move.to_x = entries[i].to_x
            current_move.to_y = entries[i].to_y
            current_move.promotion = entries[i].promotion

            board.push(current_move)
            value = minimax(max_depth - 1, board, -DBL_MAX, DBL_MAX,
                            board.turn == 1, start_time, time_limit)
            board.pop()

            if (value > best_value and board.turn == 1) or \
                    (value < best_value and board.turn == -1):
                best_value = value
                best_move = current_move
    finally:
        free(entries)

    return best_move

cdef double minimax(int depth, Board board, double alpha, double beta, bint is_maximizing,
                    double start_time, double time_limit):
    """Optimized alpha-beta minimax with node counting."""
    debug_info[b"nodes"] += 1

    if perf_counter() - start_time >= time_limit:
        return 0.0

    if board.is_checkmate():
        return -MATE_SCORE if is_maximizing else MATE_SCORE
    if board.is_game_over() or depth == 0:
        return evaluate.evaluate_board(board)

    cdef:
        list moves = board.legal_moves()
        int num_moves = len(moves)
        Move move
        double value
        double best_value

    if is_maximizing:
        best_value = -DBL_MAX
        for move in moves:
            board.push(move)
            value = minimax(depth - 1, board, alpha, beta, False, start_time, time_limit)
            board.pop()
            best_value = max(best_value, value)
            alpha = max(alpha, best_value)
            if beta <= alpha:
                break
        return best_value
    else:
        best_value = DBL_MAX
        for move in moves:
            board.push(move)
            value = minimax(depth - 1, board, alpha, beta, True, start_time, time_limit)
            board.pop()
            best_value = min(best_value, value)
            beta = min(beta, best_value)
            if beta <= alpha:
                break
        return best_value

cpdef void log_info(str message):
    """Optimized logging function."""
    cdef str LOG_FILE = rf"/home/frederik/repos/ChessOptimizationPython/logs/chess_engine_log_{debug_info[b'engine']}.txt"
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")

# PyCharm does not like this function but it works
cdef int compare_entries(const void *a, const void *b) noexcept nogil:
    cdef MoveOrderEntry *ea = <MoveOrderEntry *> a
    cdef MoveOrderEntry *eb = <MoveOrderEntry *> b
    return -1 if ea.score > eb.score else (1 if ea.score < eb.score else 0)