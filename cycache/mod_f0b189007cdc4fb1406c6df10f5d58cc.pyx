
from __main__ import is_odd

def is_even(n):
    if n == 0:
        return True
    else:             
        return is_odd(n - 1)