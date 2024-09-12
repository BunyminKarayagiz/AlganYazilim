import argparse
import json
import numpy as np
from Modules import path_drone
import pickle

import time , datetime
import threading
from Modules import Client_Tcp

from vincenty import vincenty
from dronekit import LocationGlobalRelative

#!      Sorunlar
#!Kamikaze dalış güvenliği         Test edilecek[KRITIK]
#!PWM ile takip                     Eksik
#!Yonelim ile takip                 Eksik

class client_manager:
    def __init__(self,yazilim_ip,yonelim_ip) -> None:
       
        # TCP Configurations {muhtemel host_ip -> 10.0.0.236(YazılımPC)}
        self.TCP_PWM=Client_Tcp.Client(HOST=yazilim_ip,PORT=8001,name="KALMAN-PWM")
        self.TCP_MOD=Client_Tcp.Client(HOST=yazilim_ip,PORT=8002,name="MODE")
        self.TCP_KAMIKAZE=Client_Tcp.Client(HOST=yazilim_ip,PORT=8003,name="KAMIKAZE")
        self.TCP_CONFIRMATION=Client_Tcp.Client(HOST=yazilim_ip,PORT=8004,name="CONFIRMATION")

        self.TCP_TRACK=Client_Tcp.Client(HOST=yonelim_ip,PORT=9011,name="TRACK")

        self.PWM_SERVER_STATUS=False
        self.TRACK_SERVER_STATUS=False
        self.MODE_SERVER_STATUS=False
        self.KAMIKAZE_SERVER_STATUS=False
        self.CONFIRMATION_SERVER_STATUS=False

        self.YKI_CONFIRMATION_STATUS=False

    def CONNECT_PWM_CLIENT(self):
        connection=False
        while not connection:
            try:
                self.TCP_PWM.connect_to_server()
                connection=True
                print("PWM SERVER: BAĞLANDI.")
            except (ConnectionError , Exception) as e:
                print("PWM SERVER: baglanırken hata: ", e)
            time.sleep(1)
        self.PWM_SERVER_STATUS=connection

    def CONNECT_TRACK_CLIENT(self):
        connection=False
        while not connection:
            try:
                self.TCP_TRACK.connect_to_server()
                connection=True
                print("YONELIM SERVER: BAĞLANDI.")
            except (ConnectionError , Exception) as e:
                print("YONELIM SERVER: baglanırken hata: ", e)
            time.sleep(1)
        self.TRACK_SERVER_STATUS=connection
        
    def CONNECT_MODE_CLIENT(self):
        connection=False
        while not connection:
            try:
                self.TCP_MOD.connect_to_server()
                connection=True
                print("MOD SERVER: BAĞLANDI.")
            except (ConnectionError , Exception) as e:
                print("MOD SERVER: baglanırken hata: ", e)
            time.sleep(1)
        self.MODE_SERVER_STATUS=connection

    def CONNECT_KAMIKAZE_CLIENT(self):
        connection=False
        while not connection:
            try:
                self.TCP_KAMIKAZE.connect_to_server()
                connection=True
                print("KAMIKAZE SERVER: BAĞLANDI.")
            except (ConnectionError , Exception) as e:
                print("KAMIKAZE SERVER: baglanırken hata: ", e)
            time.sleep(1)
        self.KAMIKAZE_SERVER_STATUS=connection

    def CONNECT_CONFIRMATION_CLIENT(self):
        connection=False
        while not connection:
            try:
                self.TCP_CONFIRMATION.connect_to_server()
                connection=True
                print("CONFIRMATION SERVER: BAĞLANDI.")
            except (ConnectionError , Exception) as e:
                print("CONFIRMATION SERVER: baglanırken hata: ", e)
            time.sleep(1)
        self.CONFIRMATION_SERVER_STATUS=connection
        
    def wait_for_confirmation(self):
        while True:
            try:
                if self.CONFIRMATION_SERVER_STATUS:
                    ONAY=self.TCP_CONFIRMATION.client_recv_message().decode()
                    print("YKI ONAY -> ",ONAY)
                    if ONAY == "ALGAN":
                        self.YKI_CONFIRMATION_STATUS = True
                        print("YKI ONAYI ALINDI..")
                    else:
                        self.YKI_CONFIRMATION_STATUS = False
                        print("YKI ONAYI REDDEDILDI..")
                else:
                    print(f"CONFIRMATION_SERVER OFFLINE...")
            except Exception as e:
                print("YKI ONAYI BEKLERKEN HATA : ",e)
                self.YKI_CONFIRMATION_STATUS = False
            time.sleep(1)
    
    def connect_to_servers(self):
        th1=threading.Thread(target=self.CONNECT_MODE_CLIENT)
        th2=threading.Thread(target=self.CONNECT_PWM_CLIENT)
        th3=threading.Thread(target=self.CONNECT_TRACK_CLIENT)
        th4=threading.Thread(target=self.CONNECT_KAMIKAZE_CLIENT)
        th5=threading.Thread(target=self.CONNECT_CONFIRMATION_CLIENT)
        
        th1.start()
        th2.start()
        th3.start()
        th4.start()
        th5.start()

        print("WAITING FOR 'MODE' OR 'CONFIRM' ....  ")
        th1.join()
        th2.join()
        th3.join()
        th4.join()
        th5.join()

class autopilot:
    def __init__(self,iha_path,client_manager):
        
        self.TUYGUN_PIXHAWK = iha_path
        self.CLIENT_MANAGER = client_manager
 
        self.current_mode = ""
        self.previous_mode= ""

        self.stall_speed = 14
        self.max_pitch = 30
        self.max_roll  = 30
        self.desired_altitude= 100

        self.aileron_roll_channel = 1
        self.left_rudder_channel = 4
        self.right_rudder_channel = 5
        self.throttle_channel = 3

        self.FAILSAFE_TAKEOVER = False
        self.YKI_CONFIRMATION_STATUS = False

        self.enemy_track_location = None
        
        #Kamikaze_parametreleri
        self.is_qr_available=False
        self.qr_location=None
        self.heading_to_qr=False
        self.kamikaze_dive_state=False
        self.kamikaze_recover_state=False
        self.kamikaze_start=None
        self.kamikaze_end=None

    def change_mod(self, mod_kodu, iha: path_drone.Plane):
        telemetri = self.get_telemetri_verisi(iha)
        print(mod_kodu)
        if mod_kodu == "FBWA":
            telemetri["iha_otonom"] = 0
        else:
            telemetri["iha_otonom"] = 1
        if iha.get_ap_mode() != str(mod_kodu):
            iha.set_ap_mode(str(mod_kodu))

    def stall_check(self):
        stall_error= self.TUYGUN_PIXHAWK.groundspeed - self.stall_speed
        return stall_error , self.TUYGUN_PIXHAWK.groundspeed

    def alt_check(self):
        return self.TUYGUN_PIXHAWK.pos_alt_rel

    def roll_check(self):
        return self.TUYGUN_PIXHAWK.att_roll_deg
    
    def pitch_check(self):
        return self.TUYGUN_PIXHAWK.att_pitch_deg

    def trigger_failsafe(self):
        pass

    def pitch_set(self):
        pass

    def roll_set(self):
        pass 
    
    def altitude_set(self):
        pass

    def kamikaze_maneuver(self):
        pass

    def track_maneuver(self):
        pass

    def lock_maneuver(self):
        pass

    def test_throttle(self):
        for throttle_val in range(1000,2000,10):
            self.TUYGUN_PIXHAWK.set_rc_channel(rc_chan=3,value_us=throttle_val)
            time.sleep(0.1)

    def test_pitch(self):
        for pitch_servo in range(1000,2000,10):
            self.TUYGUN_PIXHAWK.set_rc_channel(rc_chan=2,value_us=pitch_servo)
            time.sleep(0.1)

    def test_roll(self):
        for roll_servo in range(1000,2000,10):
            self.TUYGUN_PIXHAWK.set_rc_channel(rc_chan=1,value_us=roll_servo)
            time.sleep(0.1)

    def wait_for_pwm(self):
        while True:
            try:
                pwm_data=pickle.loads(self.CLIENT_MANAGER.TCP_PWM.client_recv_message())
                print("PWM RECEIVED : ",pwm_data)
                try:
                    if self.YKI_CONFIRMATION_STATUS == True:
                        print("")
                    
                    #     if self.TUYGUN_PIXHAWK.get_ap_mode() != "FBWA" :
                    #             print("AP MODE SET TO FBWA...")
                    #             self.TUYGUN_PIXHAWK.set_ap_mode("FBWA")

                        # if self.YKI_CONFIRMATION_STATUS == True:
                        #     self.TUYGUN_PIXHAWK.set_rc_channel(1, pwm_data[0]) #pwmX
                        #     self.TUYGUN_PIXHAWK.set_rc_channel(2, pwm_data[1]) #pwmY
                        #     self.TUYGUN_PIXHAWK.set_rc_channel(3, 1500)
                    else:
                        if self.TUYGUN_PIXHAWK.get_ap_mode() != "AUTO":
                            self.TUYGUN_PIXHAWK.set_ap_mode("AUTO")
                        print("PWM ICIN YKI ONAYI GEREKLI...")
                except Exception as e :
                    print("KONTROL(PWM) : YÖNELİRKEN HATA ->",e)
                    time.sleep(0.2)
            except Exception as e:
                print("PWM SERVER: Veri çekilirken hata :",e)
            time.sleep(2)
    def wait_for_track(self):
        while True:
            try:
                self.enemy_track_location = self.CLIENT_MANAGER.TCP_TRACK.client_recv_message()
            except Exception as e:
                print(f"YONELİM : VERİ ALIRKEN HATA -> {e}")
            time.sleep(1)
    def wait_for_qr_konum(self):
        while True:
            try:
                self.CLIENT_MANAGER.TCP_KAMIKAZE.send_message_to_server("QR-KONUM")
                self.qr_location = self.CLIENT_MANAGER.TCP_KAMIKAZE.client_recv_message()
                self.is_qr_available=True
            except Exception as e:
                print(f"KAMIKAZE : QR-KONUM ALIRKEN HATA -> {e}")
                time.sleep(3)
                self.is_qr_available=False

    def TRACK_BY_LOCATION(self): #!KONUMA BAĞLI TAKİP/YÖNELİM
        try:
            rakip_enlem,rakip_boylam = self.enemy_track_location
            if self.CLIENT_MANAGER.YKI_CONFIRMATION_STATUS == True:
                if self.TUYGUN_PIXHAWK.get_ap_mode() != "GUIDED":
                    self.TUYGUN_PIXHAWK.set_ap_mode("GUIDED")
                    
                qr_git = LocationGlobalRelative(rakip_enlem, rakip_boylam, 100)
                #iha_path.set_rc_channel(self.throttle_channel, 1500)
                self.TUYGUN_PIXHAWK.goto(qr_git)
            else:
                if self.TUYGUN_PIXHAWK.get_ap_mode() != "AUTO":
                    self.TUYGUN_PIXHAWK.set_ap_mode("AUTO")
                print("YKI_ONAYI BEKLENIYOR...")

        except Exception as e:
            print(f"TRACK : ERROR WHILE TRACKING -> {e}")
            if self.TUYGUN_PIXHAWK.get_ap_mode() != "AUTO":
                self.TUYGUN_PIXHAWK.set_ap_mode("AUTO")
            
    def KAMIKAZE(self): #!KONUM VE KAMIKAZE   KRITIK, Dalış anında modu değişimi sorun olabilir..
        print(f"is_qr_available:{self.is_qr_available} , qr_location:{self.qr_location}")
        try:
            if not self.is_qr_available:

                if self.CLIENT_MANAGER.YKI_CONFIRMATION_STATUS == True:
                    print(f"KAMIKAZE- YKI_ONAYI :{self.CLIENT_MANAGER.YKI_CONFIRMATION_STATUS}")
                    qr_enlem, qr_boylam = self.qr_location
                    qr_mesafe = vincenty([self.TUYGUN_PIXHAWK.pos_lat, self.TUYGUN_PIXHAWK.pos_lon], [qr_enlem, qr_boylam], 100)
                    print(f"Qr_distance:{qr_mesafe} -- heading_to_qr:{self.heading_to_qr} -- kamikaze_dive_state:{self.kamikaze_dive_state} -- kamikaze_recover_state:{self.kamikaze_recover_state}")

                    #! QR'a yönelim
                    if qr_mesafe > 0.15 and not self.heading_to_qr and not self.kamikaze_dive_state:  #and self.TUYGUN_PIXHAWK.pos_alt_rel > 100:
                        print('HEADING TO QR...')
                        if self.TUYGUN_PIXHAWK.get_ap_mode() != "GUIDED":
                            self.TUYGUN_PIXHAWK.set_ap_mode("GUIDED")
                        qr_git = LocationGlobalRelative(qr_enlem, qr_boylam, 150)
                        #self.TUYGUN_PIXHAWK.set_rc_channel(3, 1500)
                        self.TUYGUN_PIXHAWK.goto(qr_git)
                        self.heading_to_qr = True
                        self.kamikaze_dive_state=False
                        self.kamikaze_recover_state=False

                    #! Dalış başlangıç(dive)
                    if qr_mesafe < 0.08 and self.TUYGUN_PIXHAWK.pos_alt_rel >= 140 and self.heading_to_qr :  # 150 metre
                        if self.TUYGUN_PIXHAWK.get_ap_mode() != "FBWA":
                            self.TUYGUN_PIXHAWK.set_ap_mode("FBWA")
                            self.kamikaze_start= datetime.datetime.now()
                        self.TUYGUN_PIXHAWK.set_rc_channel(self.aileron_roll_channel, 1650)  # Channel 1 is for Roll Input,
                        self.TUYGUN_PIXHAWK.set_rc_channel(self.left_rudder_channel, 1100)  # Channel 2 is for Pitch Input, #Burun aşağı -> kanatlar yukarı
                        self.TUYGUN_PIXHAWK.set_rc_channel(self.right_rudder_channel, 1900)  # Channel 2 is for Pitch Input, #Burun aşağı -> kanatlar yukarı
                        self.TUYGUN_PIXHAWK.set_rc_channel(self.throttle_channel, 1100)  # Channel 3 is for Throttle Input,
                        self.heading_to_qr=True
                        self.kamikaze_dive_state=True
                        self.kamikaze_recover_state=False

                    elif self.TUYGUN_PIXHAWK.pos_alt_rel >= 120 and self.TUYGUN_PIXHAWK.pos_alt_rel < 140 and self.heading_to_qr and self.kamikaze_dive_state:
                        print(f"Qr_distance:{qr_mesafe} -- heading_to_qr:{self.heading_to_qr} -- kamikaze_dive_state:{self.kamikaze_dive_state} -- kamikaze_recover_state:{self.kamikaze_recover_state}")
                        self.TUYGUN_PIXHAWK.set_rc_channel(self.aileron_roll_channel, 1650)
                        self.TUYGUN_PIXHAWK.set_rc_channel(self.left_rudder_channel, 1200)  # Channel 2 is for Pitch Input,
                        self.TUYGUN_PIXHAWK.set_rc_channel(self.right_rudder_channel, 1800)  # Channel 2 is for Pitch Input,
                        self.TUYGUN_PIXHAWK.set_rc_channel(self.throttle_channel, 1600)
                        self.heading_to_qr=True
                        self.kamikaze_dive_state=True
                        self.kamikaze_recover_state=False

                    elif self.TUYGUN_PIXHAWK.pos_alt_rel >= 100 and self.TUYGUN_PIXHAWK.pos_alt_rel < 120 and self.heading_to_qr and self.kamikaze_dive_state:
                        print(f"Qr_distance:{qr_mesafe} -- heading_to_qr:{self.heading_to_qr} -- kamikaze_dive_state:{self.kamikaze_dive_state} -- kamikaze_recover_state:{self.kamikaze_recover_state}")
                        self.TUYGUN_PIXHAWK.set_rc_channel(self.aileron_roll_channel, 1650)
                        self.TUYGUN_PIXHAWK.set_rc_channel(self.left_rudder_channel, 1400)  # Channel 2 is for Pitch Input,
                        self.TUYGUN_PIXHAWK.set_rc_channel(self.right_rudder_channel, 1600)  # Channel 2 is for Pitch Input,
                        self.TUYGUN_PIXHAWK.set_rc_channel(self.throttle_channel, 1600)
                        self.heading_to_qr=True
                        self.kamikaze_dive_state=True
                        self.kamikaze_recover_state=False

                    elif self.TUYGUN_PIXHAWK.pos_alt_rel >= 80 and self.TUYGUN_PIXHAWK.pos_alt_rel < 100 and self.heading_to_qr and self.kamikaze_dive_state :
                        print(f"Qr_distance:{qr_mesafe} -- heading_to_qr:{self.heading_to_qr} -- kamikaze_dive_state:{self.kamikaze_dive_state} -- kamikaze_recover_state:{self.kamikaze_recover_state}")
                        self.TUYGUN_PIXHAWK.set_rc_channel(self.aileron_roll_channel, 1650)
                        self.TUYGUN_PIXHAWK.set_rc_channel(self.left_rudder_channel, 1500)  # Channel 2 is for Pitch Input,
                        self.TUYGUN_PIXHAWK.set_rc_channel(self.right_rudder_channel, 1500)  # Channel 2 is for Pitch Input,
                        self.TUYGUN_PIXHAWK.set_rc_channel(self.throttle_channel, 1600)
                        self.heading_to_qr=True
                        self.kamikaze_dive_state=False
                        self.kamikaze_recover_state=True

                        #!Toparlama(Recovery)
                    elif self.TUYGUN_PIXHAWK.pos_alt_rel >= 60 and self.TUYGUN_PIXHAWK.pos_alt_rel < 80 and self.heading_to_qr and self.kamikaze_recover_state:
                        self.TUYGUN_PIXHAWK.set_rc_channel(self.aileron_roll_channel, 1650)
                        self.TUYGUN_PIXHAWK.set_rc_channel(self.left_rudder_channel, 1700)  # Channel 2 is for Pitch Input,
                        self.TUYGUN_PIXHAWK.set_rc_channel(self.right_rudder_channel, 1300)  # Channel 2 is for Pitch Input,
                        self.TUYGUN_PIXHAWK.set_rc_channel(self.throttle_channel, 1600)
                        self.heading_to_qr=True
                        self.kamikaze_dive_state=False
                        self.kamikaze_recover_state=True

                    elif self.kamikaze_recover_state and self.TUYGUN_PIXHAWK.pos_alt_rel > 40 and self.heading_to_qr and self.kamikaze_recover_state:
                        print("Recovery Done")
                        if self.TUYGUN_PIXHAWK.get_ap_mode() != "AUTO":
                            self.TUYGUN_PIXHAWK.set_ap_mode("AUTO")
                        self.heading_to_qr=True
                        self.kamikaze_dive_state=False
                        self.kamikaze_recover_state=True
                
                else:
                    print("YKI_ONAYI BEKLENIYOR...")
            else:
                print(f"QR-KONUM IS NOT AVAILABLE -> {self.qr_location}")
        except Exception as e:
            print(f"ERROR KAMIKAZE -> {e}")

    def AUTOPILOT_STATE_CONTROL(self):
        while True:
            #print("AUTOPILOT STATE CONTROL")
            if (not self.FAILSAFE_TAKEOVER) and self.CLIENT_MANAGER.YKI_CONFIRMATION_STATUS:

                if self.current_mode == "AUTO":
                    print(f"SELECTED MODE : {self.current_mode}")
                    if self.TUYGUN_PIXHAWK.get_ap_mode() != "AUTO":
                        self.TUYGUN_PIXHAWK.set_ap_mode("AUTO")



                elif self.current_mode == "FBWA":
                    print(f"SELECTED MODE : {self.current_mode}")
                    if self.TUYGUN_PIXHAWK.get_ap_mode() != "FBWA":
                        self.TUYGUN_PIXHAWK.set_ap_mode("FBWA")



                elif self.current_mode == "RTL":
                    print(f"SELECTED MODE : {self.current_mode}")
                    if self.TUYGUN_PIXHAWK.get_ap_mode() != "RTL":
                        self.TUYGUN_PIXHAWK.set_ap_mode("RTL")



                elif self.current_mode == "KAMIKAZE":
                    print(f"SELECTED MODE : {self.current_mode}")
                    # if self.TUYGUN_PIXHAWK.get_ap_mode() != "FBWA":
                    #     self.TUYGUN_PIXHAWK.set_ap_mode("FBWA")
                    self.KAMIKAZE()

                elif self.current_mode == "KILITLENME":
                    print(f"SELECTED MODE : {self.current_mode}")
                    # if self.TUYGUN_PIXHAWK.get_ap_mode() != "FBWA":
                    #     self.TUYGUN_PIXHAWK.set_ap_mode("FBWA")
                    self.TRACK_BY_LOCATION()

                elif self.current_mode == "TESTING_MODE":
                    if self.TUYGUN_PIXHAWK.get_ap_mode() != "FBWA":
                        self.TUYGUN_PIXHAWK.set_ap_mode("FBWA")
                    print("TESTING_MODE...")

                    if False:
                        print("TEST_ROLL-FBWA")
                        time.sleep(1)
                        self.test_roll()

                        print("TEST_PITCH-FBWA")
                        time.sleep(1)
                        self.test_pitch()

                        print("TEST_THROTTLE-FBWA")
                        time.sleep(1)
                        self.test_throttle()
                        time.sleep(3)

                        if self.TUYGUN_PIXHAWK.get_ap_mode() != "MANUAL":
                            self.TUYGUN_PIXHAWK.set_ap_mode("MANUAL")
                        print("TEST_ROLL-MANUAL")
                        time.sleep(1)
                        self.test_roll()

                        print("TEST_PITCH-MANUAL")
                        time.sleep(1)
                        self.test_pitch()

                        print("TEST_THROTTLE-MANUAL")
                        time.sleep(1)
                        self.test_throttle()
                        time.sleep(1)



            elif (not self.FAILSAFE_TAKEOVER) and (not self.CLIENT_MANAGER.YKI_CONFIRMATION_STATUS):
                print("NEED GCS CONFIRMATION..")

                if self.current_mode == "AUTO":
                    if self.TUYGUN_PIXHAWK.get_ap_mode() != "AUTO":
                        self.TUYGUN_PIXHAWK.set_ap_mode("AUTO")

                elif self.current_mode == "FBWA":
                    if self.TUYGUN_PIXHAWK.get_ap_mode() != "FBWA":
                        self.TUYGUN_PIXHAWK.set_ap_mode("FBWA")

                elif self.current_mode == "RTL":
                    if self.TUYGUN_PIXHAWK.get_ap_mode() != "RTL":
                        self.TUYGUN_PIXHAWK.set_ap_mode("RTL")




            elif (self.FAILSAFE_TAKEOVER) and (not self.CLIENT_MANAGER.YKI_CONFIRMATION_STATUS):
                print("AUTOPILOT-FAILSAFE TRYING TO TAKE CONTROL..")
                
            elif self.FAILSAFE_TAKEOVER and self.CLIENT_MANAGER.YKI_CONFIRMATION_STATUS:
                print("AUTOPILOT-FAILSAFE TOOK OVER..")


            time.sleep(0.1)

class Iha():
    def __init__(self,yazilim_ip,yonelim_ip,connect_type="PIXHAWK"):
        self.client_manager = client_manager(yazilim_ip=yazilim_ip,yonelim_ip=yonelim_ip)
        
        if connect_type=="PIXHAWK":
            TUYGUN = self.PIXHAWK_connect()
            self.autopilot = autopilot(iha_path=TUYGUN,client_manager=self.client_manager)
        elif connect_type=="PLANNER":
            TUYGUN = self.Planner_connect()
            self.autopilot = autopilot(iha_path=TUYGUN,client_manager=self.client_manager)

    def Planner_connect(self):
        MissionPlanner_OR_PIXHAWK_Connection = False  #UÇAK İÇİN VERİLEN FONKSİYON RASPBERRY_CONNECT OLACAK
        while not MissionPlanner_OR_PIXHAWK_Connection:
            try:
                iha_path = self.IHA_MissionPlanner_Connect(tcp_port=5762) #M.planner_connct(5762)
                MissionPlanner_OR_PIXHAWK_Connection = True
            except Exception as e:
                print("M_PLANNER/PIXHAWK CONNECTION ERROR : ",e)
        return iha_path
    def PIXHAWK_connect(self):
        MissionPlanner_OR_PIXHAWK_Connection = False  #UÇAK İÇİN VERİLEN FONKSİYON RASPBERRY_CONNECT OLACAK
        while not MissionPlanner_OR_PIXHAWK_Connection:
            try:
                iha_path = self.IHA_Raspberry_Connect()
                MissionPlanner_OR_PIXHAWK_Connection = True
            except Exception as e:
                print("M_PLANNER/PIXHAWK CONNECTION ERROR : ",e)
        return iha_path

    def IHA_MissionPlanner_Connect(self, tcp_port):
        parser = argparse.ArgumentParser()
        parser.add_argument('--connect', default=f'tcp:127.0.0.1:{str(tcp_port)}')
        args = parser.parse_args()
        connection_string = args.connect
        return path_drone.Plane(connection_string)
    def IHA_Raspberry_Connect(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--connect', default='/dev/ttyACM0')
        args = parser.parse_args()
        connection_string = args.connect
        return path_drone.Plane(connection_string)

    def start_system_dataLines(self):
        th1=threading.Thread(target=self.client_manager.connect_to_servers)
        th2=threading.Thread(target=self.client_manager.wait_for_confirmation)
        th1.start()
        th2.start()

    def start_system_autopilot(self):
        th1=threading.Thread(target=self.autopilot.AUTOPILOT_STATE_CONTROL)
        th1_1=threading.Thread(target=self.autopilot.wait_for_track)
        th1_2=threading.Thread(target=self.autopilot.wait_for_pwm)
        th1_3=threading.Thread(target=self.autopilot.wait_for_qr_konum)

        th2=threading.Thread(target=self.autopilot.trigger_failsafe)
        
        th1.start()
        print("AUTOPILOT_STATE_CONTROL ... STARTED")
        th1_1.start()
        print("autopilot.wait_for_track ... STARTED")
        th1_2.start()
        print("autopilot.wait_for_pwm ... STARTED")
        th1_3.start()
        print("autopilot.wait_for_qr_konum ... STARTED")

        th2.start()
        print("autopilot.trigger_failsafe ... STARTED")

    def main_operation(self):
        print("system_dataLines STARTING...")
        self.start_system_dataLines()
        print("system_dataLines DONE...")

        print("system_Autopilot STARTING...")
        #self.start_system_autopilot()
        print("system_autopilot DONE...")

        while True:
            selected_servo_ch_6 = self.autopilot.TUYGUN_PIXHAWK.servo6 #ch6 servo6
            selected_servo_ch_8 = self.autopilot.TUYGUN_PIXHAWK.servo7 #ch8 servo7
            print("SERVO:8", selected_servo_ch_8)
            print("SERVO:6", selected_servo_ch_6)
            time.sleep(0.3)

            if (selected_servo_ch_6 > 1600 and selected_servo_ch_8 > 1600):  # ch6: High, ch8: High
                self.autopilot.current_mode = "AUTO"
                self.client_manager.TCP_MOD.send_message_to_server(self.autopilot.current_mode)
                self.autopilot.previous_mode = "AUTO"

            if ((selected_servo_ch_6 >= 1400 and selected_servo_ch_6 <= 1600) and selected_servo_ch_8 > 1600):  # ch6: Mid, ch8: High
                self.autopilot.current_mode = "FBWA"
                self.client_manager.TCP_MOD.send_message_to_server(self.autopilot.current_mode)
                self.autopilot.previous_mode = "FBWA"
                
            if (selected_servo_ch_6 < 1400 and selected_servo_ch_8 > 1600):  # ch6: LOW, ch8: High
                self.autopilot.current_mode = "RTL"
                self.client_manager.TCP_MOD.send_message_to_server(self.autopilot.current_mode)
                self.autopilot.previous_mode = "RTL"                

            if (selected_servo_ch_6 > 1600 and selected_servo_ch_8 < 1400):  # ch6: High, ch8: LOW
                self.autopilot.current_mode = "KAMIKAZE"
                self.client_manager.TCP_MOD.send_message_to_server(self.autopilot.current_mode)
                self.autopilot.previous_mode = "KAMIKAZE"

            if (selected_servo_ch_6 >= 1600 and (selected_servo_ch_8 > 1400 and selected_servo_ch_8 < 1600)):  # ch6: High, ch8: Mid
                self.autopilot.current_mode = "KILITLENME"
                self.client_manager.TCP_MOD.send_message_to_server(self.autopilot.current_mode)
                self.autopilot.previous_mode = "KILITLENME"

            # #TODO ÇOK KRİTİK SWİTCH DÜZENLEMESİ
            if (selected_servo_ch_6 < 1400 and selected_servo_ch_8 < 1400):  # ch6: Low, ch8: Low
                self.autopilot.current_mode = "TESTING_MODE"
                self.client_manager.TCP_MOD.send_message_to_server(self.autopilot.current_mode)
                self.autopilot.previous_mode = "TESTING_MODE"

if __name__ == '__main__':

    TUYGUN = Iha(
            connect_type = "PLANNER", # PLANNER / PIXHAWK
            yazilim_ip = "10.0.0.236", #Yazılım:10.0.0.236
            yonelim_ip = "10.0.0.236", #Yönelim:10.0.0.239 -Belirsiz
                )
    
    main_thread = threading.Thread(target=TUYGUN.main_operation)
    
    print("2 Sn bekleniyor...")
    time.sleep(2) #Tüm Bağlantıların Yerine Oturması için 2 sn bekleniyor
    main_thread.run()