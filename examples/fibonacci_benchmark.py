# @author: Ranuja Pinnaduwage
# File: fibonacci_benchmark.py
# This file compares loop-based Fibonacci performance between cycompile and cython.compile,
# and demonstrates that cython.compile does not support recursive functions or Python-style type annotations.
# Licensed under the Apache License, Version 2.0.

import time
from cycompile import cycompile
import cython

# --- Fibonacci Implementations ---

# Note cycompile works with Python-style type definition as well

# Loop fibonacci with cycompile (succesful)
@cycompile(opt="fast")
def fib_loop(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

# Recursive fibonacci with cycompile (succesful)
@cycompile(opt="fast")
def fib_recursive(n: int) -> int:
    if n <= 1:
        return n
    return fib_recursive(n - 1) + fib_recursive(n - 2)

# Attempt cython.compile for loop fibonacci with Python-style type hints (fails)
@cython.compile
def fib_loop_cython_typed(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

# Loop fibonacci with cython.compile (succesful)
@cython.compile
def fib_loop_cython_untyped(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

# Recursive function with cython.compile (fails)
@cython.compile
def fib_recursive_cython(n):
    if n <= 1:
        return n
    return fib_recursive_cython(n - 1) + fib_recursive_cython(n - 2)

# --- Timing Utility ---

def time_function(func, *args):
    start_time = time.time()
    result = func(*args)
    end_time = time.time()
    return end_time - start_time, result

# --- Tests ---

def test_fibonacci(n):
    print(f"\n→ Testing Fibonacci with n = {n}\n")

    print("[Loop Function Timing]")
    loop_time_cc, loop_result_cc = time_function(fib_loop, n)
    print(f"[cycompile] fib_loop: {loop_time_cc:.6f} sec — result: {loop_result_cc}")

    
    # Loop-based: cython.compile (with type hints)

    try:
        loop_time_cy_typed, loop_result_cy_typed = time_function(fib_loop_cython_typed, n)
        print(f"[cython]    fib_loop (with type hints): {loop_time_cy_typed:.6f} sec — result: {loop_result_cy_typed}")
    except Exception as e:
        print(f"[cython]    fib_loop (with type hints): FAILED — {type(e).__name__}: {e}")
    
    print()
    
    # Loop-based: cython.compile (no type hints)
    try:
        loop_time_cy_untyped, loop_result_cy_untyped = time_function(fib_loop_cython_untyped, n)
        print(f"[cython]    fib_loop (no type hints): {loop_time_cy_untyped:.6f} sec — result: {loop_result_cy_untyped}")
    except Exception as e:
        print(f"[cython]    fib_loop (no type hints): FAILED — {type(e).__name__}: {e}")


    print()
    print("\n[Recursive Function Timing — small n only]")
    n_small = 30

    rec_time_cc, rec_result_cc = time_function(fib_recursive, n_small)
    print(f"[cycompile] fib_recursive (n={n_small}): {rec_time_cc:.6f} sec — result: {rec_result_cc}")

    try:
        rec_time_cy, rec_result_cy = time_function(fib_recursive_cython, n_small)
        print(f"[cython]    fib_recursive (n={n_small}): {rec_time_cy:.6f} sec — result: {rec_result_cy}")
    except Exception as e:
        print(f"[cython]    fib_recursive (n={n_small}): FAILED — {type(e).__name__}: {e}")

# --- Main Execution ---

if __name__ == "__main__":
    test_fibonacci(n=30)
