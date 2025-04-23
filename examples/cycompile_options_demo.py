# @author: Ranuja Pinnaduwage
# File: cycompile_options_demo.py
# Example usage of the cycompile package, demonstrating various optimizations and configuration settings
# (such as custom compiler directives and flags) with performance comparisons between pure Python and Cython.
# Licensed under the Apache License, Version 2.0.

from cycompile import cycompile
import time
import numpy as np
import cython

# Helper function to time code execution
def time_function(func, *args):
    start_time = time.time()
    result = func(*args)
    end_time = time.time()
    return end_time - start_time, result

# Function without cycompile (pure Python)
def sum_of_squares_python(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result

# Function decorated with cycompile (safe optimization)
@cycompile()
def sum_of_squares_safe(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result

# Function decorated with cycompile (fast optimization)
@cycompile(opt="fast")
def sum_of_squares_fast(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result

# Function decorated with cycompile (overridden compiler directive)
@cycompile(
    opt="fast",
    compiler_directives={'boundscheck': True}  # override just one directive
)
def sum_of_squares_override_directive(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result

# Function decorated with cycompile (overridden compiler flags)
@cycompile(
    opt="fast",
    extra_compile_args=["-fno-fast-math"]  # override part of the default flags
)
def sum_of_squares_override_flags(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result

# Function decorated with cycompile (overridden both flags and directives)
@cycompile(
    opt="fast",
    compiler_directives={'nonecheck': True, 'boundscheck': True},
    extra_compile_args=["-fno-fast-math", "-funroll-loops"]
)
def sum_of_squares_override_both(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result

# Function decorated with cycompile (custom settings)
@cycompile(
    opt="custom",
    compiler_directives={
        'language_level': 3,
        'boundscheck': False,
        'wraparound': False,
    },
    extra_compile_args=["-O3", "-mtune=native"]
)
def sum_of_squares_custom(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result

# Function decorated with cycompile (explicitly safe)
@cycompile(opt="safe")
def sum_of_squares_explicit_safe(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result

# Create a list of functions to time (both Python and Cython versions)
functions_to_time = [
    ("sum_of_squares_safe", sum_of_squares_safe),
    ("sum_of_squares_fast", sum_of_squares_fast),
    ("sum_of_squares_override_directive", sum_of_squares_override_directive),
    ("sum_of_squares_override_flags", sum_of_squares_override_flags),
    ("sum_of_squares_override_both", sum_of_squares_override_both),
    ("sum_of_squares_custom", sum_of_squares_custom),
    ("sum_of_squares_explicit_safe", sum_of_squares_explicit_safe)
]

# --- Edge Case Testing ---
try:
    print("\n→ Testing with n = 0")
    result = sum_of_squares_safe(0)  # Edge case: n=0
    print(f"Result (n=0): {result}")
except Exception as e:
    print(f"[ERROR] sum_of_squares_safe (n=0): {e}")

try:
    print("\n→ Testing with negative n")
    result = sum_of_squares_safe(-10)  # Edge case: negative value
    print(f"Result (n=-10): {result}")
except Exception as e:
    print(f"[ERROR] sum_of_squares_safe (n=-10): {e}")

# --- Timing and Comparison ---
# Time without cycompile (pure Python)
print("\nTiming the pure Python function...")
python_time, result_python = time_function(sum_of_squares_python, 10**8)  # Calculate for 100 million
print(f"Python function took {python_time:.6f} seconds.\n")

# Time with cycompile for each decorated function
print("Timing the cycompiled functions...\n")
for name, func in functions_to_time:
    print(f"Testing {name}:")
    cython_time, result = time_function(func, 10**8)  # Calculate for 100 million
    print(f"{name} took {cython_time:.6f} seconds.\n")
