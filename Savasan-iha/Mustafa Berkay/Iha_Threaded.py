import argparse
import json
import threading
import path
import Client_Tcp
import Client_Udp

import time
import datetime


class Iha():
    def __init__(self, host):
        self.host = host
        self.Client_Tcp = Client_Tcp.Client(host)
        self.Client_Udp = Client_Udp.Client(host)
        self.Client_Tcp.connect_to_server()

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

    def send_telemetri_thread(self):
            while True:
                try:
                    telemetri_verisi = self.get_telemetri_verisi(iha)
                    self.Client_Tcp.send_message_to_server(json.dumps(telemetri_verisi))
                except Exception as e:
                    print(e)


    def change_mod(self, mod_kodu, iha: path.Plane):
        telemetri = self.get_telemetri_verisi(iha)
        print(mod_kodu)
        if mod_kodu == "FBWA":
            telemetri["iha_otonom"] = 0
        else:
            telemetri["iha_otonom"] = 1
        if iha.get_ap_mode() != str(mod_kodu):
            iha.set_ap_mode(str(mod_kodu))


    def count(self,interval,x):
        while True:
            time_1 = time.time()

            while True:
                time_2= time.time()

                if (time_2 - time_1 >= interval): 
                    print("while time : True")
                    
                    telemetri_verisi = self.get_telemetri_verisi(x)
                    self.Client_Tcp.send_message_to_server(json.dumps(telemetri_verisi))

                    break
    
    def send_video_thread(self,a):
        while True:
            try:
                a.Client_Udp.send_video()
            except Exception as e:
                print(e)

if __name__ == '__main__':
    iha_obj = Iha("192.168.56.1")

    iha = iha_obj.IHA_MissionPlanner_Connect(5762)

    print("3 Sn bekleniyor...")
    time.sleep(3) #Tüm Bağlantıların Yerine Oturması için 3 sn bekleniyor

    while True:
        try:
            if iha.servo6 > 1600 and iha.servo7 > 1600:
                iha_obj.change_mod("AUTO", iha)
            elif 1400 < iha.servo6 < 1600 and iha.servo7 > 1600:
                iha_obj.change_mod("RTL", iha)
            elif iha.servo6 < 1400 and iha.servo7 > 1600:
                iha_obj.change_mod("FBWA", iha)
        except Exception as e:
            print(e)


