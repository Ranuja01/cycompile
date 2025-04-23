# @author: Ranuja Pinnaduwage
# File: function_call_demo.py
# Demonstrates cycompile's ability to handle imported and custom function calls.
# Licensed under the Apache License, Version 2.0.

from cycompile import cycompile
import numpy as np

# Helper function used by the compiled function
@cycompile(opt="fast")
def cube(n):
    return n ** 3

# Main function using the helper, compiled with cycompile
@cycompile(opt="fast", verbose=True)
def sum_of_cubes(n):
    result = 0.0
    for i in range(1, n + 1):
        result += cube(i)
    return np.array(result)

# Demonstration
print(sum_of_cubes(10**4))
