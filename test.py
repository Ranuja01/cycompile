from cythonize_decorator import cycompile  # Assume you named it that way
import time
import numpy as np

# Function without cycompile (pure Python)
def sum_of_squares_python(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result

@cycompile
def sum_of_squares_cython(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result

# Time without cycompile
start_time = time.time()
result_python = sum_of_squares_python(10**7)  # Calculate for 1 million
end_time = time.time()
python_time = end_time - start_time
print(f"Python function took {python_time:.6f} seconds.")

# Time with cycompile
start_time = time.time()
result_cython = sum_of_squares_cython(10**7)  # Calculate for 1 million
end_time = time.time()
cython_time = end_time - start_time
print(f"cycompile function took {cython_time:.6f} seconds.")
