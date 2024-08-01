import numpy as np
import timeit

def fixed_size_array(max_array):
    #(PWM X, PWM Y, ID)
    stored_packets = np.zeros((5, 3))
    
    for i in range(max_array):
        pwm_x = np.random.rand()
        pwm_y = np.random.rand()
        packet_id = i + 1
        stored_packets[i] = [pwm_x, pwm_y, packet_id]
    
    return stored_packets

max_array = 5

# stored_array_fixed_size = fixed_size_array(max_array)
# print(stored_array_fixed_size)

# Benchmark
execution_time = timeit.timeit(lambda: fixed_size_array(max_array), number=1000)
avg_time = execution_time / 1000
print(f"Benchmark : {avg_time:.6f} seconds")
