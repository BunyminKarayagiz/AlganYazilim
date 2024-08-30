import math

class trajectory_calculations:
    def __init__(self) -> None:
        self.precision_Val = 111320 # 1 metre için lat lon çözünürlüğü

    @staticmethod
    def simple_estimation(self,x, y, speed, roll_degree,pitch_degree,rotation_yaw):
        abs_speed= speed / self.precision_Val

        next_x = x + abs_speed * math.sin(rotation_yaw)
        next_y = y + abs_speed * math.cos(rotation_yaw)
        return next_x,next_y
    
    @staticmethod
    def advanced_estimation(self,x, y, speed, roll_degree,pitch_degree,rotation_yaw):
        pass        
    
    @staticmethod
    def high_resolution_estimation(self,x, y, speed, roll_degree,pitch_degree,rotation_yaw):
        pass