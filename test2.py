from cythonize_decorator import cycompile  # Assume you named it that way
import time
import numpy as np

# Function without cycompile (pure Python)
@cycompile()
def square(n: int) -> float:
    return n ** 2

@cycompile()
def sum_of_squares_safe(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i ** 2
    return np.array(result)

start_time = time.time()
result_python = sum_of_squares_safe(10**7)  # Calculate for 100 million
end_time = time.time()
python_time = end_time - start_time
print(f"Python function took {python_time:.6f} seconds.")