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
        self.TCP_TRACK=Client_Tcp.Client(HOST=yonelim_ip,PORT="UNDEFINED",name="TRACK")
        self.TCP_KAMIKAZE=Client_Tcp.Client(HOST=yazilim_ip,PORT=8003,name="KAMIKAZE")
        self.TCP_CONFIRMATION=Client_Tcp.Client(HOST=yazilim_ip,PORT=8004,name="CONFIRMATION")

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
        self.MODE_SERVER_STATUS=connection

    def CONNECT_KAMIKAZE_CLIENT(self):
        connection=False
        while not connection:
            try:
                self.TCP_KAMIKAZE.connect_to_server()
                connection=True
                print("MOD SERVER: BAĞLANDI.")
            except (ConnectionError , Exception) as e:
                print("MOD SERVER: baglanırken hata: ", e)
        self.KAMIKAZE_SERVER_STATUS=connection

    def CONNECT_CONFIRMATION_CLIENT(self):
        connection=False
        while not connection:
            try:
                self.TCP_CONFIRMATION.connect_to_server()
                connection=True
                print("YKI_ONAY SERVER: BAĞLANDI.")
            except (ConnectionError , Exception) as e:
                print("YKI_ONAY SERVER: baglanırken hata: ", e)
        self.CONFIRMATION_SERVER_STATUS=connection
        
    def wait_for_confirmation(self):
        while True:
            try:
                ONAY=self.TCP_CONFIRMATION.client_recv_message().decode()
                print("YKI ONAY -> ",ONAY)
                if ONAY == "ALGAN":
                    self.YKI_CONFIRMATION_STATUS = True
                    print("YKI ONAYI ALINDI..")
                else:
                    self.YKI_CONFIRMATION_STATUS = False
                    print("YKI ONAYI REDDEDILDI..")
            except Exception as e:
                print("YKI ONAYI BEKLERKEN HATA : ",e)
                self.YKI_CONFIRMATION_STATUS = False

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

        self.FAILSAFE_TAKEOVER = False
        self.YKI_CONFIRMATION_STATUS = False

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
        pass

    def alt_check(self):
        pass

    def roll_check(self):
        pass
    
    def pitch_check(self):
        pass

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
        pass

    def test_pitch(self):
        pass

    def test_roll(self):
        for roll_servo in range(1000,2000,10):
            self.TUYGUN_PIXHAWK
            time.sleep(0.05)

    def wait_for_pwm(self):
        while True:
            try:
                pwm_data=pickle.loads(self.TCP_PWM.client_recv_message())
                print(pwm_data)
                try:
                    if self.YKI_CONFIRMATION_STATUS == True:
                        if self.TUYGUN_PIXHAWK.get_ap_mode() != "FBWA" :
                                print("AP MODE SET TO FBWA...")
                                self.TUYGUN_PIXHAWK.set_ap_mode("FBWA")

                        if self.YKI_CONFIRMATION_STATUS == True:
                            self.TUYGUN_PIXHAWK.set_rc_channel(1, pwm_data[0]) #pwmX
                            self.TUYGUN_PIXHAWK.set_rc_channel(2, pwm_data[1]) #pwmY
                            self.TUYGUN_PIXHAWK.set_rc_channel(3, 1500)
                    else:
                        if self.TUYGUN_PIXHAWK.get_ap_mode() != "AUTO":
                            self.TUYGUN_PIXHAWK.set_ap_mode("AUTO")
                        print("PWM ICIN YKI ONAYI GEREKLI...")

                except Exception as e :
                    print("KONTROL(PWM) : YÖNELİRKEN HATA ->",e)

            except Exception as e:
                print("PWM SERVER: Veri çekilirken hata :",e)

    def TRACK_BY_LOCATION(self): #!KONUMA BAĞLI TAKİP/YÖNELİM
            while True:
                if self.mevcut_mod != "kilitlenme":
                    print("KILITLENME -> BEKLEME MODU")
                    self.yönelim_release_event.wait()
                    print("KILITLENME -> AKTIF")
                    self.yönelim_release_event.clear()
                try:
                    print("YÖNELİM VERİSİ BEKLENİYOR..")
                    self.yönelim_yapılacak_rakip = self.TCP_GUIDED_TRACK.client_recv_message()
                    rakip_enlem,rakip_boylam = self.yönelim_yapılacak_rakip
                    print("YONELIM VERISI: ", self.yönelim_yapılacak_rakip)

                    try:
                        if self.YKI_CONFIRMATION_STATUS == True:
                            if iha_path.get_ap_mode() != "GUIDED":
                                iha_path.set_ap_mode("GUIDED")
                                timer = time.perf_counter()
                             
                            if time.perf_counter() - timer > 1.1:
                                qr_git = LocationGlobalRelative(rakip_enlem, rakip_boylam, 100)
                                #iha_path.set_rc_channel(3, 1500)
                                iha_path.goto(qr_git)
                                timer = time.perf_counter()
                        else:
                            if iha_path.get_ap_mode() != "AUTO":
                                iha_path.set_ap_mode("AUTO")
                            print("YKI_ONAYI BEKLENIYOR...")

                    except Exception as e:
                        print("KONTROL(Telem) : YÖNELİRKEN HATA ->",e)
                except Exception as e:
                    print("YONELIM SERVER: Veri çekilirken hata :", e)
    
    def KAMIKAZE(self): #!KONUM VE KAMIKAZE   KRITIK, Dalış anında modu değişimi sorun olabilir..
        #time.sleep(0.3)
        if self.mevcut_mod != "kamikaze" :
                    print("KAMIKAZE -> BEKLEME MODU")
                    self.kamikaze_release_event.wait()
                    print("KAMIKAZE -> AKTIF")
                    self.kamikaze_release_event.clear()
        # is_qr_available= False
        # try:
            # while not is_qr_available:
                # is_qr_available=self.qr_konum_al() #TODO Code-Blocking line..
                # print("QRKONUM ALINDI\nQRKONUM ALINDI\nQRKONUM ALINDI\nQRKONUM ALINDI\nQRKONUM ALINDI\nQRKONUM ALINDI\nQRKONUM ALINDI\n")
        # except Exception as e:
            # print("KAMIKAZE :QR-Konum gg ->",e)

        #Manuel verilen qr self.yönelim_yapılacak_rakip = {
        qr_enlem = 0
        qr_boylam = 0

        try:
            qr_gidiyor=False
            kalkista = False
            while True:
                if self.mevcut_mod != "kamikaze" :
                    print("KAMIKAZE -> BEKLEME MODU")
                    self.kamikaze_release_event.wait()
                    print("KAMIKAZE -> AKTIF")
                    self.kamikaze_release_event.clear()

                if self.YKI_CONFIRMATION_STATUS == True:
                    print("YKI_ONAYI : ",self.YKI_CONFIRMATION_STATUS)
                    qr_enlem, qr_boylam = json.loads(self.yönelim_yapılacak_rakip)["qrEnlem"], json.loads(self.yönelim_yapılacak_rakip)["qrBoylam"]
                    qr_mesafe = vincenty([self.TUYGUN_PIXHAWK.pos_lat, self.TUYGUN_PIXHAWK.pos_lon], [qr_enlem, qr_boylam], 100)
                    print("QR MESAFE", qr_mesafe)
                    if not qr_gidiyor and not kalkista and qr_mesafe > 0.15:  # and iha.pos_alt_rel > 100:
                        print('qr_gidiyor')
                        if self.TUYGUN_PIXHAWK.get_ap_mode() != "GUIDED":
                            self.TUYGUN_PIXHAWK.set_ap_mode("GUIDED")
                        qr_git = LocationGlobalRelative(qr_enlem, qr_boylam, 100)
                        self.TUYGUN_PIXHAWK.set_rc_channel(3, 1500)
                        self.TUYGUN_PIXHAWK.goto(qr_git)
                        qr_gidiyor = True
                    if qr_mesafe < 0.08 and qr_gidiyor:  # 150 metre
                        if self.TUYGUN_PIXHAWK.get_ap_mode() != "FBWA":
                            self.TUYGUN_PIXHAWK.set_ap_mode("FBWA")
                            kamikaze_start= datetime.datetime.now()
                            self.TCP_kamikaze.send_message_to_server(kamikaze_start)
                        self.TUYGUN_PIXHAWK.set_rc_channel(1, 1500)  # Channel 1 is for Roll Input,
                        self.TUYGUN_PIXHAWK.set_rc_channel(2, 1100)  # Channel 2 is for Pitch Input,
                        self.TUYGUN_PIXHAWK.set_rc_channel(3, 1100)  # Channel 3 is for Throttle Input,
                    if self.TUYGUN_PIXHAWK.pos_alt_rel < 60:
                        self.TUYGUN_PIXHAWK.set_rc_channel(1, 1500)
                        self.TUYGUN_PIXHAWK.set_rc_channel(2, 1900)
                        self.TUYGUN_PIXHAWK.set_rc_channel(3, 1600)
                        qr_gidiyor = False
                        kalkista = True
                    if kalkista and self.TUYGUN_PIXHAWK.pos_alt_rel < 80:
                        print("kalkiyor")
                        self.TUYGUN_PIXHAWK.set_rc_channel(1, 1500)
                        self.TUYGUN_PIXHAWK.set_rc_channel(2, 1900)
                        self.TUYGUN_PIXHAWK.set_rc_channel(3, 1600)
                    if kalkista and self.TUYGUN_PIXHAWK.pos_alt_rel > 30:
                        print("kalkis bitti AUTO")
                        if self.TUYGUN_PIXHAWK.get_ap_mode() != "AUTO":
                            self.TUYGUN_PIXHAWK.set_ap_mode("AUTO")
                        kalkista = False
                else:
                    print("YKI_ONAYI BEKLENIYOR...")

        except Exception as e:
            print("ERROR KAMIKAZE ->" + str(e))

    def AUTOPILOT_STATE_CONTROL(self):
        while True:
            if (not self.FAILSAFE_TAKEOVER) and self.CLIENT_MANAGER.YKI_CONFIRMATION_STATUS:

                if self.current_mode == "AUTO":
                    if self.TUYGUN_PIXHAWK.get_ap_mode() != "AUTO":
                        self.TUYGUN_PIXHAWK.set_ap_mode("AUTO")



                elif self.current_mode == "FBWA":
                    if self.TUYGUN_PIXHAWK.get_ap_mode() != "FBWA":
                        self.TUYGUN_PIXHAWK.set_ap_mode("FBWA")



                elif self.current_mode == "RTL":
                    if self.TUYGUN_PIXHAWK.get_ap_mode() != "RTL":
                        self.TUYGUN_PIXHAWK.set_ap_mode("RTL")



                elif self.current_mode == "KAMIKAZE":
                    if self.TUYGUN_PIXHAWK.get_ap_mode() != "FBWA":
                        self.TUYGUN_PIXHAWK.set_ap_mode("FBWA")



                elif self.current_mode == "KILITLENME":
                    if self.TUYGUN_PIXHAWK.get_ap_mode() != "FBWA":
                        self.TUYGUN_PIXHAWK.set_ap_mode("FBWA")




            elif (not self.FAILSAFE_TAKEOVER) and (not self.CLIENT_MANAGER.YKI_CONFIRMATION_STATUS):
                print("NEED GCS CONFIRMATION..")

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
        th1=self.client_manager.connect_to_servers()
        th2=self.client_manager.wait_for_confirmation()
        th1.start()
        th2.start()

    def start_system_autopilot(self):
        th1=self.autopilot.AUTOPILOT_STATE_CONTROL()
        th2=self.autopilot.trigger_failsafe()
        th1.start()
        th2.start()

    def main_operation(self):
        self.start_system_dataLines()
        self.start_system_autopilot()

        while True:
            selected_servo_ch_6 = self.autopilot.TUYGUN_PIXHAWK.servo6
            selected_servo_ch_8 = self.autopilot.TUYGUN_PIXHAWK.servo7
            print("SERVO:8", selected_servo_ch_8)
            print("SERVO:6", selected_servo_ch_6)
            time.sleep(0.1)

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
            # if (selected_servo_ch_6 < 1400 and selected_servo_ch_8 < 1400):  # ch6: Low, ch8: Low
            #     self.autopilot.current_mode = "UNDEFINED"
            #     self.client_manager.TCP_MOD.send_message_to_server(self.autopilot.current_mode)
            #     self.autopilot.previous_mode = "UNDEFINED"
            #     if iha_obj.autopilot.TUYGUN_PIXHAWK.get_ap_mode()!="UNDEFINED":
            #         iha_obj.autopilot.TUYGUN_PIXHAWK.set_ap_mode("UNDEFINED")
            #     print("SELECTED MOD : UNDEFINED")

if __name__ == '__main__':

    TUYGUN = Iha(
            connect_type = "PLANNER" , # PLANNER / PIXHAWK
            yazilim_ip = "10.0.0.236", #Yazılım:10.0.0.236
            yonelim_ip = "10.0.0.236", #Yönelim:10.0.0.23x -Belirsiz
                  )
    
    main_thread = threading.Thread(target=TUYGUN.main_operation)
    
    print("2 Sn bekleniyor...")
    time.sleep(2) #Tüm Bağlantıların Yerine Oturması için 2 sn bekleniyor
    main_thread.run()

