from PIDinC import PID
import PID_ppy
import time

if __name__ == "__main__":
    # setpoint= 100
    # obj=PID(setpoint)
    # counter = 0

    # start= time.perf_counter()
    # while counter < 50:
    #     print(obj.iterate_pid(counter))
    #     counter += 1

    # print("result:",time.perf_counter()-start)

    time.sleep(1)

    setpoint= 100
    obj=PID_ppy.PID_py(setpoint)
    counter = 0

    start= time.perf_counter()
    while counter < 50:
        print(obj.iterate_pid(counter))
        counter += 1
        time.sleep(1)

    print("result:",time.perf_counter()-start)