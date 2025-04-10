#!/bin/bash

cd $HOME/repos/ChessOptimizationPython/ || return

# Configuration
CONCURRENCY=16
GAMES_PER_MATCH=100
TIME_CONTROL="10+3"
OPENINGS_FILE="$HOME/repos/ChessOptimizationPython/Openings/Balsa_Special.pgn"

# Define your engines (name, python_executable, script_path, args...)
defaultEngine="Default|$HOME/.pyenv/versions/3.10.4/bin/python|$HOME/repos/ChessOptimizationPython/default/main.py|--name=default"

# set up Nuitka
$HOME/.pyenv/versions/3.10.4/bin/python -m nuitka ./default/main.py --follow-imports --output-dir=./nuitka

# setup Cython
cd Cpp_cython || exit
$HOME/.pyenv/versions/3.10.4/bin/python setup.py build_ext --force
cp build/lib.linux-x86_64-3.10/*.so ./
cd ..

# setup Cython
cd miniCython || exit
$HOME/.pyenv/versions/3.10.4/bin/python setup.py build_ext --force
cp build/lib.linux-x86_64-3.10/*.so ./
cd ..

engines=(
  "3.12|$HOME/.pyenv/versions/3.12.8/bin/python|$HOME/repos/ChessOptimizationPython/default/main.py|--name=python3.12"
  "Nuitka|$HOME/repos/ChessOptimizationPython/nuitka/main.bin|--name=nuitka"
  "Pypy|$HOME/repos/pypy3.11-v7.3.19-linux64/bin/pypy|$HOME/repos/ChessOptimizationPython/default/main.py|--name=pypy"
  "Numba|$HOME/.pyenv/versions/3.10.4/bin/python|$HOME/repos/ChessOptimizationPython/numbaEngine/main.py|--name=numba"
  "Cpp|$HOME/.pyenv/versions/3.10.4/bin/python|$HOME/repos/ChessOptimizationPython/Cpp_cython/main.py|--name=cpp"
  "Cython|$HOME/.pyenv/versions/3.10.4/bin/python|$HOME/repos/ChessOptimizationPython/miniCython/main.py|--name=cython"
)

# Function to build engine arguments
build_engine_args() {
  local spec="$1"
  IFS='|' read -ra parts <<< "$spec"
  local name="${parts[0]}"
  local py_exec="${parts[1]}"
  local script_args=("${parts[@]:2}")

  echo -engine "name=$name" proto=uci "cmd=$py_exec" \
    $(printf "arg=%s " "${script_args[@]}")
}

# Generate all unique match combinations
for ((i=0; i<${#engines[@]}; i++)); do
  engine_spec="${engines[i]}"
  engine_name="${engine_spec%%|*}"

  echo "================================================"
  echo "Preparing match: default vs $engine_name"

  # Build the command
  cmd=(
    ~/repos/cutechess/build/cutechess-cli
    -variant 3check
    $(build_engine_args "$defaultEngine")
    $(build_engine_args "$engine_spec")
    -each tc="$TIME_CONTROL"
    -concurrency "$CONCURRENCY"
    -games "$GAMES_PER_MATCH"
    -draw movenumber=100 movecount=15 score=50
    -maxmoves 100
    -resign movecount=8 score=600
    -repeat -recover
    -ratinginterval 2
    -openings file="$OPENINGS_FILE"
  )

  # Print the command with formatting
  echo "Command to execute:"
  printf "%s \\\\\n" "${cmd[@]}" | sed 's/ $//'
  echo -e "\n"

  # Ask for confirmation (optional)
  # Execute the command
  "${cmd[@]}"
  echo -e "\nMatch completed\n"
done
