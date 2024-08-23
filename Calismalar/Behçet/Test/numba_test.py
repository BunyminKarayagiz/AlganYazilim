from numba import jit

@jit(nopython=True)
def fast_function(x, y):
    return x * y + (x - y) ** 2

result = fast_function(10, 20)

print(result)