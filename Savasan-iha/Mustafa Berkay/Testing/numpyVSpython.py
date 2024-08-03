import numpy as np
import timeit
import random
import multiprocessing as mp
import time

def __list(data_queue,liste):
    counter = 0
    while counter < 5:
        a=data_queue.get()
        liste[a[2]%5] = a
        counter += 1
    return liste

def __numpy(data_queue,arr):
    counter = 0
    while counter < 5:
        a=data_queue.get()
        arr[a[2]%5] = a
        counter += 1
    return arr

def __tuple(data_queue,liste):
    counter = 0
    while counter < 5:
        a=data_queue.get()
        liste[a[2]%5] = a
        counter += 1
    return liste

def randomized_process_numpy(data_queue,limit):
    counter = 0
    while counter < limit:
        a=random.randint(1,100)
        b=random.randint(1,100)
        c=random.randint(1,100)
        arr = np.array([a, b, c])
        data_queue.put(arr)
        counter +=1
    print("Data_amount:",counter)
    print("Break")

def randomized_process_list(data_queue,limit):
    counter = 0
    while counter < limit:
        a=random.randint(1,100)
        b=random.randint(1,100)
        c=random.randint(1,100)
        data_queue.put([a,b,c])
        counter +=1
    print("Data_amount:",counter)
    print("Break")

def randomized_process_tuple(data_queue,limit):
    counter = 0
    while counter < limit:
        a=random.randint(1,100)
        b=random.randint(1,100)
        c=random.randint(1,100)
        data_queue.put((a,b,c))
        counter +=1
    print("Data_amount:",counter)
    print("Break")

if __name__ == "__main__":
    list_queue = mp.Queue()
    numpy_queue = mp.Queue()
    tuple_queue = mp.Queue()

    mode="both"
    python_limit= 1_000_000
    numpy_limit = 1_000_000
    tuple_limit = 1_000_000
    interval= 15

    if mode=="list" or mode=="both":
        generator = mp.Process(target=randomized_process_list,args=(list_queue,python_limit))
        generator.daemon = True
        generator.start()
        time.sleep(3)

        print("Starting benchmark for ",mode)
        liste =[[1,1,1],[2,2,2],[3,3,3],[4,4,4],[5,5,5]]
        benchmark=timeit.timeit(lambda: __list(list_queue,liste),number=(int(python_limit/5))) / (python_limit/5)
        print(f"Result({numpy_limit}):",benchmark)
        
        time.sleep(interval)
        print("Preparations for numpy...")
    
    if mode == "numpy" or mode=="both":
        generator = mp.Process(target=randomized_process_numpy,args=(numpy_queue,numpy_limit))
        generator.daemon = True
        generator.start()
        time.sleep(10)

        print("Starting benchmark for ",mode)
        arr = np.zeros((5,3))
        benchmark=timeit.timeit(lambda: __numpy(numpy_queue,arr),number=(int(numpy_limit/5)))  / (numpy_limit/5)
        print(f"Result({numpy_limit}):",benchmark)

        time.sleep(interval)
        print("Preparations for tuple...")

    if mode == "tuple" or mode=="both":
        generator = mp.Process(target=randomized_process_tuple,args=(tuple_queue,tuple_limit))
        generator.daemon = True
        generator.start()
        time.sleep(10)

        print("Starting benchmark for ",mode)
        liste =[[1,1,1],[2,2,2],[3,3,3],[4,4,4],[5,5,5]]
        benchmark=timeit.timeit(lambda: __tuple(tuple_queue,liste),number=(int(tuple_limit/5)))  / (tuple_limit/5)
        print(f"Result({tuple_limit}):",benchmark)