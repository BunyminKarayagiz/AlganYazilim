import time
import collections
import random as r

class circular_buffer:
    def __init__(self) -> None:
        self.buf = list()
        #self.buf = collections.deque()

    def append(self,packet,num):
        self.buf.append(packet)
    
    def get(self) -> str:
        return self.buf

def create_testlist():
    counter = 10
    false_packet=False
    fake_queue=[]
    for i in range(0,10):
        x = r.randint(30,50)
        packet = (x,x,counter)
        fake_queue.append(packet)
        counter -=1


    # #Switch 3-2 and 8-7        
    temp_2 = fake_queue[1]
    temp_3 = fake_queue[2]
    fake_queue[2]=temp_2
    fake_queue[1]=temp_3

    temp_2 = fake_queue[7]
    temp_3 = fake_queue[6]
    fake_queue[6]=temp_2
    fake_queue[7]=temp_3
    print(fake_queue)
    return fake_queue

if __name__ == "__main__":

    reorder=[]
    test_list = create_testlist()

    counter=1
    current_id = 0
    prev_id = 0
    while counter <= 8:
        a=test_list.pop()
        current_id = a[2]
        print("Current_id:",current_id,"-Prev_id:",prev_id)
        if current_id == prev_id+1:
            reorder.append(a)

            prev_id=current_id
        else:
            late_packet=a
            a=test_list.pop()
            reorder.append(a)
            reorder.append(late_packet)
            prev_id=current_id
        



        counter+=1
    print(reorder)