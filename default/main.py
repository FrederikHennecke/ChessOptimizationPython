import sys
import argparse
import chess
from movegeneration import next_move

parser = argparse.ArgumentParser()


def get_time_limit(args):
    return max([1, int(args.time)])


def get_name(args) -> str:
    return args.name


class uci:
    def __init__(self):
        parser.add_argument("--name", default="default", help="provide a name (default: default)")
        parser.add_argument("--time", default=1, help="provide an integer (default: 3s)")

        self.board = chess.Board()
        self.time_limit = get_time_limit(parser.parse_args())
        self.name = get_name(parser.parse_args())
        self.check_counts = {"white": 0, "black": 0}  # Track checks for 3check and 5check
        self.variant = "chess"  # default variant

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
            print("id name NTHPDA")
            print("id author FH")
            print("option name UCI_Variant type combo default chess var chess var 3check var 5check")  # Add UCI_Variant option
            print("uciok")
            return

        if msg == "isready":
            print("readyok")
            return

        if msg == "ucinewgame":
            self.board.reset()
            self.check_counts = {"white": 0, "black": 0}  # Reset check counts
            return

        if msg.startswith("position"):
            if len(tokens) < 2:
                return

            # Set starting position
            if tokens[1] == "startpos":
                self.board.reset()
                moves_start = 2
            elif tokens[1] == "fen":
                fen = " ".join(tokens[2:8])
                self.board.set_fen(fen)
                moves_start = 8
            else:
                return

            if len(tokens) <= moves_start or tokens[moves_start] != "moves":
                return

            for move in tokens[(moves_start + 1):]:
                self.board.push_uci(move)

        if msg[0:2] == "go":
            old_board = self.board._board.copy()
            _move = next_move(self.board, self.time_limit, self.name)
            self.board._board = old_board
            if not self.board._is_move_legal(_move, self.board.turn):
                print(f"bestmove 0000")
            else:
                print(f"bestmove {_move}")
            return

        if msg.startswith("setoption"):
            # Handle UCI_Variant option for 3check and 5check
            if "UCI_Variant" in msg:
                if "3check" in msg:
                    self.variant = "3check"
                    print("info string 3check variant selected")
                elif "5check" in msg:
                    self.variant = "5check"
                    print("info string 5check variant selected")
                elif "chess" in msg:
                    self.variant = "chess"
                    print("info string Standard chess variant selected")
            return


if __name__ == "__main__":
    uci()