# @author: Ranuja Pinnaduwage
# Example usage of the cycompile package, demonstrating numeric operations; compares cython.compile to cycompile.
# Licensed under the Apache License, Version 2.0.

import time
import numpy as np
import cython
from functools import wraps

# Assuming you have your decorator cycompile
from cythonize_decorator import cycompile  # Replace with actual import

# Assuming Cython is set up
@cython.compile
def elementwise_square_cython(arr):
    return np.array([x**2 for x in arr])

# With your cycompile decorator
@cycompile(opt = "fast")
def elementwise_square_optimized(arr: np.ndarray) -> np.ndarray:
    return np.array([x**2 for x in arr])

# Timing function for comparison
def time_function_call(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return result, end_time - start_time

# Test data
arr = np.random.rand(1000000)

# Compare performance of element-wise square functions
print("Testing element-wise square:")
result, elapsed_time = time_function_call(elementwise_square_cython, arr)
print(f"elementwise_square_cython took {elapsed_time:.6f} seconds")

result, elapsed_time = time_function_call(elementwise_square_optimized, arr)
print(f"elementwise_square_optimized (with @cycompile) took {elapsed_time:.6f} seconds")


# Matrix multiplication test
print("\nTesting matrix multiplication:")

A = np.random.rand(500, 500)
B = np.random.rand(500, 500)

def matrix_multiplication(A, B):
    return np.dot(A, B)

@cython.compile
def matrix_multiplication_cython(A, B):
    return np.dot(A, B)

@cycompile(opt = "fast")
def matrix_multiplication_optimized(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    return np.dot(A, B)

# Measure time for Cython-optimized and @cycompile version
result, elapsed_time = time_function_call(matrix_multiplication_cython, A, B)
print(f"matrix_multiplication_cython took {elapsed_time:.6f} seconds")

result, elapsed_time = time_function_call(matrix_multiplication_optimized, A, B)
print(f"matrix_multiplication_optimized (with @cycompile) took {elapsed_time:.6f} seconds")

result, elapsed_time = time_function_call(matrix_multiplication, A, B)
print(f"matrix_multiplication took {elapsed_time:.6f} seconds")


# Sum elements test
print("\nTesting sum elements:")

def sum_elements(arr):
    total = 0.0
    for x in arr:
        total += x
    return total

@cython.compile
def sum_elements_cython(arr):
    total = 0.0
    for x in arr:
        total += x
    return total

@cycompile(opt = "fast")
def sum_elements_optimized(arr: np.ndarray) -> float:
    total = 0.0
    for x in arr:
        total += x
    return total

# Measure time for sum elements functions
result, elapsed_time = time_function_call(sum_elements_cython, arr)
print(f"sum_elements_cython took {elapsed_time:.6f} seconds")

result, elapsed_time = time_function_call(sum_elements_optimized, arr)
print(f"sum_elements_optimized (with @cycompile) took {elapsed_time:.6f} seconds")

result, elapsed_time = time_function_call(sum_elements, arr)
print(f"sum_elements took {elapsed_time:.6f} seconds")

# Custom sorting test
print("\nTesting sorting:")

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

@cython.compile
def bubble_sort_cython(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

@cycompile(opt = "fast")
def bubble_sort_optimized(arr: np.ndarray) -> np.ndarray:
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# Test sorting
arr_small = np.random.rand(1000)

result, elapsed_time = time_function_call(bubble_sort_cython, arr_small)
print(f"bubble_sort_cython took {elapsed_time:.6f} seconds")

result, elapsed_time = time_function_call(bubble_sort_optimized, arr_small)
print(f"bubble_sort_optimized (with @cycompile) took {elapsed_time:.6f} seconds")

result, elapsed_time = time_function_call(bubble_sort, arr_small)
print(f"bubble_sort took {elapsed_time:.6f} seconds")

# Euler method test
print("\nTesting Euler method:")

def f(t, y):
    return -y + t

@cython.compile
def euler_method_cython(f, y0, t0, t_end, dt):
    t = np.arange(t0, t_end, dt)
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(1, len(t)):
        y[i] = y[i-1] + dt * f(t[i-1], y[i-1])
    return y

@cycompile(opt = "fast")
def euler_method_optimized(f, y0, t0, t_end, dt):
    t = np.arange(t0, t_end, dt)
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(1, len(t)):
        y[i] = y[i-1] + dt * f(t[i-1], y[i-1])
    return y

# Test Euler method
y0 = 1
t0 = 0
t_end = 10
dt = 0.1

result, elapsed_time = time_function_call(euler_method_cython, f, y0, t0, t_end, dt)
print(f"euler_method_cython took {elapsed_time:.6f} seconds")

result, elapsed_time = time_function_call(euler_method_optimized, f, y0, t0, t_end, dt)
print(f"euler_method_optimized (with @cycompile) took {elapsed_time:.6f} seconds")
