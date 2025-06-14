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
                print("YONELIM SERVER: BAĞLANDI.")
            except (ConnectionError , Exception) as e:
                print("YONELIM SERVER: baglanırken hata: ", e)

    def PWM_sunucusuna_baglan(self):
        connection=False
        while not connection:
            try:
                self.TCP_pwm.connect_to_server()
                connection=True
                print("PWM SERVER: BAĞLANDI.")
            except (ConnectionError , Exception) as e:
                print("PWM SERVER: baglanırken hata: ", e)

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
        iha_obj.PWM_sunucusuna_baglan()
        while True:
            try:
                pwm_verileri=self.TCP_pwm.client_recv_message().decode()
                print("PWM VERILERI: ",pwm_verileri)
            except Exception as e:
                print("PWM SERVER: Veri çekilirken hata :",e)

    def yönelim_yap(self):
        self.Yonelim_sunucusuna_baglan()
        while True:
            try:
                print("YÖNELİM VERİSİ BEKLENİYOR..")
                yönelim_yapılacak_rakip=json.loads(self.TCP_yonelim.client_recv_message())
                print("YONELIM VERISI: ",yönelim_yapılacak_rakip)
            except Exception as e:
                print("YONELIM SERVER: Veri çekilirken hata :",e)

            #YÖNELİM VERİSİ İLE RAKİBE YÖNELİM YAPILACAK KISIM
            """------------------------------------------------"
            Burada yönelimi gerçekleştirecek pixhawk-dronekit kodu yazılacak.  #TODO
            "-------------------------------------------------"""

if __name__ == '__main__':

    iha_obj = Iha("10.80.1.114") #TODO UÇAK İÇİN VERİLEN İP DEĞİŞTİRİLECEK. 10.0.0.236
    iha_path = iha_obj.IHA_MissionPlanner_Connect(5762) #TODO UÇAK İÇİN VERİLEN FONKSİYON RASPBERRY_CONNECT OLACAK.

    print("2 Sn bekleniyor...")
    time.sleep(2) #Tüm Bağlantıların Yerine Oturması için 2 sn bekleniyor

    pwm_thread = threading.Thread(target=iha_obj.pwm_cek)
    yonelim_thread= threading.Thread(target=iha_obj.yönelim_yap)
    
    pwm_thread.start()
    yonelim_thread.start()
    
    """ #ESKI KONTROL KODU
    while True:
        try:
            if iha_path.servo6 > 1600 and iha_path.servo7 > 1600:
                iha_obj.change_mod("AUTO", iha_path)
            elif 1400 < iha_path.servo6 < 1600 and iha_path.servo7 > 1600:
                iha_obj.change_mod("RTL", iha_path)
            elif iha_path.servo6 < 1400 and iha_path.servo7 > 1600:
                iha_obj.change_mod("FBWA", iha_path)
        except Exception as e:
            print(e) """

    if iha_path.servo6 > 1600 and iha_path.servo7 < 1400:  # ch6: High, ch8: LOW
        mod = "kamikaze"
        mesaj['iha_otonom'] = 1
        try:
            qr_enlem, qr_boylam = rakip[3]['qrEnlem'], rakip[3]['qrBoylam']
            # qr_enlem, qr_boylam = 40.2308154, 29.0076506
            qr_mesafe = vincenty([iha_path.pos_lat, iha_path.pos_lon], [qr_enlem, qr_boylam], 100)
            print("QR MESAFE", qr_mesafe)

            if not qr_gidiyor and not kalkista and qr_mesafe > 0.15:  # and iha.pos_alt_rel > 100:
                print('qr_gidiyor')

                if iha_path.get_ap_mode() != "GUIDED":
                    iha_path.set_ap_mode("GUIDED")
                qr_git = LocationGlobalRelative(qr_enlem, qr_boylam, 100)
                iha_path.set_rc_channel(3, 1500)
                iha_path.goto(qr_git)
                qr_gidiyor = True

            if qr_mesafe < 0.08 and qr_gidiyor:  # 150 metre
                if iha_path.get_ap_mode() != "FBWA":
                    iha_path.set_ap_mode("FBWA")

                iha_path.set_rc_channel(1, 1500)  # Channel 1 is for Roll Input,
                iha_path.set_rc_channel(2, 1100)  # Channel 2 is for Pitch Input,
                iha_path.set_rc_channel(3, 1100)  # Channel 3 is for Throttle Input,

            if iha_path.pos_alt_rel < 60:
                iha_path.set_rc_channel(1, 1500)
                iha_path.set_rc_channel(2, 1900)
                iha_path.set_rc_channel(3, 1600)
                # 169.254.148.157
                qr_gidiyor = False
                kalkista = True

            if kalkista and iha_path.pos_alt_rel < 80:
                print("kalkiyor")
                iha_path.set_rc_channel(1, 1500)
                iha_path.set_rc_channel(2, 1900)
                iha_path.set_rc_channel(3, 1600)

            if kalkista and iha_path.pos_alt_rel > 30:
                print("kalkis bitti AUTO")
                if iha_path.get_ap_mode() != "AUTO":
                    iha_path.set_ap_mode("AUTO")
                kalkista = False

        except Exception as e:
            print("kamikazede problem var:" + str(e))