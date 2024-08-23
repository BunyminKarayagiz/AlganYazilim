import numpy as np
import cupy as cp 
import time

def numpy_hesaplama(size):
    a = np.random.rand(size, size)
    b= np.random.rand(size, size)

    start_time = time.time()
    result = np.add(a, b)
    end_time = time.time()

    return end_time - start_time

def cupy_hesaplama(size):
    a = cp.random.rand(size, size)
    b= cp.random.rand(size, size)

    start_time = time.time()
    result = cp.add(a, b)
    cp.cuda.Stream.null.synchronize()
    end_time = time.time()

    return end_time - start_time

if __name__ == "__main__":
    size = 2048

    numpy_time = numpy_hesaplama(size)
    print(f"Numpy işlem süresi: {numpy_time:.6f} saniye")

    cupy_time = cupy_hesaplama(size)
    print(f"CuPy işlem süresi: {cupy_time:.6f} saniye")