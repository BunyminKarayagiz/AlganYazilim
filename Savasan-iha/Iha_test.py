import argparse
import json
import numpy as np
from Modules import path_drone as path
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
#!Logging.decorator                 .....

class Iha():
    def __init__(self,host_ip) -> None:

        # TCP Configurations
        self.TCP_pwm=Client_Tcp.Client(host_ip,9001)
        self.TCP_Yonelim=Client_Tcp.Client(host_ip,9002)
        self.TCP_mod=Client_Tcp.Client(host_ip,9003)
        self.TCP_kamikaze=Client_Tcp.Client(host_ip,9004)
        self.TCP_YKI_ONAY=Client_Tcp.Client(host_ip,9006)
        self.TCP_kamikazeyonelim=Client_Tcp.Client(host_ip,9011)

        self.yönelim_yapılacak_rakip=""
        self.mevcut_mod =""
        self.onceki_mod =""

        self.yönelim_release_event = threading.Event()
        self.kamikaze_release_event = threading.Event()

        self.YKI_ONAYI_VERILDI = False

    def KamikazeYonelim_sunucusuna_baglan(self):
        connection=False
        while not connection:
            try:
                self.TCP_kamikazeyonelim.connect_to_server()
                connection=True
                print("KamikazeYONELIM SERVER: BAĞLANDI.")
            except (ConnectionError , Exception) as e:
                print("KamikazeYONELIM SERVER: baglanırken hata: ", e)

    def Yonelim_sunucusuna_baglan(self):
        connection=False
        while not connection:
            try:
                self.TCP_Yonelim.connect_to_server()
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

    def YKI_ONAY_sunucusuna_baglan(self):
        connection=False
        while not connection:
            try:
                self.TCP_YKI_ONAY.connect_to_server()
                connection=True
                print("YKI_ONAY SERVER: BAĞLANDI.")
            except (ConnectionError , Exception) as e:
                print("YKI_ONAY SERVER: baglanırken hata: ", e)
                
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
        self.Mod_sunucusuna_baglan()
        self.PWM_sunucusuna_baglan()
        self.kamikaze_sunucusuna_baglan()
        self.YKI_ONAY_sunucusuna_baglan()
        self.KamikazeYonelim_sunucusuna_baglan()
        self.Yonelim_sunucusuna_baglan()
        

    def Yki_confirm(self):
        while True:
            try:
                ONAY=self.TCP_YKI_ONAY.client_recv_message().decode();
                print("YKI ONAY -> ",ONAY)
                if ONAY == "ALGAN":
                    self.YKI_ONAYI_VERILDI = True
                    print("YKI ONAYI ALINDI..")
                else:
                    self.YKI_ONAYI_VERILDI = False
                    print("YKI ONAYI REDDEDILDI..")
            except Exception as e:
                print("YKI ONAYI BEKLERKEN HATA : ",e)
                self.YKI_ONAYI_VERILDI = False

    #KİLİTLENME FONKSİYONLARI
    def receive_pwm(self):
        pwm_array = np.zeros((1,3),dtype=np.uint32)
        while True:
            try:
                pwm_array=pickle.loads(self.TCP_pwm.client_recv_message())
                print(pwm_array)
                try:
                    if self.YKI_ONAYI_VERILDI == True:
                        if iha_path.get_ap_mode() != "FBWA" :
                                print("AP MODE SET TO FBWA...")
                                iha_path.set_ap_mode("FBWA")

                        if self.YKI_ONAYI_VERILDI == True:
                            iha_path.set_rc_channel(1, pwm_array[0]) #pwmX
                            iha_path.set_rc_channel(2, pwm_array[1]) #pwmY
                            iha_path.set_rc_channel(3, 1500)
                    else:
                        if iha_path.get_ap_mode() != "AUTO":
                            iha_path.set_ap_mode("AUTO")
                        print("PWM-YONELIM ICIN YKI ONAYI GEREKLI...")


                except Exception as e :
                    print("KONTROL(PWM) : YÖNELİRKEN HATA ->",e)

            except Exception as e:
                print("PWM SERVER: Veri çekilirken hata :",e)

    def yönelim_yap(self): #TODO FONKSİYON İKİ FARKLI MODDA BİRDEN KULLANILDIĞINDAN DÜZENLENECEK...
            while True:
                if self.mevcut_mod != "kilitlenme":
                    print("KILITLENME -> BEKLEME MODU")
                    self.yönelim_release_event.wait()
                    print("KILITLENME -> AKTIF")
                    self.yönelim_release_event.clear()
                try:
                    print("YÖNELİM VERİSİ BEKLENİYOR..")
                    self.yönelim_yapılacak_rakip = self.TCP_Yonelim.client_recv_message()
                    rakip_enlem,rakip_boylam = self.yönelim_yapılacak_rakip
                    print("YONELIM VERISI: ", self.yönelim_yapılacak_rakip)

                    try:
                        if self.YKI_ONAYI_VERILDI == True:
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

    # KAMIKAZE FONKSİYONLARI
    def qr_konum_al(self):
            is_qr_available = False
            while not is_qr_available:
                try:
                    print("QR-KONUM BEKLENİYOR..")
                    self.yönelim_yapılacak_rakip = json.loads(self.TCP_kamikazeyonelim.client_recv_message())
                    print("RAKİP:",self.yönelim_yapılacak_rakip)
                    self.yönelim_yapılacak_rakip=json.loads(self.yönelim_yapılacak_rakip)
                    if self.yönelim_yapılacak_rakip == None:
                        print("QRKONUM = None >> Reset")
                        self.TCP_kamikazeyonelim.send_message_to_server(is_qr_available)
                    else:
                        print("QR-KONUM : ", self.yönelim_yapılacak_rakip)
                        is_qr_available = True
                        self.TCP_kamikazeyonelim.send_message_to_server(is_qr_available)
                    
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

                if self.YKI_ONAYI_VERILDI == True:
                    print("YKI_ONAYI : ",self.YKI_ONAYI_VERILDI)
                    #qr_enlem, qr_boylam = json.loads(self.yönelim_yapılacak_rakip)["qrEnlem"], json.loads(self.yönelim_yapılacak_rakip)["qrBoylam"]
                    # qr_mesafe = vincenty([iha_path.pos_lat, iha_path.pos_lon], [qr_enlem, qr_boylam], 100)
                    # print("QR MESAFE", qr_mesafe)
                    # if not qr_gidiyor and not kalkista and qr_mesafe > 0.15:  # and iha.pos_alt_rel > 100:
                    #     print('qr_gidiyor')
                    #     if iha_path.get_ap_mode() != "GUIDED":
                    #         iha_path.set_ap_mode("GUIDED")
                    #     qr_git = LocationGlobalRelative(qr_enlem, qr_boylam, 100)
                    #     iha_path.set_rc_channel(3, 1500)
                    #     iha_path.goto(qr_git)
                    #     qr_gidiyor = True
                    # if qr_mesafe < 0.08 and qr_gidiyor:  # 150 metre
                    #     if iha_path.get_ap_mode() != "FBWA":
                    #         iha_path.set_ap_mode("FBWA")
                    #         kamikaze_start= datetime.datetime.now()
                    #         self.TCP_kamikaze.send_message_to_server(kamikaze_start)
                    #     iha_path.set_rc_channel(1, 1500)  # Channel 1 is for Roll Input,
                    #     iha_path.set_rc_channel(2, 1100)  # Channel 2 is for Pitch Input,
                    #     iha_path.set_rc_channel(3, 1100)  # Channel 3 is for Throttle Input,
                    # if iha_path.pos_alt_rel < 60:
                    #     iha_path.set_rc_channel(1, 1500)
                    #     iha_path.set_rc_channel(2, 1900)
                    #     iha_path.set_rc_channel(3, 1600)
                    #     169.254.148.157
                    #     qr_gidiyor = False
                    #     kalkista = True
                    # if kalkista and iha_path.pos_alt_rel < 80:
                    #     print("kalkiyor")
                    #     iha_path.set_rc_channel(1, 1500)
                    #     iha_path.set_rc_channel(2, 1900)
                    #     iha_path.set_rc_channel(3, 1600)
                    # if kalkista and iha_path.pos_alt_rel > 30:
                    #     print("kalkis bitti AUTO")
                    #     if iha_path.get_ap_mode() != "AUTO":
                    #         iha_path.set_ap_mode("AUTO")
                    #     kalkista = False
                else:
                    print("YKI_ONAYI BEKLENIYOR...")

        except Exception as e:
            print("ERROR KAMIKAZE ->" + str(e))

if __name__ == '__main__':

    iha_obj = Iha("10.80.1.132") #UÇAK İÇİN VERİLEN İP DEĞİŞTİRİLECEK. 10.0.0.236
    
    MissionPlanner_OR_PIXHAWK_Connection = False
    while not MissionPlanner_OR_PIXHAWK_Connection:
        try:
            iha_path = iha_obj.IHA_MissionPlanner_Connect(5762) #UÇAK İÇİN VERİLEN FONKSİYON RASPBERRY_CONNECT OLACAK.
            MissionPlanner_OR_PIXHAWK_Connection = True
        except Exception as e:
            print("M_PLANNER/PIXHAWK CONNECTION ERROR : ",e)
            time.sleep(0.2)

    print("2 Sn bekleniyor...")
    time.sleep(2) #Tüm Bağlantıların Yerine Oturması için 2 sn bekleniyor
    iha_obj.sunuculara_baglan()

    kamikaze_thread = threading.Thread(target=iha_obj.kamikaze_yönelim, args=(iha_path,))
    pwm_thread = threading.Thread(target=iha_obj.receive_pwm)
    yonelim_thread = threading.Thread(target=iha_obj.yönelim_yap)
    Yki_onay_thread = threading.Thread(target=iha_obj.Yki_confirm)

    kamikaze_thread.start()
    pwm_thread.start()
    yonelim_thread.start()
    Yki_onay_thread.start()

    time.sleep(2)

    while True:
        selected_servo_ch_6 = iha_path.servo6
        selected_servo_ch_8 = iha_path.servo7
        time.sleep(0.5)
        print("SERVO:8", selected_servo_ch_8)
        print("SERVO:6", selected_servo_ch_6)

        if (selected_servo_ch_6 > 1600 and selected_servo_ch_8 > 1600):  # High High
            iha_obj.mod = "AUTO" 
            iha_obj.TCP_mod.send_message_to_server(iha_obj.mod)
            iha_obj.onceki_mod = "AUTO"
            if iha_path.get_ap_mode()!="AUTO":
                iha_path.set_ap_mode("AUTO")
            print("SELECTED MOD : AUTO")


        if ((selected_servo_ch_6 >= 1400 and selected_servo_ch_6 <= 1600) and selected_servo_ch_8 > 1600):  # Mid High
            iha_obj.mod = "FBWA" 
            iha_obj.TCP_mod.send_message_to_server(iha_obj.mod)
            iha_obj.onceki_mod = "FBWA"
            if iha_path.get_ap_mode()!="FBWA":
                iha_path.set_ap_mode("FBWA")
            print("SELECTED MOD : FBWA")


        if (selected_servo_ch_6 < 1400 and selected_servo_ch_8 > 1600):  # LOW High
            iha_obj.mod = "RTL" 
            iha_obj.TCP_mod.send_message_to_server(iha_obj.mod)
            iha_obj.onceki_mod = "RTL"
            if iha_path.get_ap_mode()!="RTL":
                iha_path.set_ap_mode("RTL")
            print("SELECTED MOD : RTL")


        if (selected_servo_ch_6 > 1600 and selected_servo_ch_8 < 1400):  # ch6: High, ch8: LOW
            iha_obj.mod = "kamikaze"
            iha_obj.TCP_mod.send_message_to_server(iha_obj.mod)
            iha_obj.kamikaze_release_event.set()
            iha_obj.onceki_mod = "kamikaze"
            print("SELECTED MOD : KAMIKAZE")


        if (selected_servo_ch_6 >= 1600 and (selected_servo_ch_8 > 1400 and selected_servo_ch_8 < 1600)):  # ch6: High, ch8: Mid
            iha_obj.mod = "kilitlenme"
            iha_obj.TCP_mod.send_message_to_server(iha_obj.mod)
            iha_obj.yönelim_release_event.set()
            iha_obj.onceki_mod = "kilitlenme"
            if iha_path.get_ap_mode()!="FBWA":
                iha_path.set_ap_mode("FBWA")
            print("SELECTED MOD : KILITLENME")
