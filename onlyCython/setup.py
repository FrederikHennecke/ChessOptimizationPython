from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

extensions = [
    Extension("chess", ["chess.pyx"],
              include_dirs=[np.get_include()],
              extra_compile_args=["-O3"]),
    Extension("movegeneration", ["movegeneration.pyx"],
              include_dirs=[np.get_include()],
              extra_compile_args=["-O3"]),
    Extension("evaluate", ["evaluate.pyx"],
              include_dirs=[np.get_include()],
              extra_compile_args=["-O3"])
]

setup(
    name="chess_engine",
    ext_modules=cythonize(extensions),
)