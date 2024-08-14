# Importing Libraries 
import serial 
import time 

def Communicate():
    arduino = serial.Serial(port='COM7', baudrate=115200, timeout=.1) 
    while True: 
        num = input("Enter a number: ") # Taking input from user 
        value = write_read(arduino,num) 
        print(value) # printing the value 

def write_read(arduino,x): 
    arduino.write(bytes(x, 'utf-8')) 
    time.sleep(0.05) 
    data = arduino.readline() 
    return data 


if __name__ == "__main__":
    Communicate()