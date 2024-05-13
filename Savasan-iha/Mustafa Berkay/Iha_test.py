import argparse
import json
import numpy as np
import path

import time
import threading
import Client_Tcp


class Iha():
    def __init__(self,host_ip) -> None:

        # TCP PWM Configurations
        self.TCP_yonelim= Client_Tcp.Client(host_ip,9002)
        self.TCP_pwm=Client_Tcp.Client(host_ip,9001)
        
    def Yonelim_sunucusuna_baglan(self):
        connection=False
        while not connection:
            try:
                self.TCP_yonelim.connect_to_server()
                connection=True
            except (ConnectionError , Exception) as e:
                print("YONELIM SERVER: baglanırken hatası: ", e)

    def PWM_sunucusuna_baglan(self):
        connection=False
        while not connection:
            try:
                self.TCP_pwm.connect_to_server()
                connection=True
            except (ConnectionError , Exception) as e:
                print("PWM SERVER: baglanırken hatası: ", e)

    def IHA_MissionPlanner_Connect(self, tcp_port):
        parser = argparse.ArgumentParser()
        parser.add_argument('--connect', default=f'tcp:127.0.0.1:{str(tcp_port)}')
        args = parser.parse_args()
        connection_string = args.connect
        return path.Plane(connection_string)

    def IHA_Raspberry_Connect(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--connect', default='/dev/ttyACM0')
        args = parser.parse_args()
        connection_string = args.connect
        return path.Plane(connection_string)

    def change_mod(self, mod_kodu, iha: path.Plane):
        telemetri = self.get_telemetri_verisi(iha)
        print(mod_kodu)
        if mod_kodu == "FBWA":
            telemetri["iha_otonom"] = 0
        else:
            telemetri["iha_otonom"] = 1
        if iha.get_ap_mode() != str(mod_kodu):
            iha.set_ap_mode(str(mod_kodu))

    def pwm_cek(self):
        while True:
            try:
                pwm_verileri=self.TCP_pwm.client_recv_message().decode()
                print("PWM VERILERI: ",pwm_verileri)
            except Exception as e:
                print("PWM SERVER: Veri çekilirken hata :",e)

    def yonelim_verisi_cek(self):
        while True:
            try:
                yonelim_verisi=self.TCP_yonelim.client_recv_message()
                print("YONELIM VERISI: ",yonelim_verisi)
            except Exception as e:
                print("YONELIM SERVER: Veri çekilirken hata :",e)

if __name__ == '__main__':

    iha_obj = Iha("10.0.0.236")
    iha_path = iha_obj.IHA_Raspberry_Connect()

    print("2 Sn bekleniyor...")
    time.sleep(2) #Tüm Bağlantıların Yerine Oturması için 2 sn bekleniyor

    # Start PWM thread
    iha_obj.Yonelim_sunucusuna_baglan()
    iha_obj.PWM_sunucusuna_baglan()

    pwm_thread = threading.Thread(target=iha_obj.pwm_cek)
    yonelim_thread= threading.Thread(target=iha_obj.yonelim_verisi_cek)
    
    pwm_thread.start()
    yonelim_thread.start()
    
    while True:
        try:
            if iha_path.servo6 > 1600 and iha_path.servo7 > 1600:
                iha_obj.change_mod("AUTO", iha_path)
            elif 1400 < iha_path.servo6 < 1600 and iha_path.servo7 > 1600:
                iha_obj.change_mod("RTL", iha_path)
            elif iha_path.servo6 < 1400 and iha_path.servo7 > 1600:
                iha_obj.change_mod("FBWA", iha_path)
        except Exception as e:
            print(e)