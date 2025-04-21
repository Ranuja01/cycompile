def sum_of_squares_cython(n: int) -> float:
    result = 0.0
    for i in range(1, n+1):
        result += i**2
    return result