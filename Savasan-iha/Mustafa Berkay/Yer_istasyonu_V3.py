import Server_Udp
import Server_Tcp
from path import Plane
import ana_sunucu_islemleri
import threading
import cv2
import yolov5_deploy
import json
import time,datetime
import asyncio



class Yerİstasyonu():

    def __init__(self):
        self.yolo_model = yolov5_deploy.Detection(capture_index=0,model_name=("D:\\Visual Code File Workspace\\ALGAN\\AlganYazilim\\Savasan-iha\\Mustafa Berkay\\bestuçak.pt"))
        self.ana_sunucuya_giris_durumu = False
        self.ana_sunucu = ana_sunucu_islemleri.sunucuApi("http://127.0.0.1:5000")

        self.Server_yönelim = Server_Tcp.Server(9002)
        self.Server_pwm = Server_Tcp.Server(9001)
        self.Server_udp = Server_Udp.Server()

        #PWM sinyal üretiminin senkronizasyonu için kullanılan objeler
        #self.lock= asyncio.Lock()
        self.pwm_event=asyncio.Event()

        #Görüntüye rakibin yakalanması durumunda mod değişikliği yapacak obje
        self.yönelim_modundan_cikis_eventi=threading.Event()
        self.yönelim_modu=True

        #Kilitlenme yapılırken kullanılan parametreler
        self.locked_prev=0
        self.is_locked=0
        self.sent_once=0
        self.elapsed_time=0
        self.start_time=0
        self.start_now:datetime.datetime = 0

        #Framerate Hesaplama parametreleri
        self.new_frame_time=0
        self.prev_frame_time=0

        #GÖREV_MODU SEÇİMİ #TODO-Daha yapılmadı. İHA'DAN ALINMASI GEREKİYOR.
        self.secilen_görev_modu="kilitlenme"

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
        connection=False
        while not connection:
            try:
                self.Server_udp.create_server()
                connection=True
            except (ConnectionError , Exception) as e:
                print("UDP SERVER oluşturma hatası: ", e)
            #    print("UDP SERVER'A 3 saniye içinden yeniden bağlanılıyor...\n")
            #   self.Server_udp.close_socket()
            #   self.Server_udp = Server_Udp.Server()
            #   self.Server_udp.create_server()

    def Yönelim_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                print("Yönelim sunucusu oluşturuluyor.")
                self.Server_yönelim.creat_server()
                connection=True
            except (ConnectionError, Exception) as e:
                print("YÖNELİM SERVER: oluştururken hata : ", e , " \n")
                print("YÖNELİM SERVER: yeniden bağlanılıyor...\n")
                connection_status=self.Server_yönelim.reconnect()
        return connection

    def PWM_sunucusu_oluştur(self):
        connection=False
        while not connection:
            try:
                self.Server_pwm.creat_server()
                connection=True
            except (ConnectionError, Exception) as e:
                print("PWM SERVER: oluştururken hata : ", e , " \n")
                print("PWM SERVER: yeniden bağlanılıyor...\n")
                self.Server_pwm.close_socket()
                self.Server_pwm = Server_Tcp.Server(9001)
                self.Server_pwm.creat_server()
        return connection

    def Yolo_frame_işleme(self,frame):
        
        "Gelen frame yolo modeline sokuluyor"
        results,frame=yer_istasyonu.yolo_model.get_results(frame)
        xCord, yCord, frame, lockedOrNot = yer_istasyonu.yolo_model.plot_boxes(results, frame)

        "Modelden gelen değerler ile pwm değeri hesaplanıyor"
        pwm_verileri=yer_istasyonu.yolo_model.coordinates_to_pwm(xCord,yCord)
        return frame,lockedOrNot,pwm_verileri

    def görüntü_çek(self):
        frame= self.Server_udp.recv_frame_from_client()
        return frame

    def mavlink_telemetri():
        pass

    def yönelim(self):
        while True:
            
            bizim_telemetri=self.mavlink_telemetri()
            rakip_telemetri=self.ana_sunucu.sunucuya_postala(bizim_telemetri)
            yönelim_verisi= 0
            "------------------------"
            "Yönelim için değerler gönderiliyor"
            "Buralar doldurulacak" #TODO
            "------------------------"
            try:
                self.Server_yönelim.send_data_to_client(json.dumps(yönelim_verisi).encode())
            except:
                print("ERROR : YONELİM VERİSİ GÖNDERİLİRKEN HATA")
                print("YONELİM YENİDEN BAĞLANIYOR--RETRY..2sec")
                connection=False
                while not connection:
                    connection=self.Yönelim_sunucusu_oluştur()
                    time.sleep(2) #TODO GEÇİÇİ
                
            print("YÖNELİM YAPILIYOR....")
            time.sleep(1) # TODO GEÇİÇİ
            if self.yönelim_modu==False:
                print("YÖNELİM DEVRE DIŞI")
                self.yönelim_modundan_cikis_eventi.wait()
                self.yönelim_modundan_cikis_eventi.clear()
        
    async def pwm_gönder(self,pwm_verileri):
        try:
            await self.pwm_event.wait()
            self.Server_pwm.send_data_to_client(json.dumps(pwm_verileri).encode())
        except Exception as e:
            print("PWM SUNUCU HATASI : ",e)
            print("PWM SUNUCUSUNA TEKRAR BAGLANIYOR...")
            self.PWM_sunucusu_oluştur()
            asyncio.sleep(1)

    async def kilitlenme_kontrol(self,frame,lockedOrNot):
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
            self.locked_prev=0
            self.is_locked=0
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
                print("KİLİTLENME BAŞARILI")
                kilitlenme_bilgisi=True
                self.is_locked=1
                
                #Kilitlenme gerçekleşti. Yönelim moduna geri dön.
                self.yönelim_modu=True
                self.yönelim_modundan_cikis_eventi.set()

        self.pwm_event.set()
        fps = 1/(self.new_frame_time-self.prev_frame_time)
        cv2.putText(img=frame,text="FPS:"+str(int(fps)),org=(50,50),fontFace=1,fontScale=1.8,color=(0,255,0),thickness=2)
        self.Server_udp.show(frame)
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
                self.ana_sunucu.sunucuya_postala(json.dumps(kilitlenme_bilgisi))
                self.sent_once = 1

    async def coroutine(self,frame,lockedOrNot,pwm_verileri):

        task1= asyncio.create_task(self.kilitlenme_kontrol(frame,lockedOrNot))
        await task1
        task2= asyncio.create_task(self.pwm_gönder(pwm_verileri))
        await task2

    def kilitlenme_görevi(self):
        while True:
           frame=self.görüntü_çek()
           frame = cv2.flip(frame,0)
           frame,lockedOrNot,pwm_verileri = self.Yolo_frame_işleme(frame)
           asyncio.run(self.coroutine(frame,lockedOrNot,pwm_verileri))

    def GOREV_KONTROL(self):
        
        if self.secilen_görev_modu == "kilitlenme":
                Yönelim_threadi = threading.Thread(target= yer_istasyonu.yönelim)
                kilitlenme_görevi_thread = threading.Thread(target=self.kilitlenme_görevi)
                kilitlenme_görevi_thread.start()
                Yönelim_threadi.start()

        if self.secilen_görev_modu == "Kamikaze":
            pass
        


if __name__ == '__main__':

    yer_istasyonu = Yerİstasyonu()

    try:
        "Ana Sunucuya giriş yapıyor."
        giris_kodu = yer_istasyonu.anasunucuya_baglan("algan", "53SnwjQ2sQ")
    except (ConnectionError , Exception) as e:
        print("Anasunucu veya Server oluşturma hatası: ", e)
        connection=False
        while not connection:
            giris_kodu = yer_istasyonu.anasunucuya_baglan("algan", "53SnwjQ2sQ")
            connection=True

    yer_istasyonu.Görüntü_sunucusu_oluştur()
    yer_istasyonu.Yönelim_sunucusu_oluştur()
    yer_istasyonu.PWM_sunucusu_oluştur()        #DEBUG TODO Burada PWM sunucusu bir şekilde kodu kilitliyor. Bu nedenle PWM SUNUCUSU gelmeden diğer sunuculardan veri alamıyorum.
                                                #Sorunun kaynağı, PWM sunucusunun iha_test.py kodunun içinde olması olabilir.
 
    görev_kontrol = threading.Thread(target=yer_istasyonu.GOREV_KONTROL)

    görev_kontrol.start()
    görev_kontrol.join()
    