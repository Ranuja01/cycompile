from cythonize_decorator import cycompile
import time
import numpy as np

# Function without cycompile (pure Python)
def sum_of_squares_python(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result

@cycompile()
def sum_of_squares_safe(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result

@cycompile(opt="fast")
def sum_of_squares_fast(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result

@cycompile(
    opt="fast",
    compiler_directives={'boundscheck': True}  # override just one directive
)
def sum_of_squares_override_directive(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result

@cycompile(
    opt="fast",
    extra_compile_args=["-fno-fast-math"]  # override part of the default flags
)
def sum_of_squares_override_flags(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result

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

# Time without cycompile (pure Python)
start_time = time.time()
result_python = sum_of_squares_python(10**7)  # Calculate for 100 million
end_time = time.time()
python_time = end_time - start_time
print(f"Python function took {python_time:.6f} seconds.")

# Time with cycompile for each decorated function
for name, func in functions_to_time:
    start_time = time.time()
    result = func(10**7)  # Calculate for 100 million
    end_time = time.time()
    cython_time = end_time - start_time
    print(f"{name} took {cython_time:.6f} seconds.")
    print()
