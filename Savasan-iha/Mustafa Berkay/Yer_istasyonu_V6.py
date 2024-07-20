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


# KOD ÇALIŞTIRMA SIRASI: sunucuapi -> Yer_istasyonu_v6 -> Iha_test(PUTTY) -> Iha_haberlesme(PUTTY)
class Yerİstasyonu():

    def __init__(self, mavlink_ip):  # TODO HER BİLGİSAYAR İÇİN PATH DÜZENLENMELİ
        self.yolo_model = YOLOv8_deploy.Detection("D:\Visual Code File Workspace\ALGAN\AlganYazilim\Savasan-iha\Mustafa Berkay\Model2024_V1.pt")
        self.ana_sunucuya_giris_durumu = False
        self.ana_sunucu = ana_sunucu_islemleri.sunucuApi("http://127.0.0.1:5000")

        self.Server_yönelim = Server_Tcp.Server(9002, name="YÖNELİM")
        self.Server_pwm = Server_Tcp.Server(9001, name="PWM")
        self.Server_udp = Server_Udp.Server()
        self.Server_mod = Server_Tcp.Server(9003, name="MOD")

        # Sunucu durumları için kullanılacak değişkenler
        self.görüntü_sunucusu = False
        self.Yönelim_sunucusu = False
        self.Mod_sunucusu = False
        self.PWM_sunucusu = False
        self.MAV_PROXY_sunucusu = False

        # YÖNELİM yapılacak uçağın seçilmesi için kullanılacak obje
        self.yönelim_obj = hesaplamalar.Hesaplamalar()

        # M.PLANNER bilgisayarından telemetri verisi çekmek için kullanılacak obje
        self.mavlink_obj = mavproxy2.MAVLink(mavlink_ip)

        # PWM sinyal üretiminin senkronizasyonu için kullanılan objeler
        # self.lock= asyncio.Lock()
        self.pwm_event = asyncio.Event()
        self.pwm_release = False

        # Görüntüye rakibin yakalanması durumunda mod değişikliği yapacak obje
        self.yönelim_modundan_cikis_eventi = threading.Event()
        self.yönelim_modu = True

        # Kilitlenme yapılırken kullanılan parametreler
        self.locked_prev = 0
        self.is_locked = 0
        self.sent_once = 0
        self.elapsed_time = 0
        self.start_time = 0
        self.start_now: datetime.datetime = 0

        # Kamikaze yapılırken kullanılan parametreler
        self.qr_coordinat = ""
        self.fark = 0
        # Framerate Hesaplama parametreleri
        self.new_frame_time = 0
        self.prev_frame_time = 0

        # GÖREV_MODU SEÇİMİ #TODO-Daha yapılmadı. İHA VEYA MİSSİON PLANNER BİLGİSAYARINDAN ALINMASI GEREKİYOR.
        self.secilen_görev_modu = "kilitlenme"

        self.frame = 0
        self.TCP_ONAYLAMA_KODU = "ALGAN"
        self.sunucu_saati: str = ""

    # SUNUCU FONKSİYONLARI
    def senkron_local_saat(self):
        status_code, sunuc_saati = self.ana_sunucu.sunucu_saati_al()
        local_saat = datetime.datetime.today()
        sunuc_saati = json.loads(sunuc_saati)
        sunucu_saat, sunucu_dakika, sunucu_saniye, sunucu_milisaniye = sunuc_saati["saat"], sunuc_saati["dakika"], \
        sunuc_saati["saniye"], sunuc_saati["milisaniye"]
        sunucu_saati = datetime.datetime(year=local_saat.year,
                                         month=local_saat.month,
                                         day=local_saat.day,
                                         hour=sunucu_saat,
                                         minute=sunucu_dakika,
                                         second=sunucu_saniye,
                                         microsecond=sunucu_milisaniye)
        self.fark = abs(local_saat - sunucu_saati)
        print("Sunucu Saati: ", self.fark)

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
        connection_status = False
        while not connection_status:
            try:
                self.Server_udp.create_server()
                connection_status = True
                print("UDP : SERVER OLUŞTURULDU")
            except (ConnectionError, Exception) as e:
                print("UDP SERVER: oluştururken hata : ", e)
            #    print("UDP SERVER'A 3 saniye içinden yeniden bağlanılıyor...\n")
            #   self.Server_udp.close_socket()
            #   self.Server_udp = Server_Udp.Server()
            #   self.Server_udp.create_server() #TODO DÜZENLEME GELEBİLİR

        self.görüntü_sunucusu = connection_status
        return connection_status

    def Yönelim_sunucusu_oluştur(self):
        connection_status = False
        while not connection_status:
            try:
                self.Server_yönelim.creat_server()
                connection_status = True
                print("YONELİM : SERVER OLUŞTURULDU")
            except (ConnectionError, Exception) as e:
                print("YÖNELİM SERVER: oluştururken hata : ", e, " \n")
                print("YÖNELİM SERVER: yeniden bağlanılıyor...\n")
                connection_status = self.Server_yönelim.reconnect()
                print("YONELİM : SERVER OLUŞTURULDU.")

        self.Yönelim_sunucusu = connection_status

    def PWM_sunucusu_oluştur(self):
        connection_status = False
        while not connection_status:
            try:
                self.Server_pwm.creat_server()
                connection_status = True
                print("PWM : SERVER OLUŞTURULDU\n")
            except (ConnectionError, Exception) as e:
                print("PWM SERVER: oluştururken hata : ", e, " \n")
                print("PWM SERVER: yeniden bağlanılıyor...\n")
                self.Server_pwm.reconnect()
                print("PWM : SERVER OLUŞTURULDU\n")

        self.Yönelim_sunucusu = connection_status
        return connection_status

    def Mod_sunucusu_oluştur(self):
        connection_status = False
        while not connection_status:
            try:
                self.Server_mod.creat_server()
                connection_status = True
                print("MOD : SERVER OLUŞTURULDU\n")
            except (ConnectionError, Exception) as e:
                print("MOD SERVER: oluştururken hata : ", e, " \n")
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
                print("MAVLINK SERVER: oluştururken hata : ", e, " \n")
                print("MAVLINK SERVER: yeniden bağlanılıyor...\n")
                connection_status = self.mavlink_obj.connect()
        self.MAV_PROXY_sunucusu = connection_status
        return connection_status

    # Frame işleyen fonksiyonlar

    def Yolo_frame_işleme(self, frame):

        "Gelen frame yolo modeline sokuluyor"
        pwm_verileri, frame ,lockedOrNot = self.yolo_model.model_predict(frame)
        # results,frame=yer_istasyonu.yolo_model.get_results(frame)
        return frame, lockedOrNot, pwm_verileri

    def qr_oku(self, frame):
        x1, x2, y1, y2 = int(frame.shape[1] * 0.25), int(frame.shape[1] * 0.75) , int(frame.shape[0] * 0.10), int(frame.shape[0] * 0.90)  # Gelen videoya dikdörtgen çizmek için koordinat almaktadır
        roi = frame[y1:y2,x1:x2]  # Roi değişkeni orijinal resim içine çizilen dörtgenin arasındaki görüntüyü alır.
        # qr_code_list = pyzbar.decode(roi)
        qr_code_list = pyzbar.decode(frame)  # 640x480 için
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Gelen videoya dikdörtgen çizmektedir

        for qr_code in qr_code_list:
            data = qr_code.data.decode("utf-8")
            print(data)
            pts = np.array([qr_code.polygon], np.int32)
            pts = pts.reshape((-1, 1, 2))
            # cv2.polylines(roi, [pts], True, (255, 0, 255), 5)
            cv2.polylines(frame, [pts], True, (255, 0, 255), 5)
            pts2 = qr_code.rect

            cv2.putText(frame, data, (pts2[0], pts2[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 255), 2)
            # cv2.putText(roi, data, (pts2[0], pts2[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 255), 2)

            if data != None:
                x1, x2, y1, y2 = int(frame.shape[1] * 0.25), int(frame.shape[1] * 0.75) , int(frame.shape[0] * 0.10), int(frame.shape[0] * 0.90)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            return qr_code.data, frame

        return None, frame

    def görüntü_çek(self):
        try:
            frame = self.Server_udp.recv_frame_from_client()
            return frame
        except:
            print("UDP: GÖRÜNTÜ ALINIRKEN HATA..")

    # KİLİTLENME MODUNDA ÇALIŞACAK FONKSİYONLAR

    def yönelim(self):  # TODO YÖNELİM SUNUCUSUNDA BUG VAR.
        self.Yönelim_sunucusu_oluştur()

        while True:
            try:
                # bizim_telemetri=self.mavlink_obj.veri_kaydetme()
                # print("Telemetri:",bizim_telemetri)
                # rakip_telemetri=self.ana_sunucu.sunucuya_postala(bizim_telemetri)
                # yönelim_yapılacak_rakip= self.yönelim_obj.rakip_sec(rakip_telemetri,bizim_telemetri)
                yönelim_yapılacak_rakip = 0
            except Exception as e:
                print("YONELİM: TELEMETRİ ALINIRKEN HATA --> ", e)

            try:
                self.Server_yönelim.send_data_to_client(json.dumps(yönelim_yapılacak_rakip).encode())

            except Exception as e:
                print("YONELİM : VERİ GÖNDERİLİRKEN HATA --> ", e)
                print("YONELİM YENİDEN BAĞLANIYOR...")
                self.Server_yönelim.reconnect()

            time.sleep(0.2)  # TODO GEÇİÇİ
            if self.yönelim_modu == False:
                print("YÖNELİM DEVRE DIŞI")
                self.pwm_release = True
                self.yönelim_modundan_cikis_eventi.wait()
                self.yönelim_modundan_cikis_eventi.clear()
                self.pwm_release = False

    def pwm_gönder(self, pwm_verileri):
        try:
            self.Server_pwm.send_data_to_client(json.dumps(pwm_verileri).encode())
        except Exception as e:
            print("PWM SUNUCU HATASI : ", e)
            print("PWM SUNUCUSUNA TEKRAR BAGLANIYOR...")
            self.Server_pwm.reconnect()

    async def sunucu_saati(self):
        sunucu_kod, sunucu_saat = self.ana_sunucu.sunucu_saati_al()
        if (sunucu_kod == 200):
            self.sunucu_saati = sunucu_saat

    async def kilitlenme_kontrol(self, frame, lockedOrNot, pwm_verileri):

        self.new_frame_time = time.time()

        "Rakip kilitlenme"
        if lockedOrNot == 1 and self.locked_prev == 0:
            self.start_time = time.time()
            self.start_now = datetime.datetime.now()
            cv2.putText(img=frame, text="HEDEF GORULDU", org=(50, 400), fontFace=1, fontScale=2, color=(0, 255, 0),
                        thickness=2)
            self.locked_prev = 1

            # Hedef Görüldü. Yönelim modu devre dışı.
            self.yönelim_modu = False

        if lockedOrNot == 0 and self.locked_prev == 1:
            cv2.putText(img=frame, text="HEDEF KAYBOLDU", org=(50, 400), fontFace=1, fontScale=2, color=(0, 255, 0),
                        thickness=2)
            self.locked_prev = 0
            self.is_locked = 0
            self.sent_once = 0

            # Hedef kayboldu. Yönelim Moduna geri dön.
            self.yönelim_modu = True
            self.yönelim_modundan_cikis_eventi.set()

        if lockedOrNot == 1 and self.locked_prev == 1:
            self.elapsed_time = time.time() - self.start_time
            cv2.putText(img=frame, text=str(round(self.elapsed_time, 3)), org=(50, 370), fontFace=1, fontScale=1.5,
                        color=(0, 255, 0), thickness=2)

            if self.is_locked == 0:
                cv2.putText(img=frame, text="KILITLENIYOR", org=(50, 400), fontFace=1, fontScale=1.8, color=(0, 255, 0),
                            thickness=2)
            if self.elapsed_time >= 4.0:
                cv2.putText(img=frame, text="KILITLENDI", org=(50, 400), fontFace=1, fontScale=1.8, color=(0, 255, 0),
                            thickness=2)
                kilitlenme_bilgisi = True
                self.is_locked = 1

                # Kilitlenme gerçekleşti. Yönelim moduna geri dön.
                self.yönelim_modu = True
                self.yönelim_modundan_cikis_eventi.set()

        fps = 1/(self.new_frame_time-self.prev_frame_time)
        cv2.putText(img=frame,text="FPS:"+str(int(fps)),org=(50,50),fontFace=1,fontScale=1.8,color=(0,255,0),thickness=2)
        self.Server_udp.show(frame)

        try:
            if self.pwm_release == True:
                self.pwm_gönder(pwm_verileri)
        except Exception as e:
            print("PWM SERVER : PWM GÖNDERİLİRKEN HATA...")

        self.prev_frame_time = time.time()

        if self.is_locked == 1 and self.sent_once == 0:
            end_now = datetime.datetime.now()
            kilitlenme_bilgisi = {
                "kilitlenmeBaslangicZamani": {
                    "saat": self.start_now.hour,
                    "dakika": self.start_now.minute,
                    "saniye": self.start_now.second,
                    "milisaniye": self.start_now.microsecond  # TODO düzeltilecek
                },
                "kilitlenmeBitisZamani": {
                    "saat": end_now.hour,
                    "dakika": end_now.minute,
                    "saniye": end_now.second,
                    "milisaniye": end_now.microsecond  # TODO düzeltilecek
                },
                "otonom_kilitlenme": 0
            }
            print("KİLİTLENME BAŞARILI\nKİLİTLENME BAŞARILI\nKİLİTLENME BAŞARILI\nKİLİTLENME BAŞARILI\n")
            self.ana_sunucu.sunucuya_postala(json.dumps(kilitlenme_bilgisi))
            self.sent_once = 1

    async def routine(self, frame, lockedOrNot, pwm_verileri):
        task1 = asyncio.create_task(self.sunucu_saati)
        task2 = asyncio.create_task(self.kilitlenme_kontrol(frame, lockedOrNot, pwm_verileri))
        await task1
        await task2

    def kilitlenme_görevi(self):
        self.Görüntü_sunucusu_oluştur()
        while True:
            try:
                frame = self.görüntü_çek()
                frame = cv2.flip(frame, 0)
                frame, lockedOrNot, pwm_verileri = self.Yolo_frame_işleme(frame)
                asyncio.run(self.kilitlenme_kontrol(frame, lockedOrNot, pwm_verileri))
            except Exception as e:
                print("KİLİTLENME GÖREVİ HATA : ", e)  # TODO doldurulacak
                pass

    # KAMİKAZE MODUNDA ÇALIŞACAK FONKSİYONLAR
    "------------------------------------"

    def kamikaze_gorevi(self):
        _, self.qr_coordinat = self.ana_sunucu.qr_koordinat_al()
        self.Server_yönelim.send_data_to_client(json.dumps(self.qr_coordinat).encode())
        while True:
            try:
                frame = self.görüntü_çek()
                frame = cv2.flip(frame, 0)
                qr_text, frame = self.qr_oku(frame)
                frame = cv2.putText(frame, str(self.fark), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            except Exception as e:
                print("Kamikaze Görev Hata", e)

    def qr_kontrol(self):
        pass

    "------------------------------------"

    def sunuculari_oluştur(self, mod):
        if mod == "kilitlenme":
            t1 = threading.Thread(target=self.Görüntü_sunucusu_oluştur)  # KİLİTLENME_GÖREVİ FONKSİYONUNDA KULLANILMIŞ
            t2 = threading.Thread(target=self.PWM_sunucusu_oluştur)
            t3 = threading.Thread(target=self.Yönelim_sunucusu_oluştur)  # YÖNELİM FONKSİYONUNDA KULLANILMIŞ
            t4 = threading.Thread(target=self.MAV_PROXY_sunucusu_oluştur)
            t5 = threading.Thread(target=self.Mod_sunucusu_oluştur)
            # t1.start()
            t2.start()
            # t3.start()
            # t4.start()
            # t5.start()
            return t2
        
        if mod == "kamikaze":
            t1 = threading.Thread(target=self.Görüntü_sunucusu_oluştur)  # KİLİTLENME_GÖREVİ FONKSİYONUNDA KULLANILMIŞ
            t2 = threading.Thread(target=self.PWM_sunucusu_oluştur)
            t3 = threading.Thread(target=self.Yönelim_sunucusu_oluştur)  # YÖNELİM FONKSİYONUNDA KULLANILMIŞ
            t4 = threading.Thread(target=self.MAV_PROXY_sunucusu_oluştur)
            t5 = threading.Thread(target=self.Mod_sunucusu_oluştur)
            t1.start()
            # t2.start()
            t3.start()
            # t4.start()  Sonradan Açılacak
            # t5.start()
            return t1, t3

    def ANA_GOREV_KONTROL(self):  # ANA GÖREV KONTROL DEĞİŞECEK #TODO
        threads = {}
        yer_istasyonu.Mod_sunucusu_oluştur()
        self.secilen_görev_modu = self.Server_mod.recv_tcp_message()

        if self.secilen_görev_modu == "kilitlenme":
            pwm_thread = self.sunuculari_oluştur(self.secilen_görev_modu)

            Yönelim_threadi = threading.Thread(target=self.yönelim)
            kilitlenme_görevi_thread = threading.Thread(target=self.kilitlenme_görevi)
            kilitlenme_görevi_thread.start()
            Yönelim_threadi.start()

        if self.secilen_görev_modu == "kamikaze":
            goruntu_cek, qr_yonelim = self.sunuculari_oluştur(self.secilen_görev_modu)
            kamikaze_gorev_thread = threading.Thread(target=self.kamikaze_gorevi)
            kamikaze_gorev_thread.start()

        if self.secilen_görev_modu == "AUTO":
            pass


if __name__ == '__main__':

    yer_istasyonu = Yerİstasyonu("10.80.1.72")  # <----- Burada mission planner bilgisayarının ip'si(string) verilecek. 10.0.0.240

    try:
        "Ana Sunucuya giriş yapıyor."
        giris_kodu = yer_istasyonu.anasunucuya_baglan("algan", "53SnwjQ2sQ")
    except (ConnectionError, Exception) as e:
        print("Anasunucu veya Server oluşturma hatası: ", e)
        connection = False
        while not connection:
            giris_kodu = yer_istasyonu.anasunucuya_baglan("algan", "53SnwjQ2sQ")
            connection = True

    time.sleep(2)
    yer_istasyonu.senkron_local_saat()
    görev_kontrol = threading.Thread(target=yer_istasyonu.ANA_GOREV_KONTROL)

    görev_kontrol.start()
    görev_kontrol.join()
