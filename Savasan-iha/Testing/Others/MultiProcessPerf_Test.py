import multiprocessing
import time

def worker(num):
    """Example worker function"""
    time.sleep(1)  # Simulate a time-consuming task
    return num * num

if __name__ == '__main__':
    num_processes = multiprocessing.cpu_count()  # Start with the number of CPU cores
    pool = multiprocessing.Pool(processes=num_processes)

    start= time.perf_counter()
    results = pool.map(worker, range(8))
    mid_time=time.perf_counter()
    pool.close()
    pool.join()
    final=time.perf_counter() - start
    mid=time.perf_counter() - mid_time
    print("Pool spent :",mid)
    print("Total spent : ",final)


    print(results)
