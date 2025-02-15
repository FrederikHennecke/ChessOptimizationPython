#!/bin/bash

# Configuration
CONCURRENCY=16
GAMES_PER_MATCH=10
TIME_CONTROL="10+3"
OPENINGS_FILE="$HOME/PycharmProjects/ChessOptimizationPython/Openings/Balsa_Special.pgn"

# Define your engines (name, python_executable, script_path, args...)
engines=(
  "Default|$HOME/.pyenv/versions/3.12.8/bin/python|$HOME/PycharmProjects/ChessOptimizationPython/main.py|--name=default"
  "3.13_gil|$HOME/.pyenv/versions/3.13.1_gil/bin/python|$HOME/PycharmProjects/ChessOptimizationPython/main.py|--name=test"
  "3.13|$HOME/.pyenv/versions/3.13.1/bin/python|$HOME/PycharmProjects/ChessOptimizationPython/main.py|--name=test2"

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
  for ((j=i+1; j<${#engines[@]}; j++)); do
    engine1_spec="${engines[i]}"
    engine2_spec="${engines[j]}"
    engine1_name="${engine1_spec%%|*}"
    engine2_name="${engine2_spec%%|*}"

    echo "================================================"
    echo "Preparing match: $engine1_name vs $engine2_name"

    # Build the command
    cmd=(
      ~/repos/cutechess/build/cutechess-cli
      $(build_engine_args "$engine1_spec")
      $(build_engine_args "$engine2_spec")
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
done