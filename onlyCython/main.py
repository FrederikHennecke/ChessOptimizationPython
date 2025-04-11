import sys
import argparse
from chess import Board, Move  # Import your Cython classes
from movegeneration import next_move  # Import your Cython next_move

parser = argparse.ArgumentParser()


def get_time_limit(args):
    return max([1, int(args.time)])


def get_name(args) -> str:
    return args.name


class UCI:
    def __init__(self):
        parser.add_argument("--name", default="default", help="provide a name (default: default)")
        parser.add_argument("--time", default=1, help="provide an integer (default: 3s)")

        self.board = Board()  # Use your custom Board class
        self.time_limit = get_time_limit(parser.parse_args())
        self.name = get_name(parser.parse_args())
        self.variant = "chess"

        while True:
            msg = input()
            self.command(msg)

    def command(self, msg: str):
        msg = msg.strip()
        tokens = msg.split(" ")
        while "" in tokens:
            tokens.remove("")

        if msg == "quit":
            sys.exit()

        if msg == "uci":
            print("id name CythonChessEngine")
            print("id author YourName")
            print("option name UCI_Variant type combo default chess var chess var 3check var 5check")
            print("uciok")
            return

        if msg == "isready":
            print("readyok")
            return

        if msg == "ucinewgame":
            self.board.reset()
            return

        if msg.startswith("position"):
            if len(tokens) < 2:
                return

            # Handle position setup
            if tokens[1] == "startpos":
                self.board.reset()
                moves_start = 2
            elif tokens[1] == "fen":
                fen = " ".join(tokens[2:8])
                self.board.set_fen(fen)
                moves_start = 8
            else:
                return

            # Apply moves
            if len(tokens) > moves_start and tokens[moves_start] == "moves":
                for move_uci in tokens[moves_start + 1:]:
                    move = Move()
                    from_x = 8 - int(move_uci[1])
                    from_y = ord(move_uci[0]) - ord('a')
                    to_x = 8 - int(move_uci[3])
                    to_y = ord(move_uci[2]) - ord('a')
                    move.from_x, move.from_y = (from_x, from_y)
                    move.to_x, move.to_y = (to_x, to_y)

                    if len(move_uci) == 5:
                        promotion = move_uci[4].lower()
                        move.promotion = {
                            'q': 5,  # QUEEN
                            'r': 4,  # ROOK
                            'b': 3,  # BISHOP
                            'n': 2  # KNIGHT
                        }.get(promotion, 0)

                    self.board.push_uci(str(move))  # Use your board's push_uci

        if msg.startswith("go"):
            # Get the best move from your engine
            best_move = next_move(self.board, self.time_limit, self.name, True)
            print()
            for i in range(8):
                for j in range(8):
                    print(self.board._board_view[i,j], end=" ")
                print()
            print(f"bestmove {best_move}")
            return

        if msg.startswith("setoption"):
            if "UCI_Variant" in msg:
                if "3check" in msg:
                    self.variant = "3check"
                elif "5check" in msg:
                    self.variant = "5check"
                elif "chess" in msg:
                    self.variant = "chess"
            return


if __name__ == "__main__":
    UCI()