import numpy
import timeit

def create_set():
    myset= {1,2,3}

def create_list():
    mylist = [1,2,3]

def create_tuple():
    thistuple = (1,2,3)

if __name__ == "__main__":

    test_num = 10

    benchmark = timeit.timeit(lambda:create_set(),number=test_num) / test_num
    print("SET:",benchmark)

    benchmark = timeit.timeit(lambda:create_list(),number=test_num) / test_num
    print("LIST",benchmark)

    benchmark = timeit.timeit(lambda:create_tuple(),number=test_num) / test_num
    print("TUPLE:",benchmark)

    my_set = (1,2,3)
    my_nparr= numpy.array([1,1,1])
    my_list = [my_set,my_nparr]
    print(my_list)

