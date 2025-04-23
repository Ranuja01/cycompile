
from __main__ import is_even

def is_odd(n):
    if n == 0:
        return False
    else:
        return is_even(n - 1)