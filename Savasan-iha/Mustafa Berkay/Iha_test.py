import argparse
import json
import numpy as np
import path
    
import time , datetime
import threading
import Client_Tcp

from vincenty import vincenty
from dronekit import LocationGlobalRelative
#!      Sorunlar
#!Kamikaze dalış güvenliği         Test edilecek[KRITIK]
#!PWM ile takip                     Eksik
#!Yonelim ile takip                 Eksik
#!Logging.decorator                 .....

class Iha():
    def __init__(self,host_ip) -> None:

        # TCP Configurations
        self.TCP_yonelim=Client_Tcp.Client(host_ip,9002)
        self.TCP_pwm=Client_Tcp.Client(host_ip,9001)
        self.TCP_mod=Client_Tcp.Client(host_ip,9003)
        self.TCP_kamikaze=Client_Tcp.Client(host_ip,9004)
        self.yönelim_yapılacak_rakip=""
        self.mevcut_mod =""
        self.onceki_mod =""

        self.yönelim_release_event = threading.Event()
        self.kamikaze_release_event = threading.Event()

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

    def Mod_sunucusuna_baglan(self):
        connection=False
        while not connection:
            try:
                self.TCP_mod.connect_to_server()
                connection=True
                print("MOD SERVER: BAĞLANDI.")
            except (ConnectionError , Exception) as e:
                print("MOD SERVER: baglanırken hata: ", e)
                
    def kamikaze_sunucusuna_baglan(self):
        connection=False
        while not connection:
            try:
                self.TCP_kamikaze.connect_to_server()
                connection=True
                print("MOD SERVER: BAĞLANDI.")
            except (ConnectionError , Exception) as e:
                print("MOD SERVER: baglanırken hata: ", e)

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

    def sunuculara_baglan(self):
        self.Yonelim_sunucusuna_baglan()
        self.PWM_sunucusuna_baglan()
        self.kamikaze_sunucusuna_baglan()
        


    #KİLİTLENME FONKSİYONLARI

    def receive_pwm(self):
        while True:
            try:
                pwm_verileri=self.TCP_pwm.client_recv_message().decode()
                print("PWM VERILERI: ",pwm_verileri)
            except Exception as e:
                print("PWM SERVER: Veri çekilirken hata :",e)

    def yönelim_yap(self): #TODO FONKSİYON İKİ FARKLI MODDA BİRDEN KULLANILDIĞINDAN DÜZENLENECEK...

            while True:
                if self.mevcut_mod != "kilitlenme":
                    self.yönelim_release_event.wait()
                    self.yönelim_release_event.clear()
                    pass
                try:
                    print("YÖNELİM VERİSİ BEKLENİYOR..")
                    self.yönelim_yapılacak_rakip = json.loads(self.TCP_yonelim.client_recv_message())
                    print("YONELIM VERISI: ", self.yönelim_yapılacak_rakip)
                except Exception as e:
                    print("YONELIM SERVER: Veri çekilirken hata :", e)

    # KAMIKAZE FONKSİYONLARI

    def qr_konum_al(self):
            is_qr_available = False
            while not is_qr_available:
                try:
                    print("QR-KONUM BEKLENİYOR..")
                    self.yönelim_yapılacak_rakip = json.loads(self.TCP_yonelim.client_recv_message())
                    print("RAKİP:",self.yönelim_yapılacak_rakip)
                    self.yönelim_yapılacak_rakip=json.loads(self.yönelim_yapılacak_rakip)
                    if self.yönelim_yapılacak_rakip == None:
                        print("QRKONUM = None >> Reset")
                        self.TCP_yonelim.send_message_to_server(is_qr_available)
                    else:
                        print("QR-KONUM : ", self.yönelim_yapılacak_rakip)
                        is_qr_available = True
                        self.TCP_yonelim.send_message_to_server(is_qr_available)
                    
                    return is_qr_available
                
                except Exception as e:
                    print("QR-KONUM: Veri çekilirken hata :", e)
            
    def kamikaze_yönelim(self,iha_path): #! KRITIK, Dalış anında modu değişimi sorun olabilir..
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

                    
                #qr_enlem, qr_boylam = json.loads(self.yönelim_yapılacak_rakip)["qrEnlem"], json.loads(self.yönelim_yapılacak_rakip)["qrBoylam"]
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
                        kamikaze_start= datetime.datetime.now()
                        self.TCP_kamikaze.send_message_to_server(kamikaze_start)
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
            print("ERROR KAMIKAZE ->" + str(e))

if __name__ == '__main__':

    iha_obj = Iha("10.80.1.114") #UÇAK İÇİN VERİLEN İP DEĞİŞTİRİLECEK. 10.0.0.236
    iha_path = iha_obj.IHA_Raspberry_Connect() #UÇAK İÇİN VERİLEN FONKSİYON RASPBERRY_CONNECT OLACAK.

    print("2 Sn bekleniyor...")
    time.sleep(2) #Tüm Bağlantıların Yerine Oturması için 2 sn bekleniyor
    iha_obj.Mod_sunucusuna_baglan()
    iha_obj.sunuculara_baglan()
    DEBUG = input("Input 'DEBUG_LOCK' or 'DEBUG_QR' for DEBUG_MODE...\n>")

    kamikaze_thread = threading.Thread(target=iha_obj.kamikaze_yönelim, args=(iha_path,))
    pwm_thread = threading.Thread(target=iha_obj.receive_pwm)
    yonelim_thread = threading.Thread(target=iha_obj.yönelim_yap)

    kamikaze_thread.start()
    pwm_thread.start()
    yonelim_thread.start()

    time.sleep(2)

    while True:
        time.sleep(0.5)
        if (iha_path.ch6 > 1600 and iha_path.ch8 > 1600):  # High High
            iha_obj.mod = "AUTO" 
            iha_obj.TCP_mod.send_message_to_server(iha_obj.mod)
            iha_obj.onceki_mod = "AUTO"
            if iha_path.get_ap_mode()!="AUTO":
                iha_path.set_ap_mode("AUTO")
            print("SELECTED MOD : AUTO")
                
        if ((iha_path.ch6 >= 1400 and iha_path.ch6 <= 1600) and iha_path.ch8 > 1600):  # Mid High
            iha_obj.mod = "FBWA" 
            iha_obj.TCP_mod.send_message_to_server(iha_obj.mod)
            iha_obj.onceki_mod = "FBWA"
            if iha_path.get_ap_mode()!="FBWA":
                iha_path.set_ap_mode("FBWA")
            print("SELECTED MOD : FBWA")
        
        if (iha_path.ch6 < 1400 and iha_path.ch8 > 1600):  # LOW High
            iha_obj.mod = "RTL" 
            iha_obj.TCP_mod.send_message_to_server(iha_obj.mod)
            iha_obj.onceki_mod = "RTL"
            if iha_path.get_ap_mode()!="RTL":
                iha_path.set_ap_mode("RTL")
            print("SELECTED MOD : RTL")
        
            
        if (iha_path.ch6 > 1600 and iha_path.ch8 < 1400) or DEBUG=="DEBUG_QR":  # ch6: High, ch8: LOW
            iha_obj.mod = "kamikaze"
            iha_obj.TCP_mod.send_message_to_server(iha_obj.mod)
            iha_obj.kamikaze_release_event.set()
            iha_obj.onceki_mod = "kamikaze"
            print("SELECTED MOD : KAMIKAZE")

            if DEBUG == "DEBUG_QR":
                while True:
                    print("DEBUG MOD ON...\n\n")
                    time.sleep(9999)

        if (iha_path.ch6 >= 1600 and (iha_path.ch8 > 1400 and iha_path.ch8 < 1600)) or DEBUG=="DEBUG_LOCK":  # ch6: High, ch8: Mid
            iha_obj.mod = "kilitlenme"
            iha_obj.TCP_mod.send_message_to_server(iha_obj.mod)
            iha_obj.yönelim_release_event.set()
            iha_obj.onceki_mod = "kilitlenme"
            if iha_path.get_ap_mode()!="FBWA":
                iha_path.set_ap_mode("FBWA")
            print("SELECTED MOD : KILITLENME")
                        
            if DEBUG == "DEBUG_kilitlenme":
                while True:
                    print("DEBUG MOD ON...\n\n")
                    time.sleep(9999)
