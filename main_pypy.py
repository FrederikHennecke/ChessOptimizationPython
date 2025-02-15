import sys
import chess
import argparse
from movegeneration import next_move


def get_depth() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", default=5, help="provide an integer (default: 3)")
    args = parser.parse_args()
    return max([1, int(args.depth)])


def get_time_limit():
    parser = argparse.ArgumentParser()
    parser.add_argument("--time", default=3, help="provide an integer (default: 3s)")
    args = parser.parse_args()
    return max([1, int(args.time)])


def get_name() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="pypy", help="provide a name (default: default)")
    args = parser.parse_args()
    return args.name


class uci:
    def __init__(self):
        self.board = chess.Board()
        self.depth = get_depth()
        self.time_limit = get_time_limit()
        self.name = get_name()

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
            print("uciok")
            return

        if msg == "isready":
            print("readyok")
            return

        if msg == "ucinewgame":
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
            _move = next_move(self.depth, self.board, self.time_limit, self.name)
            print(f"bestmove {_move}")
            return


if __name__ == "__main__":
    uci()