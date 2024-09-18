from Modules import path_drone
import argparse
import time

class Iha():
    def __init__(self):
        self.TUYGUN = self.PIXHAWK_connect()
        
        self.roll_pwm_max=1900
        self.roll_pwm_min=1100
        self.roll_physical_max = 90
        self.roll_physical_min = -90

        self.pitch_pwm_max = 1900
        self.pitch_pwm_min = 1100
        
        self.stall_speed = 14
        self.max_pitch = 30
        self.max_roll  = 30
        self.desired_altitude= 100 # metre
        self.critical_altitude= 10 # metre
        self.critical_stall_diff = 2 # metre/sn
        self.roll_limit=45.0# roll deg
        self.pitch_limit=15.0 # pitch deg

        self.roll_trim=1500 #roll trim
        self.pitch_trim=1500 #pitch trim
        self.throttle_trim=1500 #throttle trim
        self.throttle_min=1100

        self.altitude_warning:bool = False
        self.roll_warning:bool = False
        self.pitch_warning:bool = False
        self.stall_warning:bool = False
        
        self.aileron_roll_channel = 1 #Roll
        self.rudder_channel = 2 #Pitch
        self.throttle_channel = 3 # Throttle

        self.FAILSAFE_TAKEOVER = False
        self.YKI_CONFIRMATION_STATUS = False

        self.enemy_track_location = None
        

    def PIXHAWK_connect(self):
        MissionPlanner_OR_PIXHAWK_Connection = False  #UÇAK İÇİN VERİLEN FONKSİYON RASPBERRY_CONNECT OLACAK
        while not MissionPlanner_OR_PIXHAWK_Connection:
            try:
                iha_path = self.IHA_Raspberry_Connect()
                MissionPlanner_OR_PIXHAWK_Connection = True
            except Exception as e:
                print("M_PLANNER/PIXHAWK CONNECTION ERROR : ",e)
        return iha_path

    def IHA_Raspberry_Connect(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--connect', default='/dev/ttyACM0')
        args = parser.parse_args()
        connection_string = args.connect
        return path_drone.Plane(connection_string)

    def roll_set(self,ch_val):
        self.TUYGUN.set_rc_channel(self.aileron_roll_channel,ch_val)

    def roll_check(self):
        return self.TUYGUN.att_roll_deg

    def roll_to_pwm_conversion(self,roll):
        return round(((roll - self.roll_physical_min) * (self.roll_pwm_max - self.roll_pwm_min) / (self.roll_physical_max - self.roll_physical_min)) + self.roll_pwm_min)

    def roll_stabilize(self):
        roll=self.roll_check()
        print("ROLL:",roll)
        #while not (roll < 10 and roll > -10) :
        pwm_roll = self.roll_to_pwm_conversion(roll)
        if (roll > 5 or roll < -5) :
            if roll > 5:
                self.roll_set(ch_val = pwm_roll - 100)
            if roll < -5:
                self.roll_set(ch_val = pwm_roll + 100)
        else:
            print("ROLL STABILIZED")
            self.roll_set(ch_val=self.roll_trim)

if __name__=="__main__":
    iha_obj= Iha()

    if iha_obj.TUYGUN.get_ap_mode() != "GUIDED":
        iha_obj.TUYGUN.set_ap_mode("GUIDED")
    while True:

        if True:
            if iha_obj.TUYGUN.get_ap_mode() != "MANUAL":
                iha_obj.TUYGUN.set_ap_mode("MANUAL")
            iha_obj.roll_stabilize()
            time.sleep(0.03)


        if False:
            iha_obj.TUYGUN.set_rc_channel(rc_chan=1,value_us=1500)
            iha_obj.TUYGUN.set_rc_channel(rc_chan=2,value_us=1500)
            iha_obj.TUYGUN.set_rc_channel(rc_chan=3,value_us=1100)
            print(iha_obj.TUYGUN.get_ap_mode())
            abc = input("CHANNEL:")

            if iha_obj.TUYGUN.get_ap_mode() != "GUIDED":
                print(iha_obj.TUYGUN.get_ap_mode())
                iha_obj.TUYGUN.set_ap_mode("GUIDED")
                print(iha_obj.TUYGUN.get_ap_mode())

            if abc == "roll1":
                iha_obj.TUYGUN.set_rc_channel(rc_chan=1,value_us=1900)
                iha_obj.TUYGUN.set_rc_channel(rc_chan=2,value_us=1500)
                iha_obj.TUYGUN.set_rc_channel(rc_chan=3,value_us=1100)
            if abc == "roll2":
                iha_obj.TUYGUN.set_rc_channel(rc_chan=1,value_us=1100)
                iha_obj.TUYGUN.set_rc_channel(rc_chan=2,value_us=1500)
                iha_obj.TUYGUN.set_rc_channel(rc_chan=3,value_us=1100)

            if abc == "pitch1": #Burun aşağı
                iha_obj.TUYGUN.set_rc_channel(rc_chan=1,value_us=1500)
                iha_obj.TUYGUN.set_rc_channel(rc_chan=2,value_us=1900)
                iha_obj.TUYGUN.set_rc_channel(rc_chan=3,value_us=1100)
            if abc == "pitch2": #Burun yukarı
                iha_obj.TUYGUN.set_rc_channel(rc_chan=1,value_us=1500)
                iha_obj.TUYGUN.set_rc_channel(rc_chan=2,value_us=1100)
                iha_obj.TUYGUN.set_rc_channel(rc_chan=3,value_us=1100)

            if abc == "th1":
                iha_obj.TUYGUN.set_rc_channel(rc_chan=1,value_us=1500)
                iha_obj.TUYGUN.set_rc_channel(rc_chan=2,value_us=1500)
                iha_obj.TUYGUN.set_rc_channel(rc_chan=3,value_us=1100)
            if abc == "th2":
                iha_obj.TUYGUN.set_rc_channel(rc_chan=1,value_us=1500)
                iha_obj.TUYGUN.set_rc_channel(rc_chan=2,value_us=1500)
                iha_obj.TUYGUN.set_rc_channel(rc_chan=3,value_us=1900)

            time.sleep(0.1)