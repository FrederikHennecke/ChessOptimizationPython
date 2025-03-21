#!/bin/bash

pyenv install 3.10.4
pyenv install 3.12.8

# List of pip paths (add your own paths here)
pip_paths=(
  "$HOME/.pyenv/versions/3.10.4/bin/pip"
  "$HOME/.pyenv/versions/3.12.8/bin/pip"
)

# List of packages to install (add your packages here)
packages=(
  "numpy"
  "nuitka"
  "numba"
  "cython"
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

./repos/pypy3.11-v7.3.19-linux64/bin/pypy -m ensurepip
$HOME/repos/pypy3.11-v7.3.19-linux64/bin/pypy -m pip install numpy