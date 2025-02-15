#!/bin/bash

# List of pip paths (add your own paths here)
pip_paths=(
  "$HOME/.pyenv/versions/3.12.8/bin/pip"
  "$HOME/.pyenv/versions/3.13.1_gil/bin/pip"
)

# List of packages to install (add your packages here)
packages=(
  "numpy"
  "chess"
  "nuitka"
)

# Install packages for each Python version
for pip in "${pip_paths[@]}"; do
  if [[ -f "$pip" ]]; then
    echo "Installing packages using $pip"
    "$pip" install --upgrade "${packages[@]}"
    echo -e "Done\n"
  else
    echo "Pip not found: $pip"
  fi
done