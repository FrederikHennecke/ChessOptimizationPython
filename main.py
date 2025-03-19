import sys
import argparse
from chess_engine import Board, Move, next_move  # Cython module

parser = argparse.ArgumentParser()

def get_time_limit(args):
    return max([1, int(args.time)])

def get_name(args) -> str:
    return args.name

class uci:
    def __init__(self):
        parser.add_argument("--name", default="default", help="provide a name (default: default)")
        parser.add_argument("--time", default=1, help="provide an integer (default: 3s)")

        self.board = Board()  # Using C++ board
        self.time_limit = get_time_limit(parser.parse_args())
        self.name = get_name(parser.parse_args())
        self.check_counts = {"white": 0, "black": 0}
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
            print("id name CppEngine")
            print("id author FH")
            print("option name UCI_Variant type combo default chess var chess var 3check var 5check")
            print("uciok")
            return

        if msg == "isready":
            print("readyok")
            return

        if msg == "ucinewgame":
            self.board.reset()
            self.check_counts = {"white": 0, "black": 0}
            return

        if msg.startswith("position"):
            if len(tokens) < 2:
                return

            if tokens[1] == "startpos":
                self.board.reset()
                moves_start = 2
            elif tokens[1] == "fen":
                fen = " ".join(tokens[2:8])
                self.board.set_fen(fen)
                moves_start = 8
            else:
                return

            if len(tokens) > moves_start and tokens[moves_start] == "moves":
                for move in tokens[(moves_start + 1):]:
                    self.board.push_uci(move)

        if msg.startswith("go"):
            _move = next_move(self.board, self.time_limit, self.name, "")
            print(f"bestmove {_move.uci()}")
            return

        if msg.startswith("setoption"):
            if "UCI_Variant" in msg:
                # Handle variant logic in Python
                pass

if __name__ == "__main__":
    uci()