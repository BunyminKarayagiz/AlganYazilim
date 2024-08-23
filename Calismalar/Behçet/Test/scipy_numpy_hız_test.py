import numpy as np
from scipy import linalg
import time

# Matris boyutu
n = 1000

# Rastgele matrisler oluştur
A = np.random.rand(n, n)
B = np.random.rand(n, n)

# NumPy ile matris çarpımı
start_time = time.time()
C_np = np.dot(A, B)
numpy_time = time.time() - start_time

# SciPy ile matris çarpımı (SciPy, temel işlemler için NumPy kullanır)
start_time = time.time()
C_scipy = linalg.multi_dot([A, B])
scipy_time = time.time() - start_time

print(f"NumPy ile matris çarpımı süresi: {numpy_time:.6f} saniye")
print(f"SciPy ile matris çarpımı süresi: {scipy_time:.6f} saniye")
