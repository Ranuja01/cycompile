# @author: Ranuja Pinnaduwage
# File: numeric_operations_demo.py
# Demonstrates numeric and algorithmic performance with the cycompile package.
# Includes optional comparisons with equivalent Python and Cython code for context.
# Licensed under the Apache License, Version 2.0.

import time
import numpy as np
import cython
from cycompile import cycompile

# Timing utility
def time_function_call(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return result, end_time - start_time

# Utility to run a function and report timing
def run_and_report(name, func, *args, **kwargs):
    _, elapsed = time_function_call(func, *args, **kwargs)
    print(f"{name} took {elapsed:.6f} seconds")

# -----------------------------
# Test data setup
# -----------------------------
arr = np.random.rand(1_000_000)
arr_small = np.random.rand(1_000)
A = np.random.rand(500, 500)
B = np.random.rand(500, 500)

# -----------------------------
# Element-wise square
# -----------------------------
print("\n--- Element-wise Square ---")

@cython.compile
def elementwise_square_cython(arr):
    return np.array([x**2 for x in arr])

@cycompile(opt="fast")
def elementwise_square_optimized(arr: np.ndarray) -> np.ndarray:
    return np.array([x**2 for x in arr])

run_and_report("elementwise_square_cython", elementwise_square_cython, arr)
run_and_report("elementwise_square_optimized (with @cycompile)", elementwise_square_optimized, arr)

# -----------------------------
# Matrix multiplication
# -----------------------------
print("\n--- Matrix Multiplication ---")

def matrix_multiplication(A, B):
    return np.dot(A, B)

@cython.compile
def matrix_multiplication_cython(A, B):
    return np.dot(A, B)

@cycompile(opt="fast")
def matrix_multiplication_optimized(A, B):
    return np.dot(A, B)

run_and_report("matrix_multiplication_cython", matrix_multiplication_cython, A, B)
run_and_report("matrix_multiplication_optimized (with @cycompile)", matrix_multiplication_optimized, A, B)
run_and_report("matrix_multiplication (pure Python)", matrix_multiplication, A, B)

# -----------------------------
# Sum elements
# -----------------------------
print("\n--- Sum Elements ---")

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

@cycompile(opt="fast")
def sum_elements_optimized(arr):
    total = 0.0
    for x in arr:
        total += x
    return total

run_and_report("sum_elements_cython", sum_elements_cython, arr)
run_and_report("sum_elements_optimized (with @cycompile)", sum_elements_optimized, arr)
run_and_report("sum_elements (pure Python)", sum_elements, arr)

# -----------------------------
# Bubble sort
# -----------------------------
print("\n--- Sorting (Bubble Sort) ---")

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

@cycompile(opt="fast")
def bubble_sort_optimized(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

run_and_report("bubble_sort_cython", bubble_sort_cython, arr_small.copy())
run_and_report("bubble_sort_optimized (with @cycompile)", bubble_sort_optimized, arr_small.copy())
run_and_report("bubble_sort (pure Python)", bubble_sort, arr_small.copy())

# -----------------------------
# Euler method for ODE
# -----------------------------
print("\n--- Euler Method (ODE Solver) ---")

def f(t, y):
    return -y + t

def euler_method(f, y0, t0, t_end, dt):
    t = np.arange(t0, t_end, dt)
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(1, len(t)):
        y[i] = y[i-1] + dt * f(t[i-1], y[i-1])
    return y

@cython.compile
def euler_method_cython(f, y0, t0, t_end, dt):
    t = np.arange(t0, t_end, dt)
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(1, len(t)):
        y[i] = y[i-1] + dt * f(t[i-1], y[i-1])
    return y

@cycompile(opt="fast")
def euler_method_optimized(f, y0, t0, t_end, dt):
    t = np.arange(t0, t_end, dt)
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(1, len(t)):
        y[i] = y[i-1] + dt * f(t[i-1], y[i-1])
    return y

y0 = 1
t0 = 0
t_end = 10
dt = 0.1

run_and_report("euler_method_cython", euler_method_cython, f, y0, t0, t_end, dt)
run_and_report("euler_method_optimized (with @cycompile)", euler_method_optimized, f, y0, t0, t_end, dt)
run_and_report("euler_method (pure Python)", euler_method, f, y0, t0, t_end, dt)