from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension("chess_engine",
              ["chess_engine.pyx", "evaluation.cpp", "chess.cpp", "movegeneration.cpp"],
              language="c++",
              extra_compile_args=["-std=c++17", "-O3"],
              include_dirs=["."])
]

setup(
    name="chess_engine",
    ext_modules=cythonize(extensions),
)