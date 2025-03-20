cmake_minimum_required(VERSION 3.28)
project(Cython)

set(CMAKE_CXX_STANDARD 17)

add_executable(Cython
        chess.hpp
        chess.cpp
        evaluation.hpp
        evaluation.cpp
        movegeneration.hpp
        movegeneration.cpp
        test.cpp)
