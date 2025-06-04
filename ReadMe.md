# ♟️ Chess Engine Optimization in Python

This project explores performance optimization techniques in Python using a custom-built chess engine as a benchmarking tool. The goal is to evaluate how far Python-based applications can be pushed using various modern optimization tools, including Cython, Numba, Nuitka, and even a full C++ rewrite wrapped with Cython.

See [the techincal report](https://github.com/FrederikHennecke/ChessOptimizationPython/blob/main/report.pdf) for more information about the project.

---

## 📁 Repository Structure

```
.
├── Cpp_cython/       # Chess engine rewritten in C++ with a Cython wrapper
├── default/          # Pure Python baseline implementation
├── onlyCython/       # Python engine with Cython-based optimizations
├── nuitka/           # Nuitka-compiled version of the Python engine
├── numbaEngine/      # Python engine with Numba JIT optimizations
├── install.sh        # Installation script (requires pyenv)
├── run.sh            # Benchmark runner script
```

---

## 🛠️ Requirements

Before getting started, ensure you have the following installed:

- [`pyenv`](https://github.com/pyenv/pyenv) — for managing Python versions
- `bash` (for running the scripts)
- C/C++ compiler (e.g., `gcc`, `clang`) for Cython/Nuitka/C++ builds

---

## 🚀 Setup

Run the installation script to install all required Python versions and dependencies:

```bash
./install.sh
```

This script uses `pyenv` to set up the correct Python environments and installs all needed libraries (e.g., `numpy`, `cython`, `numba`, etc.).

---

## 🧪 Running Benchmarks

To execute all engine versions and run the benchmark suite:

```bash
./run.sh
```

This will benchmark each implementation and output evaluation speed (nodes/sec) and playing strength comparisons.

---

## 📊 Implementations Compared

| Engine           | Description                                      |
|------------------|--------------------------------------------------|
| `default`        | Baseline engine using pure Python 3.10          |
| `onlyCython`     | Python engine statically compiled via Cython    |
| `numbaEngine`    | Numba-accelerated version of the Python engine  |
| `nuitka`         | Ahead-of-time compiled version via Nuitka       |
| `Cpp_cython`     | Full C++ rewrite exposed to Python using Cython |

---

## 📌 License

This project is for educational and benchmarking purposes. Feel free to fork or extend it.

---

## 🙌 Acknowledgments

Inspired by https://github.com/healeycodes/andoma


