import sys
import argparse

from chess_engine import Board, next_move, Move, debug_cpp_board

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
            _move_uci = next_move(self.board, self.time_limit, self.name, True)

            if not self.board.is_move_legal(_move_uci):
                print(f"bestmove 0000")
            else:
                print(f"bestmove {_move_uci.uci()}")
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