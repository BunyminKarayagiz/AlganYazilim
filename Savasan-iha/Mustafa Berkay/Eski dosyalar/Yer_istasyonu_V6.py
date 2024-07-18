import numpy as np
from pyzbar import pyzbar

import Server_Udp
import Server_Tcp
from path import Plane
import ana_sunucu_islemleri
import threading
import cv2
import YOLOv8_deploy
import json
import time, datetime
import asyncio
import mavproxy2
import hesaplamalar
from qr_detection import QR_Detection

# KOD ÇALIŞTIRMA SIRASI: sunucuapi -> Yer_istasyonu_v6 -> Iha_test(PUTTY) -> Iha_haberlesme(PUTTY)
class Yerİstasyonu():

    def __init__(self, mavlink_ip): #TODO HER BİLGİSAYAR İÇİN PATH DÜZENLENMELİ
        self.yolo_model = YOLOv8_deploy.Detection("D:\\Visual Code File Workspace\\ALGAN\\AlganYazilim\\Savasan-iha\\Mustafa Berkay\\Model2024_V1.pt")
        self.ana_sunucuya_giris_durumu = False
        self.ana_sunucu = ana_sunucu_islemleri.sunucuApi("http://127.0.0.1:5000")

        self.Server_yönelim = Server_Tcp.Server(9002,name="YÖNELİM")
        self.Server_pwm = Server_Tcp.Server(9001,name="PWM")
        self.Server_udp = Server_Udp.Server()
        self.Server_mod = Server_Tcp.Server(9003,name="MOD")

        #Sunucu durumları için kullanılacak değişkenler
        self.görüntü_sunucusu=False
        self.Yönelim_sunucusu=False
        self.Mod_sunucusu=False
        self.PWM_sunucusu=False
        self.MAV_PROXY_sunucusu=False

        #YÖNELİM yapılacak uçağın seçilmesi için kullanılacak obje
        self.yönelim_obj=hesaplamalar.Hesaplamalar()

        #M.PLANNER bilgisayarından telemetri verisi çekmek için kullanılacak obje
        self.mavlink_obj = mavproxy2.MAVLink(mavlink_ip)

        #PWM sinyal üretiminin senkronizasyonu için kullanılan objeler
        #self.lock= asyncio.Lock()
        self.pwm_event=asyncio.Event()
        self.pwm_release=False

        #MOD DEĞİŞİM EVENTLERİ
        self.qr_release_event = threading.Event()
        self.kamikaze_release_event = threading.Event()
        self.yönelim_release_event = threading.Event()
        self.kilitlenme_release_event = threading.Event()


        #Görüntüye rakibin yakalanması durumunda pwm moduna geçiş yapacak obje
        self.yönelim_modundan_cikis_eventi=threading.Event()
        self.yönelim_modu=True

        #Kilitlenme yapılırken kullanılan parametreler
        self.locked_prev=0
        self.is_locked=0
        self.sent_once=0
        self.elapsed_time=0
        self.start_time=0
        self.start_now:datetime.datetime = 0

        # Kamikaze yapılırken kullanılan parametreler
        self.qr_coordinat = ""
        self.fark = 0
        self.qr = QR_Detection()

        #Framerate Hesaplama parametreleri
        self.new_frame_time=0
        self.prev_frame_time=0

        #GÖREV_MODU SEÇİMİ #TODO-Daha yapılmadı. İHA VEYA MİSSİON PLANNER BİLGİSAYARINDAN ALINMASI GEREKİYOR.
        self.secilen_görev_modu="kilitlenme"
        self.mod_event=threading.Event()
        self.frame=0
        self.TCP_ONAYLAMA_KODU="ALGAN"
        self.sunucu_saati:str = ""

    # SUNUCU FONKSİYONLARI
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
        print("Sunucu Saat Farki: ", self.fark)

    def anasunucuya_baglan(self, kullanici_adi, sifre):
        "Burada durum kodu işlemin başarı kodunu vermektedir örn:200"
        ana_sunucuya_giris_kodu, durum_kodu = self.ana_sunucu.sunucuya_giris(
            str(kullanici_adi),
            str(sifre))
        if int(durum_kodu) == 200:
            print(f"\x1b[{31}m{'Ana Sunucuya Bağlanıldı: ' + durum_kodu}\x1b[0m")  # Ana sunucuya girerkenki durum kodu.
            self.ana_sunucuya_giris_durumu = True
        return self.ana_sunucuya_giris_durumu

    def Görüntü_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_udp.create_server()
                connection_status=True
                print("UDP : SERVER OLUŞTURULDU")
            except (ConnectionError , Exception) as e:
                print("UDP SERVER: oluştururken hata : ", e)
            #    print("UDP SERVER'A 3 saniye içinden yeniden bağlanılıyor...\n")
            #   self.Server_udp.close_socket()
            #   self.Server_udp = Server_Udp.Server()
            #   self.Server_udp.create_server() #TODO DÜZENLEME GELEBİLİR
        self.görüntü_sunucusu=connection_status
        return connection_status

    def Yönelim_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_yönelim.creat_server()
                connection_status=True
                print("YONELİM : SERVER OLUŞTURULDU")
            except (ConnectionError, Exception) as e:
                print("YÖNELİM SERVER: oluştururken hata : ", e , " \n")
                print("YÖNELİM SERVER: yeniden bağlanılıyor...\n")
                connection_status=self.Server_yönelim.reconnect()
                print("YONELİM : SERVER OLUŞTURULDU.")

        self.Yönelim_sunucusu=connection_status

    def PWM_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_pwm.creat_server()
                connection_status=True
                print("PWM : SERVER OLUŞTURULDU\n")
            except (ConnectionError, Exception) as e:
                print("PWM SERVER: oluştururken hata : ", e , " \n")
                print("PWM SERVER: yeniden bağlanılıyor...\n")
                self.Server_pwm.reconnect()
                print("PWM : SERVER OLUŞTURULDU\n")
        self.Yönelim_sunucusu=connection_status
        return connection_status

    def Mod_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_mod.creat_server()
                connection_status=True
                print("MOD : SERVER OLUŞTURULDU\n")
            except (ConnectionError, Exception) as e:
                print("MOD SERVER: oluştururken hata : ", e , " \n")
                print("MOD SERVER: yeniden bağlanılıyor...\n")
                self.Server_pwm.reconnect()
                print("MOD : SERVER OLUŞTURULDU\n")
        self.Mod_sunucusu_sunucusu = connection_status
        return connection_status

    def MAV_PROXY_sunucusu_oluştur(self):
        connection_status = False
        while not connection_status:
            try:
                self.mavlink_obj.connect()
                connection_status = True
                print("MAVLINK : SERVER OLUŞTURULDU\n")
            except (ConnectionError, Exception) as e:
                print("MAVLINK SERVER: oluştururken hata : ", e , " \n")
                print("MAVLINK SERVER: yeniden bağlanılıyor...\n")
                connection_status=self.mavlink_obj.connect()
        self.MAV_PROXY_sunucusu=connection_status
        return connection_status


    # Frame işleyen fonksiyonlar

    def Yolo_frame_işleme(self, frame):

        "Gelen frame yolo modeline sokuluyor"
        pwm_verileri, frame, lockedOrNot = self.yolo_model.model_predict(frame)
        # results,frame=yer_istasyonu.yolo_model.get_results(frame)
        return frame, lockedOrNot, pwm_verileri

    def qr_oku(self, frame):
        qr_result = self.qr.file_operations(frame=frame)
        return qr_result
    
    def görüntü_çek(self):
        try:
            frame = self.Server_udp.recv_frame_from_client()
            return frame
        except Exception as e:
            print("UDP: GÖRÜNTÜ ALINIRKEN HATA..",e)


    # KİLİTLENME MODUNDA ÇALIŞACAK FONKSİYONLAR

    def pwm_gönder(self,pwm_verileri):
        try:
            self.Server_pwm.send_data_to_client(json.dumps(pwm_verileri).encode())
        except Exception as e:
            print("PWM SUNUCU HATASI : ",e)
            print("PWM SUNUCUSUNA TEKRAR BAGLANIYOR...")
            self.Server_pwm.reconnect()

    async def sunucu_saati(self):
        sunucu_kod , sunucu_saat = self.ana_sunucu.sunucu_saati_al()
        if (sunucu_kod == 200):
            self.sunucu_saati = sunucu_saat

    async def kilitlenme_kontrol(self,frame,lockedOrNot,pwm_verileri):

        self.new_frame_time=time.time()

        "Rakip kilitlenme"
        if lockedOrNot == 1 and self.locked_prev== 0:
            self.start_time=time.time()
            self.start_now =datetime.datetime.now()
            cv2.putText(img=frame,text="HEDEF GORULDU",org=(50,400),fontFace=1,fontScale=2,color=(0,255,0),thickness=2)
            self.locked_prev=1

            #Hedef Görüldü. Yönelim modu devre dışı.
            self.yönelim_modu=False

        if lockedOrNot == 0 and self.locked_prev== 1:
            cv2.putText(img=frame,text="HEDEF KAYBOLDU",org=(50,400),fontFace=1,fontScale=2,color=(0,255,0),thickness=2)
            self.locked_prev= 0
            self.is_locked= 0
            self.sent_once = 0

            #Hedef kayboldu. Yönelim Moduna geri dön.
            self.yönelim_modu=True
            self.yönelim_modundan_cikis_eventi.set()

        if lockedOrNot == 1 and self.locked_prev== 1:
            self.elapsed_time= time.time()- self.start_time
            cv2.putText(img=frame,text=str(round(self.elapsed_time,3)),org=(50,370),fontFace=1,fontScale=1.5,color=(0,255,0),thickness=2)

            if self.is_locked == 0:
                cv2.putText(img=frame,text="KILITLENIYOR",org=(50,400),fontFace=1,fontScale=1.8,color=(0,255,0),thickness=2)
            if self.elapsed_time >= 4.0:
                cv2.putText(img=frame,text="KILITLENDI",org=(50,400),fontFace=1,fontScale=1.8,color=(0,255,0),thickness=2)
                kilitlenme_bilgisi=True
                self.is_locked=1

                #Kilitlenme gerçekleşti. Yönelim moduna geri dön.
                self.yönelim_modu=True
                self.yönelim_modundan_cikis_eventi.set()

        #fps = 1/(self.new_frame_time-self.prev_frame_time)
        #cv2.putText(img=frame,text="FPS:"+str(int(fps)),org=(50,50),fontFace=1,fontScale=1.8,color=(0,255,0),thickness=2)

        self.Server_udp.show(frame)

        try:
            if self.pwm_release==True:
                self.pwm_gönder(pwm_verileri)
        except Exception as e:
            print("PWM SERVER : PWM GÖNDERİLİRKEN HATA...")

        self.prev_frame_time=time.time()

        if self.is_locked == 1 and self.sent_once == 0:
            end_now = datetime.datetime.now()
            kilitlenme_bilgisi = {
                "kilitlenmeBaslangicZamani": {
                    "saat": self.start_now.hour,
                    "dakika": self.start_now.minute,
                    "saniye": self.start_now.second,
                    "milisaniye": self.start_now.microsecond #TODO düzeltilecek
                },
                "kilitlenmeBitisZamani": {
                    "saat": end_now.hour,
                    "dakika": end_now.minute,
                    "saniye": end_now.second,
                    "milisaniye": end_now.microsecond #TODO düzeltilecek
                },
                "otonom_kilitlenme": 0
            }
            print("KİLİTLENME BAŞARILI\nKİLİTLENME BAŞARILI\nKİLİTLENME BAŞARILI\nKİLİTLENME BAŞARILI\n")
            self.ana_sunucu.sunucuya_postala(json.dumps(kilitlenme_bilgisi))
            self.sent_once = 1

    async def routine(self,frame,lockedOrNot,pwm_verileri):
        task1 = asyncio.create_task(self.sunucu_saati)
        task2 = asyncio.create_task(self.kilitlenme_kontrol(frame,lockedOrNot,pwm_verileri))
        await task1
        await task2

    def kilitlenme_görevi(self):
        while True:

            if self.secilen_görev_modu != "kilitlenme":
                print("KILITLENME --> BEKLEME MODU")
                self.kilitlenme_release_event.wait()
                print("KILITLENME --> AKTIF")
                self.kilitlenme_release_event.clear()


            try:
                frame=self.görüntü_çek()
                frame = cv2.flip(frame,0)
                frame,lockedOrNot,pwm_verileri = self.Yolo_frame_işleme(frame)
                asyncio.run(self.kilitlenme_kontrol(frame,lockedOrNot,pwm_verileri))
            except Exception as e:
                print("KİLİTLENME GÖREVİ HATA : ",e) #TODO doldurulacak
                pass

    def kilitlenme_yönelim(self): #TODO YÖNELİM SUNUCUSUNDA BUG VAR.

        while True:

            if self.secilen_görev_modu != "kilitlenme":
                print("YONELİM/TAKIP --> BEKLEME MODU")
                self.yönelim_release_event.wait()
                print("YONELİM/TAKIP --> AKTIF")
                self.yönelim_release_event.clear()

            try:
                #bizim_telemetri=self.mavlink_obj.veri_kaydetme()
                #print("Telemetri:",bizim_telemetri)
                #rakip_telemetri=self.ana_sunucu.sunucuya_postala(bizim_telemetri)
                #yönelim_yapılacak_rakip= self.yönelim_obj.rakip_sec(rakip_telemetri,bizim_telemetri)
                yönelim_yapılacak_rakip = 0
            except Exception as e:
                print("YONELİM: TELEMETRİ ALINIRKEN HATA --> ",e)

            try:
                self.Server_yönelim.send_data_to_client(json.dumps(yönelim_yapılacak_rakip).encode())

            except Exception as e:
                print("YONELİM : VERİ GÖNDERİLİRKEN HATA --> ",e)
                print("YONELİM YENİDEN BAĞLANIYOR...")
                self.Server_yönelim.reconnect()

            time.sleep(0.1) #TODO GEÇİÇİ
            if self.yönelim_modu==False:
                print("YÖNELİM DEVRE DIŞI")
                self.pwm_release=True
                self.yönelim_modundan_cikis_eventi.wait()
                self.yönelim_modundan_cikis_eventi.clear()
                self.pwm_release=False


    # KAMİKAZE MODUNDA ÇALIŞACAK FONKSİYONLAR

    def kamikaze_gorevi(self):

        if self.secilen_görev_modu != "kamikaze":
            print("KAMIKAZE GOREVİ --> BEKLEME MODU")
            self.kamikaze_release_event.wait()
            print("KAMIKAZE GOREVİ --> AKTIF")
            self.kamikaze_release_event.clear()

        try:
            _, self.qr_coordinat = self.ana_sunucu.qr_koordinat_al()
        except Exception as e :
            print("KAMIKAZE : SUNUCUDAN QR-KONUM ALINIRKEN HATA -> ",e)
            #TODO EKLEME YAPILACAK
        try:
            self.Server_yönelim.send_data_to_client(json.dumps(self.qr_coordinat).encode())
            
        except:
            print("KAMIKAZE : QR-KONUM IHA'YA GONDERILIRKEN HATA -> ",e)
            #TODO EKLEME YAPILACAK

    def qr_kontrol(self):

        while True:
            if self.secilen_görev_modu != "kamikaze":
                print("QR KONTROL --> BEKLEME MODU")
                self.qr_release_event.wait()
                print("QR KONTROL --> AKTIF")
                self.qr_release_event.clear()

            self.new_frame_time=time.time()

            try:
                frame = self.görüntü_çek()
            except Exception as e:
                print("KAMIKAZE : FRAME RECV ERROR -> ", e)
            
            try:
                frame = cv2.flip(frame, 0)
                qr_text = self.qr_oku(frame)
                
                now = datetime.datetime.now() #TODO Düzeltilecek
                t = now.strftime("%H:%M:%S")
                cv2.putText(img=frame,text= "Sunucu saati: "+ t,org=(350,50),fontFace=1,fontScale=1.4,color=(0,255,0),thickness=2)
                #fps = 1/(self.new_frame_time-self.prev_frame_time)
                #cv2.putText(img=frame,text="FPS:"+str(int(fps)),org=(50,50),fontFace=1,fontScale=1.8,color=(0,255,0),thickness=2)

                self.Server_udp.show(frame)
                self.prev_frame_time=time.time()
                print(qr_text)
            except Exception as e:
                print("KAMIKAZE : QR ERROR -> ", e)            

    # ANA FONKSİYONLAR
            
    def sunuculari_oluştur(self):
        t1 = threading.Thread(target=self.Görüntü_sunucusu_oluştur)  # KİLİTLENME_GÖREVİ FONKSİYONUNDA KULLANILMIŞ
        t2 = threading.Thread(target=self.PWM_sunucusu_oluştur)
        t3 = threading.Thread(target=self.Yönelim_sunucusu_oluştur)  # YÖNELİM FONKSİYONUNDA KULLANILMIŞ
        t4 = threading.Thread(target=self.MAV_PROXY_sunucusu_oluştur)
        t5 = threading.Thread(target=self.Mod_sunucusu_oluştur)
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t5.start()
        return t1,t2,t3,t4,t5


    def ANA_GOREV_KONTROL(self): # ANA GÖREV KONTROL DEĞİŞECEK #TODO
        yer_istasyonu.Mod_sunucusu_oluştur()
        goruntu_thread, pwm_thread, yonelim_thread,mavproxy_thread,mod_thread = yer_istasyonu.sunuculari_oluştur()
        threads = {
                "goruntu"  : goruntu_thread,
                "pwm"      : pwm_thread,
                "yonelim"  : yonelim_thread,
                "mavproxy" : mavproxy_thread,
                "mod"      : mod_thread
        }

        kamikaze_görevi_thread = threading.Thread(target=self.kamikaze_gorevi)
        qr_görev_thread = threading.Thread(target=self.qr_kontrol)
        kilitlenme_görevi_thread = threading.Thread(target=self.kilitlenme_görevi)
        yönelim_thread = threading.Thread(target=self.kilitlenme_yönelim)

        #Bir kerelik başlangıç modunun alınması
        self.secilen_görev_modu = self.Server_mod.recv_tcp_message()
        kamikaze_görevi_thread.start()
        qr_görev_thread.start()
        kilitlenme_görevi_thread.start()
        yönelim_thread.start()


        while True:
            self.secilen_görev_modu = self.Server_mod.recv_tcp_message()

            if self.secilen_görev_modu == "kilitlenme":               
                self.kilitlenme_release_event.set()
                self.yönelim_release_event.set()

            if self.secilen_görev_modu == "kamikaze":
                self.kamikaze_release_event.set()
                self.qr_release_event.set()

            if self.secilen_görev_modu == "AUTO":
                pass

if __name__ == '__main__':

    yer_istasyonu = Yerİstasyonu("10.80.1.85") #<----- Burada mission planner bilgisayarının ip'si(string) verilecek. 10.0.0.240

    try:
        giris_kodu = yer_istasyonu.anasunucuya_baglan("algan", "53SnwjQ2sQ")
    except (ConnectionError , Exception) as e:
        print("Anasunucu veya Server oluşturma hatası: ", e)
        connection=False
        while not connection:
            giris_kodu = yer_istasyonu.anasunucuya_baglan("algan", "53SnwjQ2sQ")
            connection=True

    time.sleep(2)
    yer_istasyonu.senkron_local_saat()
    görev_kontrol = threading.Thread(target=yer_istasyonu.ANA_GOREV_KONTROL)

    görev_kontrol.start()
    görev_kontrol.join()
