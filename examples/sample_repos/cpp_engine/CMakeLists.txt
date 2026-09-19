cmake_minimum_required(VERSION 3.15)
project(HighPerformanceEngine VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(engine_app
    src/main.cpp
    src/engine.cpp
)

target_include_directories(engine_app PRIVATE src)
