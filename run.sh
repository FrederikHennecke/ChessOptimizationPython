#!/bin/bash

cd $HOME/PycharmProjects/ChessOptimizationPython/ || return

# Configuration
CONCURRENCY=16
GAMES_PER_MATCH=10
TIME_CONTROL="10+3"
OPENINGS_FILE="$HOME/repos/ChessOptimizationPython/Openings/Balsa_Special.pgn"

# Define your engines (name, python_executable, script_path, args...)
defaultEngine="Default|$HOME/.pyenv/versions/3.12.8/bin/python|$HOME/repos/ChessOptimizationPython/main.py|--name=default"

#$HOME/.pyenv/versions/3.12.8/bin/python -m nuitka main.py --follow-imports --output-dir=./nuitka3.12
#$HOME/.pyenv/versions/3.13.1_gil/bin/python -m nuitka main.py --follow-imports --output-dir=./nuitka3.13

engines=(
  "3.13|$HOME/.pyenv/versions/3.13.1-gil/bin/python|$HOME/repos/ChessOptimizationPython/main.py|--name=python3.13"
  #"Nuitka12|$HOME/repos/ChessOptimizationPython/nuitka3.12/main.bin|--name=nuitka3.12"
  #"Nuitka13|$HOME/repos/ChessOptimizationPython/nuitka3.13/main.bin|--name=nuitka3.13"
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
    -variant 5check
    $(build_engine_args "$defaultEngine")
    $(build_engine_args "$engine_spec")
    -each tc="$TIME_CONTROL"
    -concurrency "$CONCURRENCY"
    -games "$GAMES_PER_MATCH"
    -repeat -recover
    -ratinginterval 2
    -sprt elo0=0 elo1=10 alpha=0.05 beta=0.05
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