# @author: Ranuja Pinnaduwage
# Example usage of the cycompile package, showing imported and custom function usage; compares cython.compile to cycompile.
# Licensed under the Apache License, Version 2.0.

from cythonize_decorator import cycompile
import time
import numpy as np

# Function without cycompile (pure Python)
@cycompile(opt = "fast",)
def square(n):
    return n ** 3

@cycompile(opt = "fast", verbose = True)
def sum_of_squares_safe(n):
    result = 0.0
    for i in range(1, n+1):
        result += square(i)
    return np.array(result)

import cython


def square2(n):
    return n ** 3

@cython.compile
def sum_of_squares(n):
    result = 0.0
    for i in range(1, n+1):
        result += square2 (i)
    return np.array(result)

start_time = time.time()
result_python = sum_of_squares_safe(10**4)
end_time = time.time()
python_time = end_time - start_time
print(f"Python function took {python_time:.6f} seconds.")
print(result_python)
print()

start_time = time.time()
result_python = sum_of_squares(10**4)
end_time = time.time()
python_time = end_time - start_time
print(f"Python function took {python_time:.6f} seconds.")
print(result_python)