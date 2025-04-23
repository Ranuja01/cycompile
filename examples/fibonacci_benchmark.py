# @author: Ranuja Pinnaduwage
# Example usage of the cycompile package, comparing cython.compile to cycompile.
# Licensed under the Apache License, Version 2.0.

import time
from cythonize_decorator import cycompile
import cython

# Loop version of Fibonacci
@cycompile(opt = "fast", verbose=True)
def fib_loop(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

# Recursive version of Fibonacci
@cycompile(opt = "fast", verbose=True)
def fib_recursive(n: int) -> int:
    if n <= 1:
        return n
    return fib_recursive(n - 1) + fib_recursive(n - 2)


# Test with @cython.compile (if installed as a package)
@cython.compile
def fib_loop_cython(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

@cython.compile
def fib_recursive_cython(n):
    if n <= 1:
        return n
    return fib_recursive_cython(n - 1) + fib_recursive_cython(n - 2)

def time_function(func, *args):
    start_time = time.time()
    result = func(*args)
    end_time = time.time()
    return end_time - start_time, result

def test_fibonacci(n):
    # Test loop-based Fibonacci with @cycompile
    loop_time, loop_result = time_function(fib_loop, n)
    print(f"Loop-based Fibonacci with @cycompile took {loop_time:.10f} seconds, result: {loop_result}")

    # Test recursive Fibonacci with @cycompile
    # recursive_time, recursive_result = time_function(fib_recursive, n)
    # print(f"Recursive Fibonacci with @cycompile took {recursive_time:.6f} seconds, result: {recursive_result}")

    # Test loop-based Fibonacci with @cython.compile
    loop_time_cython, loop_result_cython = time_function(fib_loop_cython, n)
    print(f"Loop-based Fibonacci with @cython.compile took {loop_time_cython:.10f} seconds, result: {loop_result_cython}")

    # Test recursive Fibonacci with @cython.compile
    # recursive_time_cython, recursive_result_cython = time_function(fib_recursive_cython, n)
    # print(f"Recursive Fibonacci with @cython.compile took {recursive_time_cython:.6f} seconds, result: {recursive_result_cython}")

if __name__ == "__main__":
    n = 301  # Change this value to test larger numbers, e.g., 35 for more substantial testing
    test_fibonacci(n)
