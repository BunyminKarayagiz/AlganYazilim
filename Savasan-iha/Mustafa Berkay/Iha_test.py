
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

        # TCP JSON Configurations
        self.tcp_port = 9000
        self.TCP_json = Client_Tcp.Client(host_ip,self.tcp_port)
        self.TCP_json.connect_to_server()
        print('Connected to TCP server...')

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

    def get_telemetri_verisi(self, iha: path.Plane):
        self.telemetri_verisi = {
            "takim_numarasi": 1,
            "iha_enlem": float("{:.7f}".format(iha.pos_lat)),
            "iha_boylam": float("{:.7f}".format(iha.pos_lon)),
            "iha_irtifa": float("{:.2f}".format(iha.pos_alt_rel)),
            "iha_dikilme": float("{:.2f}".format(iha.att_pitch_deg)),
            "iha_yonelme": float("{:.2f}".format(iha.att_heading_deg)),
            "iha_yatis": float("{:.2f}".format(iha.att_roll_deg)),
            "iha_hiz": float("{:.2f}".format(iha.groundspeed)),
            "iha_batarya": iha.get_battery(),
            "iha_otonom": 0,
            "iha_kilitlenme": 0,
            "hedef_merkez_X": 0,
            "hedef_merkez_Y": 0,
            "hedef_genislik": 0,
            "hedef_yukseklik": 0,
            "gps_saati": {
                "saat": iha.gps_time.hour,  # datetime.datetime.now().hour,
                "dakika": iha.gps_time.minute,  # datetime.datetime.now().minute,
                "saniye": iha.gps_time.second,  # datetime.datetime.now().second,
                "milisaniye": iha.gps_time.microsecond // 1000,  # int(datetime.datetime.now().microsecond//1000)
            }
        }
        return self.telemetri_verisi 

    def change_mod(self, mod_kodu, iha: path.Plane):
        telemetri = self.get_telemetri_verisi(iha)
        print(mod_kodu)
        if mod_kodu == "FBWA":
            telemetri["iha_otonom"] = 0
        else:
            telemetri["iha_otonom"] = 1
        if iha.get_ap_mode() != str(mod_kodu):
            iha.set_ap_mode(str(mod_kodu))

    def get_n_send_json(self,seconds=1.0):
        start_time = time.time()
        while True:
            elapsed_time=time.time() - start_time
            
            raw_data = iha_obj.get_telemetri_verisi(iha_path)
            json_string_encoded = json.dumps(raw_data)

                # Json verisi gönderilir.
            if elapsed_time >=seconds:
                self.TCP_json.send_message_to_server(json_string_encoded)
                print(iha_obj.get_telemetri_verisi(iha_path))
                start_time = time.time()

    def recv_pwm(self):
        while True:
            pwm_verileri=self.TCP_pwm.client_recv_message()

    def close_sockets(self):
        self.TCP_json.close()
        self.TCP_pwm.close()

if __name__ == '__main__':

    iha_obj = Iha(ipConfig.wlan_ip())
    iha_path = iha_obj.IHA_MissionPlanner_Connect(5762)



    print("2 Sn bekleniyor...")
    time.sleep(2) #Tüm Bağlantıların Yerine Oturması için 2 sn bekleniyor

    # Start TCP thread
    json_thread = threading.Thread(target=iha_obj.get_n_send_json)
    json_thread.start()

    # Start PWM thread
    pwm_thread = threading.Thread(target=iha_obj.recv_pwm)
    pwm_thread.start()

    pwm_thread.join()
    json_thread.join()
    
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