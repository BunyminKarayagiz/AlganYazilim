
import argparse
import ipConfig
import json
import numpy as np
import path

import time
import threading
import Client_Tcp,Client_Udp


class Iha():
    def __init__(self,host_ip) -> None:

        # TCP PWM Configurations
        self.TCP_pwm=Client_Tcp.Client(host_ip,9001)
        self.TCP_pwm.connect_to_server()
        print('Connected to TCP_pwm server...')

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

    def recv_pwm(self):
        while True:
            pwm_verileri=self.TCP_pwm.client_recv_message()

    def close_sockets(self):

        self.TCP_pwm.close()

if __name__ == '__main__':

    iha_obj = Iha(ipConfig.wlan_ip())
    iha_path = iha_obj.IHA_MissionPlanner_Connect(5762)



    print("2 Sn bekleniyor...")
    time.sleep(2) #Tüm Bağlantıların Yerine Oturması için 2 sn bekleniyor

    # Start PWM thread
    pwm_thread = threading.Thread(target=iha_obj.recv_pwm)
    pwm_thread.start()
    
    # Clean up
    iha_obj.close_sockets()

    
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