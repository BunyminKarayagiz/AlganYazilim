import numpy as np
import time
import numba
from custom_decorators import perf_counter
import timeit



@numba.jit
def foo():
    pwm1 = np.array([1,1,881],dtype=np.uint32)
    pwm2 = np.array([2,2,882],dtype=np.uint32)
    pwm3 = np.array([3,3,883],dtype=np.uint32)
    pwm4 = np.array([4,4,884],dtype=np.uint32)
    pwm5 = np.array([5,5,885],dtype=np.uint32)
    pwm6 = np.array([6,6,886],dtype=np.uint32)

    final_array = np.zeros((5,3),dtype=np.uint32)

    iterable_list = [pwm1,pwm2,pwm3,pwm5,pwm4,pwm6]

    id_correction = 0
    for arrays in iterable_list:
        # if arrays[2] != id_correction:
        #     id_correction = arrays[2] + 1
        #     print("KUSURLU PWM -> Current ID:",arrays[2]," Next should be:",id_correction)

        # else:
        #     id_correction = arrays[2] + 1
        #     print("Current ID:",arrays[2]," Next should be:",id_correction)
        
        final_array[arrays[2]%5-1] = arrays
        if arrays[2]%5 == 4:
            pass
    
start = time.perf_counter()
timeit.timeit(lambda:foo(),number=1_000_000)
print(time.perf_counter()-start)