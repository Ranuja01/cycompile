# @author: Ranuja Pinnaduwage
# File: mutual_recursion_demo.py
# Demonstrates mutual recursion support with the cycompile package.
# Licensed under the Apache License, Version 2.0.

from cycompile import cycompile

# Determines if a number is even using mutual recursion
@cycompile(opt="fast", verbose=True)
def is_even(n):
    if n == 0:
        return True
    else:
        return is_odd(n - 1)

# Determines if a number is odd using mutual recursion
@cycompile(opt="fast", verbose=True)
def is_odd(n):
    if n == 0:
        return False
    else:
        return is_even(n - 1)

# --- Example usage ---
number = 5
print(f"Is {number} even? {is_even(number)}")
print(f"Is {number} odd? {is_odd(number)}")
