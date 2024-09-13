# import numpy as np
# from pyzbar import pyzbar
# from path import Plane
#from Modules import mavproxy2

from Modules import ana_sunucu_islemleri,hesaplamalar,YOLOv8_deploy,SimplifiedTelemetry,Server_Tcp,Client_Udp,Server_Udp
from Modules.qr_detection import QR_Detection
from Modules.Cprint import cp
from Modules.yki_arayuz import App

import multiprocessing as mp
import numpy as np

import threading,cv2,pyvirtualcam,os,json,time,datetime,av, pickle , shutil

from Modules.prediction_algorithm_try import KalmanFilter

#!      SORUNLAR
#?SUNUCU-SAATİ + FARK :                Eksik(Mevcut Durum yeterli)
#?Yonelim-PWM Değişimi :               Eksik(Çözüldü)
#?Ana_sunucuya veri gönderimi :        Kusurlu(Çözüldü)
#?Telemetri verilerinin alınması :     Kusurlu(Çözüldü)
#TODOYonelim modunda rakip seçimi:     Eksik(GÖREVLERE EKLENDİ)
#!Aşırı yönelim(pwm):                  Eksik(iptal)
#TODO Hava savunma sistemi:            Eksik(GÖREVLERE EKLENDI)
#!Pwm veri doğruluğu:                  Test edilecek
#?Telemetri gönderim sıklığı:           Kusurlu(Çözüldü)
#!Logger                                Kusurlu/Eksik(iptal)
#!Qr için timeout                       Eksik(İptal edildi)
#TODO Kalman ile rota tahmin            Eksik(görevlere eklendi)
#?Kalman array için gecikmesi           Kusurlu(Çözüldü)

#! KOD ÇALIŞTIRMA SIRASI: sunucuapi -> Yer_istasyonu_v6 -> Iha_test(PUTTY) -> Iha_haberlesme(PUTTY)

class YerIstasyonu:

    def __init__(self,yonelim_ip,ana_sunucu_ip,ana_sunucu_port,mavlink_ip,mavlink_port,takimNo,event_map,SHUTDOWN_KEY,queue_size=1,frame_debug_mode="IHA"):

        self.mavlink_ip = mavlink_ip
        self.mavlink_port = mavlink_port
        self.takim_no = takimNo

        self.yonelim_ip=yonelim_ip

        self.frame_debug_mode = frame_debug_mode
        self.SHUTDOWN_KEY = SHUTDOWN_KEY

        self.event_map = event_map

        self.fark = 0
        self.is_qrAvailable = False
        self.is_qr_transmitted = "False"
        self.YKI_CONFIRMATION_STATUS = False
        
        self.qr_coordinat = ""

        # *GÖREV_MODU SEÇİMİ
        self.event_map = event_map
        self.secilen_görev_modu="kilitlenme"
        self.önceki_mod = ""
        self.sunucu_saati:str = ""
        # Telemetri paketi için PWM'den veriler alınmalı
        self.iha_mod = 0
        self.x_center=0
        self.y_center=0
        self.width=0
        self.height=0
        self.rakip=0

        self.kullanici_adi = "algan" #ID-23
        self.sifre = "Ea5ngUqWYV"
        self.ana_sunucu = ana_sunucu_islemleri.sunucuApi(f"http://{ana_sunucu_ip}:{ana_sunucu_port}")

        #* Servers # 
        #* < Yazılım_PC-IHA :8000 >  <Yazılım_PC-Yonelim_PC :9000 >   <Yonelim_PC-IHA :11000 >
        #* IHA -- YazılımPC
        self.Server_PWM = Server_Tcp.Server(PORT=8001,name="KALMAN-PWM")
        self.Server_MOD = Server_Tcp.Server(PORT=8002,name="MODE")
        self.Server_KAMIKAZE = Server_Tcp.Server(PORT=8003,name="KAMIKAZE")
        self.Server_CONFIRMATION = Server_Tcp.Server(PORT=8004,name="CONFIRMATION")
        #* YonelimPC -- YazılımPC
        self.Server_UI_Telem = Client_Udp.data_Client(server_ip=self.yonelim_ip, server_port=11000 ,name="UI_TELEM")
        self.Server_UI_Control = Server_Tcp.Server(PORT=11001,name="UI-CONTROL")

        #* Server State
        self.ANA_SUNUCU_DURUMU=False
        self.KALMAN_PWM_SERVER_STATUS=False
        self.MODE_SERVER_STATUS=False
        self.KAMIKAZE_SERVER_STATUS=False
        self.CONFIRMATION_SERVER_STATUS=False

        self.MAVPROXY_SERVER_STATUS=False

        self.UI_TELEM_SERVER_STATUS=True
        self.UI_VIDEO_SERVER_STATUS=False
        cp.ok("Server Manager initialized ✓✓✓")
    
    def senkron_local_saat(self):
        status_code, sunuc_saati = self.ana_sunucu.sunucu_saati_al()
        local_saat = datetime.datetime.today()
        sunuc_saati = json.loads(sunuc_saati)
        sunucu_saat, sunucu_dakika, sunucu_saniye, sunucu_milisaniye = sunuc_saati["saat"], sunuc_saati["dakika"],sunuc_saati["saniye"], sunuc_saati["milisaniye"]
        sunucu_saati = datetime.datetime(year=local_saat.year,
                                         month=local_saat.month,
                                         day=local_saat.day,
                                         hour=sunucu_saat,
                                         minute=sunucu_dakika,
                                         second=sunucu_saniye,
                                         microsecond=sunucu_milisaniye)
        self.fark = abs(local_saat - sunucu_saati)
        cp.info(f"Sunucu Saat Farki: {self.fark}")
        return self.fark

    def anasunucuya_baglan(self):
        connection_status = False
        while not connection_status:
            try:
                "Burada durum kodu işlemin başarı kodunu vermektedir örn:200"
                ana_sunucuya_giris_kodu, durum_kodu = self.ana_sunucu.sunucuya_giris(str(self.kullanici_adi),str(self.sifre))
                if (durum_kodu):
                    cp.ok(f"Ana Sunucuya Bağlanıldı:{durum_kodu}")  # Ana sunucuya girerkenki durum kodu.
                    connection_status = True
                    self.ANA_SUNUCU_DURUMU = connection_status
                elif(int(durum_kodu)==400):
                    raise Exception("DURUM KODU 400 :")
                else:
                    raise Exception("DURUM KODU '200' DEGIL")
            except Exception as e:
                cp.err(f"ANA SUNUCU : BAGLANTI HATASI -> {e}")

    def CREATE_PWM_SERVER(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_PWM.creat_server()
                connection_status=True
                cp.ok("PWM SERVER : OLUŞTURULDU..")
            except (ConnectionError, Exception) as e:
                cp.warn(f"PWM SERVER: oluştururken hata :{e} \nPWM SERVER: yeniden bağlanılıyor... ")
                self.Server_PWM.reconnect()
                cp.ok("PWM : SERVER OLUŞTURULDU...RETRY..")
        self.KALMAN_PWM_SERVER_STATUS=connection_status
        return connection_status

    def CREATE_MOD_SERVER(self):
        connection_status=False
        while not connection_status:
            try:
                connection_status=self.Server_MOD.creat_server()
                cp.ok("TRACK SERVER: OLUSTURULDU..")
            except (ConnectionError, Exception) as e:
                cp.warn(f"TRACK SERVER: OLUSTURULAMADI : {e}\TRACK SERVER: YENIDEN BAGLANIYOR...")
                connection_status=self.Server_MOD.reconnect()
                cp.ok("TRACK SERVER: OLUSTURULDU..")
        self.MODE_SERVER_STATUS=connection_status
        return connection_status

    def CREATE_KAMIKAZE_SERVER(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_KAMIKAZE.creat_server()
                connection_status=True
                cp.ok("KAMIKAZE : SERVER OLUŞTURULDU..")
            except (ConnectionError, Exception) as e:
                cp.warn(f"KAMIKAZE SERVER: oluştururken hata :{e}\nKAMIKAZE SERVER: yeniden bağlanılıyor...")
                self.Server_KAMIKAZE.reconnect()
                cp.ok("KAMIKAZE : SERVER OLUŞTURULDU..RETRY..")
        self.KAMIKAZE_SERVER_STATUS = connection_status
        return connection_status

    def CREATE_CONFIRMATION_SERVER(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_CONFIRMATION.creat_server()
                connection_status=True
                cp.ok("KONTROL-ONAY : SERVER OLUSTURULDU..\n")
            except (ConnectionError, Exception) as e:
                cp.warn(f"KONTROL-ONAY SERVER -> SERVER OLUSTURURKEN HATA :{e}\nKONTROL-ONAY SERVER :YENIDEN BAGLANIYOR...")
                self.Server_CONFIRMATION.reconnect()
                cp.ok("KONTROL-ONAY SERVER : OLUSTURULDU..RETRY..\n")
        self.CONFIRMATION_SERVER_STATUS = connection_status
        return connection_status

    def CREATE_MAVPROXY_SERVER(self):
        mavlink_obj = SimplifiedTelemetry.Telemetry(Mp_Ip=self.mavlink_ip,Mp_Port=self.mavlink_port,takimNo=self.takim_no)
        connection_status = False
        while not connection_status:
            try:
                mavlink_obj.connect()
                connection_status = True
                cp.ok("MAVLINK SERVER : OLUSTURULDU..")
            except (ConnectionError, Exception) as e:
                cp.warn(f"MAVLINK SERVER : OLUSTURURKEN HATA -> {e}\nMAVLINK SERVER : Yeniden baglanılıyor..")
                connection_status=mavlink_obj.connect()
                cp.ok("MAVLINK : SERVER OLUSTURULDU...RETRY..")
        self.MAVPROXY_SERVER_STATUS=connection_status
        return connection_status,mavlink_obj

    #! Arayüze telemetri verisi sağlayan kısım TCP'den UDP'ye geçirildiği için bu fonksiyon işlevsiz kaldı...
    # def CREATE_UI_TELEM_SERVER(self):
    #     connection_status=False
    #     while not connection_status:
    #         try:
    #             self.Server_UI_Telem.create_server()
    #             connection_status=True
    #             cp.ok("UI_TELEM : SERVER OLUSTURULDU..")
    #         except (ConnectionError, Exception) as e:
    #             cp.warn(f"UI_TELEM : SERVER OLUSTURURKEN HATA -> {e}\nUI_TELEM : SERVER YENIDEN BAGLANIYOR..")
    #             # self.Server_UI_telem.reconnect()
    #             # cp.ok("UI_TELEM : SERVER OLUSTURULDU..")
    #     self.UI_TELEM_SERVER_STATUS = connection_status
    #     return connection_status

    def SEND_PWM(self,pwm_data):
        try:
            self.Server_PWM.send_data_to_client(pickle.dumps(pwm_data))
        except Exception as e:
            cp.err(f"PWM SERVER SEND ERROR -> {e}")
            #self.KALMAN_PWM_SERVER_STATUS=False
            #self.Server_PWM.reconnect()

    def SV_MAIN(self):

        cp.info("Sunucular bekleniyor...")
        t0 = threading.Thread(target=self.anasunucuya_baglan)
        t1=threading.Thread(target=self.CREATE_PWM_SERVER)
        t2 = threading.Thread(target=self.CREATE_MOD_SERVER)
        t3 = threading.Thread(target=self.CREATE_KAMIKAZE_SERVER)
        t4 = threading.Thread(target=self.CREATE_CONFIRMATION_SERVER)
        #t8= threading.Thread(target=self.CREATE_UI_TELEM_SERVER) #! İPTAL

        t0.start()
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        #t8.start()

        t0.join()
        return t0,t1,t2,t3,t4 #t8 #t1,t6

    #! KONTROL FONKSİYONU
    def trigger_event(self, event_id, message):
        try:
            if event_id in self.event_map:
                    queue, event = self.event_map[event_id]
                    queue.put(message)
                    event.set()
            else:
                raise ValueError(f"Event_map do not contain '{event_id}'")
        except Exception as e:
            print("TRIGGER ERROR -> ",e)

    #! ANA FONKSİYONLAR

    #? UI-TESTING
    def HSS_TEST(self):
        print("HSS")
        status_code,hss_coord=self.ana_sunucu.get_hava_savunma_coord()
        message_type = "HSS"
        self.Server_UI_Telem.send_data(json.dumps([message_type,hss_coord]))
        print(hss_coord)

    def HSS_2_TEST(self):
        print("HSS")
        status_code,hss_coord=self.ana_sunucu.get_hava_savunma_coord()
        hss_coord = json.loads(hss_coord)
        if status_code == 200:
            ucus_alanı=[(36.942314,35.563323),(36.942673,35.553363),(36.937683,35.553324),(36.937864,35.562873)]
            fence_konumları = []
            dosya_adi = "hss.waypoints"
            for i in hss_coord["hss_koordinat_bilgileri"]:
                enlem = float(i["hssEnlem"])
                boylam = float(i["hssBoylam"])
                yarıçap = float(i["hssYaricap"])
                fence_konumları.append((enlem, boylam, yarıçap))

                            
                ucus_alanı_miktarı = len(ucus_alanı)
                fence_konumları_miktarı = len(fence_konumları)

                with open(dosya_adi, 'w') as dosya:
                    dosya.truncate(0)
                    dosya.write("QGC WPL 110\n")
                    dosya.write("0\t1\t0\t16\t0\t0\t0\t0\t40.2320505\t29.0042872\t100.220000\t1\n")
                    for i, konum in enumerate(ucus_alanı, start=1):
                        dosya.write(
                            f"{i}\t0\t0\t5001\t5.00000000\t0.00000000\t0.00000000\t0.00000000\t{konum[0]}\t{konum[1]}\t100.000000\t1\n")
                    for j, konum in enumerate(fence_konumları, start=ucus_alanı_miktarı + 1):
                        dosya.write(
                            f"{j}\t0\t0\t5004\t{float(konum[2]):.8f}\t0.00000000\t0.00000000\t0.00000000\t{konum[0]}\t{konum[1]}\t100.000000\t1\n")

        dosya=r'C:\Users\asus\OneDrive - Pamukkale University\Masaüstü\AlganYazilim-1-YEDEK-HAZIR-CALISIYOR\hss.waypoints'
        print(dosya)
        hedef_klasor=r'\\SEVINÇ\123'
        hedef_dosya = os.path.join(hedef_klasor, os.path.basename(dosya))
        print(hedef_dosya)

        #bu kısım dosya paylaşır.
        shutil.copy2(dosya, hedef_dosya)
        print(f"Dosya başarıyla kopyalandı: {hedef_dosya}")

    def KILITLENME_TEST(self):
        print("KILITLENME-TEST")
        start_now =datetime.datetime.now()
        mission_data = {
                        "kilitlenmeBaslangicZamani": {
                            "saat": start_now.hour-3,
                            "dakika": start_now.minute,
                            "saniye": start_now.second,
                            "milisaniye": start_now.microsecond #TODO düzeltilecek
                        },
                        "kilitlenmeBitisZamani": {
                            "saat": start_now.hour-3,
                            "dakika": start_now.minute,
                            "saniye": start_now.second+4,
                            "milisaniye": start_now.microsecond #TODO düzeltilecek
                        },
                        "otonom_kilitlenme": 1
                            }
        

        status = self.ana_sunucu.kilitlenme_postala(mission_data)
        cp.err(status)
        #cp.warn(ret)

    def QR_TEST(self):
        print("QR-TEST")
        start_now =datetime.datetime.now()
        mission_data = {
                        "kamikazeBaslangicZamani" : {
                            "saat": start_now.hour-3,
                            "dakika": start_now.minute,
                            "saniye": start_now.second,
                            "milisaniye": start_now.microsecond #TODO düzeltilecek
                        },
                        "kamikazeBitisZamani": {
                            "saat": start_now.hour-3,
                            "dakika": start_now.minute,
                            "saniye": start_now.second+4,
                            "milisaniye": start_now.microsecond #TODO düzeltilecek
                        },
                        "qrMetni": "teknofest2024"
                                }
        


        
        status=self.ana_sunucu.kamikaze_gonder(mission_data)
        cp.err(status)
        # cp.warn(ret)

    def yki_onay_ver(self):
        if self.CONFIRMATION_SERVER_STATUS:
            cp.ok(f"YKI ONAY : Server ONLINE / MEVCUT ONAY DURUMU --> {self.YKI_CONFIRMATION_STATUS}")
            if self.YKI_CONFIRMATION_STATUS == False:
                self.Server_CONFIRMATION.send_data_to_client("ALGAN".encode())
                self.YKI_CONFIRMATION_STATUS = True
                cp.warn(f"ONAY VERILDI ---> {self.YKI_CONFIRMATION_STATUS}")
            else:
                self.Server_CONFIRMATION.send_data_to_client("RED".encode())
                self.YKI_CONFIRMATION_STATUS = False
                cp.warn(f"ONAY REDDEDILDI ---> {self.YKI_CONFIRMATION_STATUS}")
        else:
            cp.err(f"YKI ONAY : Server OFFLINE / MEVCUT ONAY DURUMU --> {self.YKI_CONFIRMATION_STATUS}")
            return False

    def telemetri(self):
        timer_start=time.perf_counter()
        ret,mavlink_obj=self.CREATE_MAVPROXY_SERVER()
        telemetri_queue,telem_trigger=self.event_map["Telem1"]
        while True:
            try:
                bizim_telemetri,ui_telemetri=mavlink_obj.telemetry_packet()

                # bizim_telemetri = {"takim_numarasi": 1, "iha_enlem": 0,"iha_boylam":0,"iha_irtifa": 0,"iha_dikilme":0,
                #                    "iha_yonelme":0,"iha_yatis":0,"iha_hiz":0,"iha_batarya":0,"iha_otonom": 1,color
                #                                                        "dakika": time.gmtime().tm_min,
                #                                                        "saniye": time.gmtime().tm_sec,
                #                                                        "milisaniye": int((time.time() % 1) * 1000)
                #                                                        }
                #                     }

                if bizim_telemetri is not None:
                    if time.perf_counter() - timer_start > 1:
                        if telem_trigger.is_set():
                            telemetri_verileri= telemetri_queue.get()
                            bizim_telemetri["iha_kilitlenme"]=telemetri_verileri[1]
                            bizim_telemetri["hedef_merkez_X"]=telemetri_verileri[2]
                            bizim_telemetri["hedef_merkez_Y"]=telemetri_verileri[3]
                            bizim_telemetri["hedef_genislik"]=telemetri_verileri[4]
                            bizim_telemetri["hedef_yukseklik"]=telemetri_verileri[5]
                            telem_trigger.clear()
                        bizim_telemetri["iha_otonom"] = self.iha_mod
                        cp.ok(bizim_telemetri)
                        status_code,rakip_telemetri=self.ana_sunucu.sunucuya_postala(bizim_telemetri) #TODO Telemetri 1hz olmalı...
                        #cp.warn(rakip_telemetri)
                        try:
                            if self.UI_TELEM_SERVER_STATUS:
                                message_type="TELEM"
                                self.Server_UI_Telem.send_data(json.dumps([message_type,rakip_telemetri])) #json.dumps(rakip_telemetri).encode('utf-8'))
                            else:
                                cp.warn("UI-TELEM SERVER OFFLINE")
                        except Exception as e:
                            cp.warn(f"IU_TELEM : DATA SENDING ERROR -> {e}",)
                        timer_start=time.perf_counter()

            except Exception as e:
                cp.warn(f"TELEMETRI : VERI HATASI -> {e}")

    def ana_sunucu_manager(self):
        mission_queue,mission_event=self.event_map["Gorev_verisi"]

        while True:
            if mission_event.is_set():
                time.sleep(0.01)
                [mission_data,mission_type] = mission_queue.get()
                if mission_type=="kilitlenme":
                    self.ana_sunucu.kilitlenme_postala(json.dumps(mission_data))
                elif mission_type=="qr_data":
                    self.ana_sunucu.kamikaze_gonder(json.dumps(mission_data))
                else:
                    cp.err(f"GEÇERSİZ GÖREV ->{mission_type} - {mission_data}")

                mission_event.clear()
            else:
                time.sleep(1)

    def process_flow_manager(self):
        self.SV_MAIN()

        th1 = threading.Thread(target=self.telemetri)
        th2 = threading.Thread(target=self.ana_sunucu_manager)

        th1.daemon = True
        th2.daemon = True

        th1.start()
        th2.start()

        time.sleep(5)

        return th1,th2

    def ANA_GOREV_KONTROL(self):
        th1,th2 = self.process_flow_manager()

        time.sleep(2)

        while True:
            if self.MODE_SERVER_STATUS:
                try:
                    self.secilen_görev_modu = self.Server_MOD.recv_tcp_message()
                    try:
                        if self.SHUTDOWN_KEY == "ALGAN":
                            cp.fatal("FINAL SHUTDOWN..FINAL SHUTDOWN..FINAL SHUTDOWN..FINAL SHUTDOWN..FINAL SHUTDOWN..")
                            break

                        if self.secilen_görev_modu == "KILITLENME" and not (self.önceki_mod=="KILITLENME"):
                            self.trigger_event("Frame_1","kilitlenme")
                            self.trigger_event("Frame_2","kilitlenme")
                            self.önceki_mod = "KILITLENME"
                            self.iha_mod = 1
                            cp.info(f"GOREV MODU : Degisim -> {self.secilen_görev_modu}")

                        elif self.secilen_görev_modu == "KAMIKAZE" and not (self.önceki_mod=="KAMIKAZE"):
                            self.trigger_event("Frame_1","kamikaze")
                            self.trigger_event("Frame_2","kamikaze")
                            self.önceki_mod = "KAMIKAZE"
                            self.iha_mod = 1
                            cp.info(f"GOREV MODU : Degisim -> {self.secilen_görev_modu}")

                        elif self.secilen_görev_modu == "AUTO" and not (self.önceki_mod=="AUTO"):
                            self.trigger_event("Frame_1","AUTO")
                            self.trigger_event("Frame_2","AUTO")
                            self.önceki_mod = "AUTO"
                            self.iha_mod = 1
                            cp.info(f"GOREV MODU : Degisim -> {self.secilen_görev_modu}")

                        elif self.secilen_görev_modu == "FBWA" and not (self.önceki_mod=="FBWA"):
                            self.trigger_event("Frame_1","FBWA")
                            self.trigger_event("Frame_2","FBWA")
                            self.önceki_mod = "FBWA"
                            self.iha_mod = 0
                            cp.info(f"GOREV MODU : Degisim -> {self.secilen_görev_modu}")

                        elif self.secilen_görev_modu == "RTL" and not (self.önceki_mod=="RTL"):
                            self.trigger_event("Frame_1","RTL")
                            self.trigger_event("Frame_2","RTL")
                            self.önceki_mod = "RTL"
                            self.iha_mod = 1
                            cp.info(f"GOREV MODU : Degisim -> {self.secilen_görev_modu}")

                        else:
                            cp.info(f'GOREV MODU :{self.önceki_mod}')

                    except Exception as e:
                        print("ANA_GOREV_KONTROL HATA: ",e)
                except Exception as e:
                    cp.err(f"MOD : Secilen modu alirken hata -> {e}") #TODO EKLENECEK...
                    cp.err(" 'MODE_SERVER_STATUS' set to: <FALSE>")
                    self.MODE_SERVER_STATUS=False

            else:
                cp.fatal("MOD SERVER OFFLINE")
                self.MODE_SERVER_STATUS=False
                self.Server_MOD.reconnect()
                time.sleep(1)
            
            #? ISTENILEN BUTUN DURUMLAR EKLENEBILIR...

class Frame_processing:

    def __init__(self,event_map,frame_debug_mode="IHA",):
        self.yolo_model = YOLOv8_deploy.Detection2("C:\\Users\\asus\\AlganYazilim-1\\Savasan-iha\\Models\\Model_2024_V6_best.pt")
        self.qr = QR_Detection()
        self.frame_debug_mode = frame_debug_mode

        #*External queues
        self.event_map = event_map

        #*Internal queues
        self.capture_queue=mp.Queue()
        frame_process_1=mp.Queue()
        frame_process_2=mp.Queue()
        self.detection_queues=[0,frame_process_1,frame_process_2]
        self.display_queue=mp.Queue()
        
        #* Kalman Filter
        self.datas = []
        #self.kalman = KalmanFilter()

        self.VIDEO_SERVER_STATUS=False
        self.MODE_SERVER_STATUS=False

    #!Server
    def CREATE_UDP_SERVER(self,Server_obj):
        connection_status=False
        while not connection_status:
            try:
                Server_obj.create_server()
                connection_status=True
                cp.ok(f"{Server_obj.name} : OLUŞTURULDU..")
            except (ConnectionError , Exception) as e:
                cp.warn(f"{Server_obj.name}: oluştururken hata :{e}")
            #    cp.warn("UDP SERVER'A 3 saniye içinden yeniden bağlanılıyor...\n")
            #   self.Server_udp.close_socket()
            #   self.Server_udp = Server_Udp.Server()
            #   self.Server_udp.create_server() #TODO DÜZENLEME GELEBİLİR
        self.VIDEO_SERVER_STATUS = connection_status
        return connection_status

    def CREATE_PWM_SERVER(self,Server_obj):
        connection_status=False
        while not connection_status:
            try:
                connection_status=Server_obj.creat_server()
                cp.ok("KALMAN-PWM SERVER: OLUSTURULDU..")
            except (ConnectionError, Exception) as e:
                cp.warn(f"KALMAN-PWM SERVER: OLUSTURULAMADI : {e}\KALMAN-PWM SERVER: YENIDEN BAGLANIYOR...")
                connection_status=Server_obj.reconnect()
                cp.ok("KALMAN-PWM SERVER: OLUSTURULDU..")
        self.MODE_SERVER_STATUS=connection_status
        return connection_status

    #!Calculations
    def kalman_predict(self,kalman_obj, x_center, y_center):
        data = [x_center, y_center]
        self.datas.append(data)
        if len(self.datas) >= 20:
            self.datas = self.datas[-20:]
        kalmanPWMx, KalmanPWMy = kalman_obj.add_measurements(self.datas)
        return kalmanPWMx, KalmanPWMy

    # def qr_oku(self, frame):
    #     qr_result = self.qr.file_operations(frame=frame)
    #     return qr_result ,frame
    
    def qr_oku(self, frame):
        qr_result = self.qr.file_operations(frame=frame)
        return qr_result ,frame
    #!Frames
    def capture(self):
        process_name = mp.current_process().name
        cp.info(f"Starting Capture-process: {process_name}")

        Server_Video=Server_Udp.Server(PORT=5555,name="IHA-VIDEO")
        Frame_server_thread=threading.Thread(target=self.CREATE_UDP_SERVER,args=(Server_Video,))
        Frame_server_thread.start()

        cp.fatal(f"FRAME_DEBUG_MODE:{self.frame_debug_mode}")
        while True:
            if self.VIDEO_SERVER_STATUS:
                cp.ok("Video Server ONLINE...")
                if self.frame_debug_mode == "IHA":
                    codec_1 = av.CodecContext.create('h264', 'r')
                    frame_id = 0
                    while True:
                        try:
                            data = Server_Video.recv_frame_from_client()
                            packet = av.Packet(data)
                            frames = codec_1.decode(packet)
                            for frame in frames:
                                try:
                                    img = frame.to_image()
                                    frame = np.array(img)
                                    frame=cv2.flip(frame,-1)
                                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                    if not self.capture_queue.full():
                                        self.capture_queue.put((frame,frame_id))
                                        frame_id += 1
                                        #print("FRAME :SAVED IN CAPTURE_QUEUE ...")
                                    else:
                                        #print("FRAME : CAPTURE_QUEUE FULL...")
                                        pass
                                except Exception as e:
                                    cp.err("FRAME : CAPTURE_QUEUE ERROR -> ",e)
                        except Exception as e:
                            cp.err(f"FRAME : RECEIVE ERROR ->{e}")

                elif self.frame_debug_mode == "LOCAL":
                    frame_id = 0
                    while True:
                        try:
                            frame = Server_Video.recv_frame_from_client()
                            try:
                                if not self.capture_queue.full():
                                    self.capture_queue.put((frame,frame_id))
                                    frame_id += 1
                                    #print("FRAME :SAVED IN CAPTURE_QUEUE ...")
                                else:
                                    #print("FRAME : CAPTURE_QUEUE FULL...")
                                    pass
                            except Exception as e:
                                cp.err(f"FRAME : CAPTURE_QUEUE ERROR -> {e}")
                        except Exception as e:
                            cp.err(f"FRAME : RECEIVE ERROR -> {e}")
            else:
                cp.err("Video Server Down...Waiting....")
                time.sleep(1)

    def Image_detection(self,event_map_id:str):
        process_name = mp.current_process().name
        cp.info(f"Starting Image_DETECTION-process: {process_name}")

        #*External Queues
        message_queue , message_trigger=self.event_map[event_map_id]
        telem_queue , telem_trigger=self.event_map["Telem1"]
        kalman_pwm_queue , kalman_pwm_event=self.event_map["Kalman"]
        mission_queue,mission_event=self.event_map["Gorev_verisi"]

        lockedOrNot = 0
        locked_prev = 0
        message = "AUTO"
        is_locked = 0
        sent_once = 0

        while True:
            if message_trigger.is_set():
                time.sleep(0.01)
                message = message_queue.get()
                cp.warn(f"{process_name} received event: {message}")
                message_trigger.clear()

            if not self.capture_queue.empty():
                (frame,frame_id) = self.capture_queue.get()

                if message == "kilitlenme":
                    telemetri_verileri, kalman_data, processed_frame, lockedOrNot = self.yolo_model.model_predict(frame=frame,frame_id=frame_id)
                    telem_queue.put(telemetri_verileri)
                    telem_trigger.set()

                    #* 4 SANIYE-KILITLENME
                    #Hedef Görüldü.
                    if lockedOrNot == 1 and locked_prev == 0:
                            lock_start_time=time.perf_counter()
                            start_now =datetime.datetime.now()
                            
                            cv2.putText(img=processed_frame,text="HEDEF GORULDU",org=(50,400),fontFace=1,fontScale=2,color=(0,255,0),thickness=2)
                            locked_prev=1
                            kalman_pwm_queue.put(kalman_data)
                    #Hedef kayboldu.
                    if lockedOrNot == 0 and locked_prev== 1:
                            cv2.putText(img=processed_frame,text="HEDEF KAYBOLDU",org=(50,400),fontFace=1,fontScale=2,color=(0,255,0),thickness=2)
                            locked_prev= 0
                            is_locked= 0
                            sent_once = 0

                    if lockedOrNot == 1 and locked_prev== 1:
                            kalman_pwm_queue.put(kalman_data)
                            lock_elapsed_time= time.perf_counter() - lock_start_time
                            cv2.putText(img=processed_frame,text=str(round(lock_elapsed_time,3)),org=(50,370),fontFace=1,fontScale=1.5,color=(0,255,0),thickness=2)
                            if is_locked == 0:
                                cv2.putText(img=processed_frame,text="KILITLENIYOR",org=(50,400),fontFace=1,fontScale=1.8,color=(0,255,0),thickness=2)
                            if lock_elapsed_time >= 4.0:
                                cv2.putText(img=processed_frame,text="KILITLENDI",org=(50,400),fontFace=1,fontScale=1.8,color=(0,255,0),thickness=2)
                                kilitlenme_bilgisi=True
                                is_locked=1
                                #pwm_trigger.clear()
                                # #Kilitlenme gerçekleşti. Yönelim moduna geri dön.

                    if is_locked == 1 and sent_once == 0:
                            end_now = datetime.datetime.now()
                            kilitlenme_bilgisi = {
                                "kilitlenmeBaslangicZamani": {
                                    "saat": start_now.hour,
                                    "dakika": start_now.minute,
                                    "saniye": start_now.second,
                                    "milisaniye": start_now.microsecond #TODO düzeltilecek
                                },
                                "kilitlenmeBitisZamani": {
                                    "saat": end_now.hour,
                                    "dakika": end_now.minute,
                                    "saniye": end_now.second,
                                    "milisaniye": end_now.microsecond #TODO düzeltilecek
                                },
                                "otonom_kilitlenme": 0
                            }
                            mission_queue.put([kilitlenme_bilgisi,"kilitlenme"])
                            mission_event.set()
                            sent_once=1

                    if not self.display_queue.full():
                        self.display_queue.put(processed_frame)

                elif message == "kamikaze":
                    qr_text,processed_frame = self.qr_oku(frame)
                    
                    # if qr_text != None :
                    #     qr_once_event.set()
                    # elif qr_text == None:
                    #     qr_once_event.clear()
                        
                    #if qr_once_event.is_set() and (not qr_outer_event.is_set()):
                    # if qr_once_event.is_set():
                    #     self.trigger_event(6,(qr_text,"qr"))
                    if qr_text != None :
                        mission_queue.put([qr_text,"qr_data"])
                        mission_event.set()

                    if not self.display_queue.full():
                        self.display_queue.put(processed_frame)
                
                elif message == "AUTO" or message == "FBWA" or message == "RTL":
                    if not self.display_queue.full():
                        self.display_queue.put(frame)

                else:
                    cp.warn("Process_frame :INVALID MODE...")
                    time.sleep(0.5)

    def display(self):
        process_name = mp.current_process().name
        cp.info(f"Starting Capture-process: {process_name}")

        Arayuz_Frame_queue,Arayuz_Frame_trigger=self.event_map["UI-FRAME"]
        display_record_queue,display_record_trigger = self.event_map["Display-Record"]
        
        fourrcc = cv2.VideoWriter_fourcc(*'MP4V')
        videoKayit = cv2.VideoWriter('video.mp4', fourrcc, 30.0, (640, 480))
        
        is_stream_available = False
        frame_count:float= 0.0
        fps:float = 0.0
        with pyvirtualcam.Camera(width=640,height=480,fps=30) as cam:
            while True:
                if not self.display_queue.empty():
                    if not is_stream_available:
                        fps_start_time = time.perf_counter()
                        is_stream_available = True

                    frame = self.display_queue.get() #TODO EMPTY Queue blocking test?
                    now = datetime.datetime.now()
                    #virtual_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    current_time = now.strftime("%H:%M:%S") + f".{now.microsecond//1000:03d}"
                    cv2.putText(frame,"SUNUCU : "+current_time , (420, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 128, 0), 2)
                    cv2.putText(frame, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 128, 0), 2)
                    videoKayit.write(frame)    
                    if not Arayuz_Frame_queue.full():
                        Arayuz_Frame_queue.put(frame)
                    #cam.send(frame= virtual_frame)
                    cv2.imshow('Camera', frame)
                    fps = frame_count / (time.perf_counter() - fps_start_time)
                    frame_count += 1.0
                else:
                    pass

                if cv2.waitKey(1) & 0xFF == ord('q'): #TODO sonradan kalkabilir.
                    break
                
                if display_record_trigger.is_set():
                    time.sleep(0.01)
                    event_message = display_record_queue.get()
                    cp.warn(f"{process_name} received event: {event_message}")
                    display_record_trigger.clear()

                    if event_message=="stop_capture":
                        videoKayit.release()

        videoKayit.release()
        cv2.destroyAllWindows()

    def PWM(self):
        kalman = KalmanFilter()
        kalman_pwm_queue,kalman_pwm_event = self.event_map["Kalman"]

        while True:
            if not kalman_pwm_queue.empty():
                kalman_tuple= kalman_pwm_queue.get()
                if self.KALMAN_PWM_SERVER_STATUS:
                    kalman_tuple=self.kalman_predict(kalman_obj=kalman,x_center=kalman_tuple[0], y_center=kalman_tuple[1])
                    self.SEND_PWM(kalman_tuple)
                else:
                    cp.warn(f"KALMAN_PWM SERVER OFFLINE")
                    time.sleep(1)

    #! KONTROL FONKSİYONU
    def trigger_event(self, event_name, message):
        try:
            if event_name in self.event_map:
                    queue, event = self.event_map[event_name]
                    queue.put(message)
                    event.set()
            else:
                raise ValueError(f"Event_map do not contain {event_name}")
        except Exception as e:
            cp.warn(f"TRIGGER ERROR -> {e}")

    def run_processes(self):
        p1=mp.Process(target=self.capture)
        p2_1=mp.Process(target=self.Image_detection,args=("Frame_1",))
        p2_2=mp.Process(target=self.Image_detection,args=("Frame_2",))
        p3=mp.Process(target=self.display)

        p1.start()
        p2_1.start()
        p2_2.start()
        p3.start()

class Graphical_User_Interface:
    def __init__(self,Yer_istasyonu_obj):
        self.Gui_obj = App(Yer_istasyonu_obj=yer_istasyonu_obj)

    def start(self):
        self.Gui_obj.run()

def create_event_map():
    #Process frames
    frame_queue_1 = mp.Queue()
    frame_event_1 = mp.Event()
    frame_queue_2 = mp.Queue()
    frame_event_2 = mp.Event()
    frame_queue_3 = mp.Queue()
    frame_event_3 = mp.Event()

    #AnaSunucu<--Telemetri
    telem_queue=mp.Queue()
    telem_event=mp.Event()
    kalman_pwm_queue=mp.Queue()
    kalman_pwm_event=mp.Event()
    Arayuz_Frame_queue=mp.Queue()
    Arayuz_Frame_trigger=mp.Event()
    mission_queue=mp.Queue()
    mission_event=mp.Event()
    
    
    display_record_queue=mp.Queue()
    display_record_trigger=mp.Event()
    

    #Kilitlenme mod change
    yonelim_queue = mp.Queue()
    yonelim_event = mp.Event()
    pwm_data_queue = mp.Queue()
    pwm_event = mp.Event()

    ana_sunucu_queue = mp.Queue()
    sunucu_event =  mp.Event()

    lock_once_event = mp.Event()
    qr_once_event = mp.Event()
    lock_outer_event = mp.Event()
    qr_outer_event = mp.Event()

    arayuz_frame_queue = mp.Queue()
    arayuz_telem_queue = mp.Queue()

    display_process_queue=mp.Queue()
    display_process_event=mp.Event()

    event_map = {
    "Frame_1": (frame_queue_1, frame_event_1),
    "Frame_2": (frame_queue_2, frame_event_2),
    "Frame_3": (frame_queue_3, frame_event_3),
    "Telem1" : (telem_queue,telem_event),
    "Kalman" : (kalman_pwm_queue,kalman_pwm_event),
    "UI-FRAME": (Arayuz_Frame_queue,Arayuz_Frame_trigger),
    "Display-Record":(display_process_queue,display_process_event),
    "Gorev_verisi" : (mission_queue,mission_event)
    #TODO EKLENECEK
    }
    return event_map

def check_picklability(obj):
    """
    This function checks if the attributes of an object are picklable.
    It returns a list of attributes that are not picklable.
    """
    non_picklable_attrs = []
    for attr_name in dir(obj):
        # Ignore built-in attributes and methods (anything that starts with '__')
        if attr_name.startswith("__"):
            continue
        attr_value = getattr(obj, attr_name)
        try:
            pickle.dumps(attr_value)  # Attempt to pickle the attribute
        except Exception as e:
            non_picklable_attrs.append((attr_name, type(attr_value), str(e)))
    
        non_picklable_attributes = check_picklability(Frame_processing_obj)
    if non_picklable_attributes:
        cp.warn("Non-picklable attributes found:")
        for attr_name, attr_type, error in non_picklable_attributes:
            cp.warn(f"Attribute: {attr_name}, Type: {attr_type}, Error: {error}")
    else:
        cp.warn("All attributes are picklable.")

if __name__ == '__main__':
    SHUTDOWN_KEY = ""
    event_map = create_event_map()

    Frame_processing_obj=Frame_processing(frame_debug_mode="LOCAL",
                                          event_map=event_map
                                            ) #! IHA / LOCAL
    
    yer_istasyonu_obj = YerIstasyonu(
                                    yonelim_ip="10.0.0.123", #! Yönelim bilgisayarı ip(str) -> 10.0.0.180
                                    ana_sunucu_ip="10.0.0.123", ana_sunucu_port="10001", #! Teknofest Sunucu ip(str)-> 10.0.0.10 , port(str)-> 10001
                                    mavlink_ip="10.0.0.123", mavlink_port=14550, #! mission planner ip(str)-> 10.0.0.180 , mavlink_port(int) -> 14550
                                    takimNo=23,
                                    event_map=event_map,
                                    SHUTDOWN_KEY=SHUTDOWN_KEY,
                                    queue_size=2 #TODO OPTIMAL DEĞER BULUNMALI...
                                        )
    
    Gui_obj=Graphical_User_Interface(
                                    Yer_istasyonu_obj=yer_istasyonu_obj
                                    )

    t1=threading.Thread(target=yer_istasyonu_obj.ANA_GOREV_KONTROL)

    Frame_processing_obj.run_processes()
    t1.start()
    Gui_obj.start()
    
    cp.fatal("FINAL")