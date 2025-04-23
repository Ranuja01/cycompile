from cythonize_decorator import cycompile

@cycompile(opt = "fast", verbose = True)
def is_even(n):
    if n == 0:
        return True
    else:             
        return is_odd(n - 1)
    
@cycompile(opt = "safe", verbose = True)
def is_odd(n):
    if n == 0:
        return False
    else:
        return is_even(n - 1)

# Example usage
number = 5
print(f"Is {number} even? {is_even(number)}")
print(f"Is {number} odd? {is_odd(number)}")
