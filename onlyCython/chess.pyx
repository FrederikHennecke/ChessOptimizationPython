# cython: language_level=3
import numpy as np
cdef class Move:
    def __init__(self):
        self.from_x = -1
        self.from_y = -1
        self.to_x = -1
        self.to_y = -1
        self.promotion = 0


    def __str__(self):
        if self.from_x == -1 or self.to_x == -1:
            return "Invalid move"

        def square_to_notation(square):
            x, y = square
            file = chr(ord('a') + y)
            rank = str(8 - x)
            return file + rank

        from_notation = square_to_notation((self.from_x, self.from_y))
        to_notation = square_to_notation((self.to_x, self.to_y))

        if self.promotion:
            promotion_piece = ""
            if self.promotion == QUEEN:
                promotion_piece = "q"
            elif self.promotion == ROOK:
                promotion_piece = "r"
            elif self.promotion == BISHOP:
                promotion_piece = "b"
            elif self.promotion == KNIGHT:
                promotion_piece = "n"
            return f"{from_notation}{to_notation}{promotion_piece}"
        else:
            return f"{from_notation}{to_notation}"

cdef class Board:
    def __init__(self):
        self.turn = WHITE
        self._board_array = np.array([
            [-4,-2,-3,-5,-6,-3,-2,-4],
            [-1,-1,-1,-1,-1,-1,-1,-1],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [1,1,1,1,1,1,1,1],
            [4,2,3,5,6,3,2,4]
        ], dtype=np.int32)
        self._board_view = self._board_array.copy()
        self.event = []

    cpdef void reset(self):
        self.__init__()

    cpdef void set_fen(self, unicode fen):
        cdef dict piece_map = {
            'P': (WHITE, PAWN),
            'N': (WHITE, KNIGHT),
            'B': (WHITE, BISHOP),
            'R': (WHITE, ROOK),
            'Q': (WHITE, QUEEN),
            'K': (WHITE, KING),
            'p': (BLACK, PAWN),
            'n': (BLACK, KNIGHT),
            'b': (BLACK, BISHOP),
            'r': (BLACK, ROOK),
            'q': (BLACK, QUEEN),
            'k': (BLACK, KING)
        }

        self._board_view = np.zeros((8,8), dtype=np.int32)

        parts = fen.split(' ')
        piece_placement = parts[0]

        cdef int row = 0, col = 0
        cdef str c
        for c in piece_placement:
            if c == '/':
                row += 1
                col = 0
            elif c.isdigit():
                col += int(c)
            else:
                color, piece_type = piece_map[c]
                self._board_view[row, col] = piece_type if color == WHITE else -piece_type
                col += 1

        self.turn = WHITE if parts[1] == "w" else BLACK

    cpdef void push_uci(self, unicode move):
        if len(move) < 4:
            return

        cdef int from_x = 8 - int(move[1])
        cdef int from_y = ord(move[0]) - ord('a')
        cdef int to_x = 8 - int(move[3])
        cdef int to_y = ord(move[2]) - ord('a')
        cdef int promotion = 0

        if len(move) == 5:
            promo_char = move[4].lower()
            if promo_char == 'q':
                promotion = QUEEN
            elif promo_char == 'r':
                promotion = ROOK
            elif promo_char == 'b':
                promotion = BISHOP
            elif promo_char == 'n':
                promotion = KNIGHT

        cdef int piece = self._board_view[from_x, from_y]
        cdef int old_piece = self._board_view[to_x, to_y]

        # Handle castling
        if abs(piece) == KING and abs(from_y - to_y) == 2:
            if to_y > from_y:  # Kingside
                self._board_view[from_x, 5] = self._board_view[from_x, 7]
                self._board_view[from_x, 7] = 0
            else:  # Queenside
                self._board_view[from_x, 3] = self._board_view[from_x, 0]
                self._board_view[from_x, 0] = 0

        if old_piece != 0:
            self.event.append(old_piece)

        self._board_view[to_x, to_y] = piece
        self._board_view[from_x, from_y] = 0

        if promotion:
            self._board_view[to_x, to_y] = promotion * self.turn

        self.turn = -self.turn

    cpdef list legal_moves(self):
        cdef list moves = []
        cdef list directions = []
        cdef int x, y, dx, dy, direction, start_row, promotion_row
        cdef int x2, y2, piece, piece_type, promo
        cdef Move move

        for x in range(8):
            for y in range(8):
                piece = self._board_view[x, y]
                if piece == 0 or (piece * self.turn) <= 0:
                    continue

                piece_type = abs(piece)

                if piece_type == PAWN:
                    direction = -self.turn
                    start_row = 6 if self.turn == WHITE else 1
                    promotion_row = 0 if self.turn == WHITE else 7

                    # Single move forward
                    if 0 <= x + direction < 8 and self._board_view[x + direction, y] == 0:
                        if x + direction == promotion_row:
                            for promo in [QUEEN, ROOK, BISHOP, KNIGHT]:
                                move = Move()
                                move.from_x, move.from_y = (x, y)
                                move.to_x, move.to_y = (x + direction, y)
                                move.promotion = promo
                                if self._is_move_legal(move):
                                    moves.append(move)
                        else:
                            move = Move()
                            move.from_x, move.from_y = (x, y)
                            move.to_x, move.to_y = (x + direction, y)
                            if self._is_move_legal(move):
                                moves.append(move)

                    # Double move
                    if x == start_row and self._board_view[x + direction, y] == 0 \
                            and self._board_view[x + 2 * direction, y] == 0:
                        move = Move()
                        move.from_x, move.from_y  = (x, y)
                        move.to_x, move.to_y = (x + 2 * direction, y)
                        if self._is_move_legal(move):
                            moves.append(move)

                    # Captures
                    for dy in [-1, 1]:
                        if 0 <= y + dy < 8 and 0 <= x + direction < 8:
                            if (self._board_view[x + direction, y + dy] * self.turn) < 0:
                                if x + direction == promotion_row:
                                    for promo in [QUEEN, ROOK, BISHOP, KNIGHT]:
                                        move = Move()
                                        move.from_x, move.from_y = (x, y)
                                        move.to_x, move.to_y = (x + direction, y + dy)
                                        move.promotion = promo
                                        if self._is_move_legal(move):
                                            moves.append(move)
                                else:
                                    move = Move()
                                    move.from_x, move.from_y = (x, y)
                                    move.to_x, move.to_y = (x + direction, y + dy)
                                    if self._is_move_legal(move):
                                        moves.append(move)

                elif piece_type == KNIGHT:
                    for dx, dy in [(-2, -1), (-1, -2), (1, -2), (2, -1),
                                   (2, 1), (1, 2), (-1, 2), (-2, 1)]:
                        x2 = x + dx
                        y2 = y + dy
                        if 0 <= x2 < 8 and 0 <= y2 < 8:
                            if (self._board_view[x2, y2] * self.turn) <= 0:
                                move = Move()
                                move.from_x, move.from_y = (x, y)
                                move.to_x, move.to_y= (x2, y2)
                                if self._is_move_legal(move):
                                    moves.append(move)

                elif piece_type in (BISHOP, ROOK, QUEEN):
                    directions = []  # Reset directions for each piece
                    if piece_type in (BISHOP, QUEEN):
                        directions.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])
                    if piece_type in (ROOK, QUEEN):
                        directions.extend([(-1, 0), (1, 0), (0, -1), (0, 1)])

                    for dx, dy in directions:
                        x2, y2 = x + dx, y + dy
                        while 0 <= x2 < 8 and 0 <= y2 < 8:
                            if (self._board_view[x2, y2] * self.turn) <= 0:
                                move = Move()
                                move.from_x, move.from_y = (x, y)
                                move.to_x, move.to_y = (x2, y2)
                                if self._is_move_legal(move):
                                    moves.append(move)
                            if self._board_view[x2, y2] != 0:
                                break
                            x2 += dx
                            y2 += dy

                elif piece_type == KING:
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            x2 = x + dx
                            y2 = y + dy
                            if 0 <= x2 < 8 and 0 <= y2 < 8:
                                if (self._board_view[x2, y2] * self.turn) <= 0:
                                    move = Move()
                                    move.from_x, move.from_y = (x, y)
                                    move.to_x, move.to_y = (x2, y2)
                                    if self._is_move_legal(move):
                                        moves.append(move)
        return moves

    cpdef bint _is_move_legal(self, Move move):
        cdef int original_piece = self._board_view[move.to_x, move.to_y]
        cdef int moving_piece = self._board_view[move.from_x, move.from_y]
        cdef tuple king_pos
        cdef bint is_legal

        # Make the move
        self._board_view[move.to_x, move.to_y] = moving_piece
        self._board_view[move.from_x, move.from_y] = 0

        # Apply promotion
        if move.promotion:
            self._board_view[move.to_x, move.to_y] = move.promotion * self.turn

        # Find king position
        king_pos = self._find_king(self.turn)

        # Check safety
        is_legal = not self._is_square_attacked(king_pos, -self.turn)

        # Undo the move
        self._board_view[move.from_x, move.from_y] = moving_piece
        self._board_view[move.to_x, move.to_y] = original_piece

        return is_legal

    cpdef tuple _find_king(self, int color):
        cdef int x, y
        for x in range(8):
            for y in range(8):
                if self._board_view[x, y] == KING * color:
                    return (x, y)
        return (-1, -1)

    cpdef bint _is_square_attacked(self, tuple square, int enemy_color):
        if square[0] == -1:
            return False

        cdef int x, y, dx, dy, x2, y2, piece_type
        cdef list directions

        # Pawn attacks
        cdef list pawn_dirs = [(1, -1), (1, 1)] if enemy_color == WHITE else [(-1, -1), (-1, 1)]
        for dx, dy in pawn_dirs:
            x = square[0] + dx
            y = square[1] + dy
            if 0 <= x < 8 and 0 <= y < 8:
                if self._board_view[x, y] == PAWN * enemy_color:
                    return True

        # Knight attacks
        cdef list knight_dirs = [(-2, -1), (-1, -2), (1, -2), (2, -1),
                                 (2, 1), (1, 2), (-1, 2), (-2, 1)]
        for dx, dy in knight_dirs:
            x = square[0] + dx
            y = square[1] + dy
            if 0 <= x < 8 and 0 <= y < 8:
                if self._board_view[x, y] == KNIGHT * enemy_color:
                    return True

        # King attacks
        cdef list king_dirs = [(-1, -1), (-1, 0), (-1, 1),
                               (0, -1), (0, 1),
                               (1, -1), (1, 0), (1, 1)]
        for dx, dy in king_dirs:
            x = square[0] + dx
            y = square[1] + dy
            if 0 <= x < 8 and 0 <= y < 8:
                if self._board_view[x, y] == KING * enemy_color:
                    return True

        # Sliding pieces
        cdef dict sliding_dirs = {
            BISHOP: [(-1, -1), (-1, 1), (1, -1), (1, 1)],
            ROOK: [(-1, 0), (1, 0), (0, -1), (0, 1)],
            QUEEN: [(-1, -1), (-1, 1), (1, -1), (1, 1),
                    (-1, 0), (1, 0), (0, -1), (0, 1)]
        }

        for piece_type, directions in sliding_dirs.items():
            for dx, dy in directions:
                x, y = square[0] + dx, square[1] + dy
                while 0 <= x < 8 and 0 <= y < 8:
                    if self._board_view[x, y] != 0:
                        if self._board_view[x, y] == piece_type * enemy_color:
                            return True
                        break
                    x += dx
                    y += dy

        return False

    cpdef bint is_checkmate(self):
        if not self._is_square_attacked(self._find_king(-self.turn), self.turn):
            return False

        cdef Move move
        cdef int original_piece
        cdef bint has_legal_moves = False

        for move in self.legal_moves():
            original_piece = self._board_view[move.to_x, move.to_y]

            # Make move
            self._board_view[move.to_x, move.to_y] = self._board_view[
                move.from_x, move.from_y]
            self._board_view[move.from_x, move.from_y] = 0

            # Check king safety
            king_pos = (move.to_x, move.to_y) if abs(
                self._board_view[move.to_x, move.to_y]) == KING else self._find_king(-self.turn)
            if not self._is_square_attacked(king_pos, self.turn):
                has_legal_moves = True

            # Undo move
            self._board_view[move.from_x, move.from_y] = self._board_view[
                move.to_x, move.to_y]
            self._board_view[move.to_x, move.to_y] = original_piece

            if has_legal_moves:
                return False

        return True

    cpdef bint can_claim_draw(self):
        cdef int count_pawns = 0, count_queens = 0, count_rooks = 0, minor_count = 0
        cdef int x, y, piece

        for x in range(8):
            for y in range(8):
                piece = abs(self._board_view[x, y])
                if piece == PAWN:
                    count_pawns += 1
                elif piece == QUEEN:
                    count_queens += 1
                elif piece == ROOK:
                    count_rooks += 1

        if count_pawns == 0 and count_queens == 0 and count_rooks == 0:
            for x in range(8):
                for y in range(8):
                    piece = abs(self._board_view[x, y])
                    if piece in (BISHOP, KNIGHT):
                        minor_count += 1
            return minor_count <= 1

        return False

    cpdef void push(self, Move move):
        self.event.append(move)
        self.push_uci(move.__str__())

    cpdef Move pop(self):
        if not self.event:
            raise IndexError("No moves to pop")

        cdef object last_event = self.event.pop()
        cdef Move last_move = None
        if type(last_event).__name__ in "Type[Move]":
            last_move = self._retract_move(last_event)
        else:
            last_move = self._retract_move(self.event.pop())
            self._board_view[last_move.to_x, last_move.to_y] = last_event
        return last_move

    cdef Move _retract_move(self, Move move):
        cdef int moving_piece = self._board_view[move.to_x, move.to_y]

        # Revert move
        self._board_view[move.from_x, move.from_y] = moving_piece
        self._board_view[move.to_x, move.to_y] = 0

        # Handle castling
        if abs(moving_piece) == KING and abs(move.from_y - move.to_y) == 2:
            if move.to_y > move.from_y:  # Kingside
                self._board_view[move.from_x, 7] = self._board_view[move.from_x, 5]
                self._board_view[move.from_x, 5] = 0
            else:  # Queenside
                self._board_view[move.from_x, 0] = self._board_view[move.from_x, 3]
                self._board_view[move.from_x, 3] = 0

        # Handle promotion
        if move.promotion:
            original_color = -self.turn
            self._board_view[move.from_x, move.from_y] = PAWN * original_color

        self.turn = -self.turn
        return move

    cpdef bint is_game_over(self):
        return self.is_checkmate() or not self.legal_moves() or self.can_claim_draw()

    cpdef int piece_at(self, tuple square):
        return self._board_view[square[0], square[1]]

    cpdef dict piece_map(self):
        cdef dict pmap = {}
        cdef int x, y, piece
        for x in range(8):
            for y in range(8):
                piece = self._board_view[x, y]
                if piece != 0:
                    pmap[(x, y)] = piece
        return pmap
