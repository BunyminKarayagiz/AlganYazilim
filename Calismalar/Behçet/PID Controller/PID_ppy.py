import time

class PID_py:
    def __init__(self,setpoint) -> None:
        self.setpoint:int = setpoint
        self.feed:int #INPUT -> PWM

        self.error:float = 0.0
        self.error_prev:float = 0.0

        self.prev_time = time.perf_counter()
        self.delta_time:float = time.perf_counter()

        self.proportional_val:float = 0.0
        self.Integral_val:float = 0.0
        self.Derivative_val:float = 0.0

        self.const_kp:float = 1.0
        self.const_ki:float = 1.0
        self.const_kd:float = 1.0

        self.output:float

    def iterate_pid(self,feed):

        #Time and error calc
        self.error = self.setpoint - feed
        self.delta_time = time.perf_counter() - self.prev_time

        #Calculations
        self.proportional_val=(self.const_kp * self.error)
        self.Integral_val +=(self.const_ki * self.Integral_val)
        self.Derivative_val = (self.const_kd  * (self.error - self.error_prev)/self.delta_time )

        #Output
        self.output = (self.proportional_val) + (self.Integral_val) + (self.Derivative_val)

        #Ending for the next loop
        self.prev_time = time.perf_counter()
        self.error_prev = self.error
        return f"OUTPUT:{self.output} ,P:{self.proportional_val} ,I:{self.Integral_val} ,D:{self.Derivative_val}"

# if __name__ == "__main__":
#     setpoint = 100
#     pid_object = PID(setpoint=setpoint)

#     for i in range(1,50,3):
#         print(pid_object.iterate_pid(i))
#         time.sleep(1)