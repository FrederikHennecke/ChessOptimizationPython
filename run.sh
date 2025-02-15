#!/bin/bash

ENGINE1_SCRIPT="$HOME/PycharmProjects/ChessOptimizationPython/main.py"
TESTARGS_SCRIPT="$HOME/PycharmProjects/ChessOptimizationPython/main.py"
TESTARGS_NAME="--name=test"

~/repos/cutechess/build/cutechess-cli \
  -engine name=default proto=uci cmd="$HOME/.pyenv/versions/3.12.8/bin/python" \
    arg="$ENGINE1_SCRIPT" \
  -engine name=new proto=uci cmd="$HOME/.pyenv/versions/3.13.1_gil/bin/python" \
    arg="$TESTARGS_SCRIPT" arg="$TESTARGS_NAME" \
  -concurrency 16 -ratinginterval 2 -games 50 -repeat -each tc=10+3 -recover \
  -sprt elo0=0 elo1=10 alpha=0.05 beta=0.05 -openings file="$HOME/PycharmProjects/ChessOptimizationPython/Openings/Balsa_Special.pgn"