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

        self.Server_tcp_pwm = Server_Tcp.Server(9001)
        self.Server_udp = Server_Udp.Server()
        #self.lock= asyncio.Lock()
        self.pwm_event=asyncio.Event()

        self.locked_prev=0
        self.is_locked=0
        self.sent_once=0
        self.elapsed_time=0
        self.start_time=0
        self.start_now:datetime.datetime = 0

    "Ana Sunucuya Bağlanma Fonksiyonu"
    def connect_to_anasunucu(self, kullanici_adi, sifre):
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
                print("UDP SERVER'A 3 saniye içinden yeniden bağlanılıyor...\n")
                self.Server_udp.close_socket()
                self.Server_udp = Server_Udp.Server()
                self.Server_udp.create_server()
                
    def PWM_sunucusu_oluştur(self):
        connection=False
        while not connection:
            try:
                self.Server_tcp_pwm.creat_server()
                connection=True
            except (ConnectionError, Exception) as e:
                print("PWM SERVER oluştururken hata : ", e , " \n")
                print("3 saniye içinden yeniden bağlanılıyor...\n")
                self.Server_tcp_pwm.close_socket()
                self.Server_tcp_pwm = Server_Tcp.Server(9001)
                self.Server_tcp_pwm.creat_server()

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
    
    async def pwm_gönder(self,pwm_verileri):
        try:
            await self.pwm_event.wait()
            self.Server_tcp_pwm.send_data_to_client(json.dumps(pwm_verileri).encode())
        except Exception as e:
            print("PWM SUNUCU HATASI : ",e)
            print("PWM SUNUCUSUNA TEKRAR BAGLANIYOR...")
            self.PWM_sunucusu_oluştur()
            asyncio.sleep(1)


    async def kilitlenme_kontrol(self,frame,lockedOrNot):

        "Rakip kilitlenme"        
        if lockedOrNot == 1 and self.locked_prev== 0:
            self.start_time=time.time()
            
            self.start_now =datetime.datetime.now()
            cv2.putText(img=frame,text="HEDEF GORULDU",org=(50,400),fontFace=1,fontScale=2,color=(0,255,0),thickness=2)
            self.locked_prev=1

        if lockedOrNot == 0 and self.locked_prev== 1:
            cv2.putText(img=frame,text="HEDEF KAYBOLDU",org=(50,400),fontFace=1,fontScale=2,color=(0,255,0),thickness=2)
            self.locked_prev=0
            self.is_locked=0
            self.sent_once = 0

        if lockedOrNot == 1 and self.locked_prev== 1:
            self.elapsed_time= time.time()- self.start_time
            cv2.putText(img=frame,text=str(round(self.elapsed_time,3)),org=(50,370),fontFace=1,fontScale=1.5,color=(0,255,0),thickness=2)
            
            if self.is_locked == 0:
                cv2.putText(img=frame,text="KILITLENIYOR",org=(50,400),fontFace=1,fontScale=1.8,color=(0,255,0),thickness=2)
            if self.elapsed_time >= 4.0:
                cv2.putText(img=frame,text="KILITLENDI",org=(50,400),fontFace=1,fontScale=1.8,color=(0,255,0),thickness=2)
                kilitlenme_bilgisi=True
                self.is_locked=1
        self.pwm_event.set()
        self.Server_udp.show(frame)

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

    def kilitlenme_ve_pwm_üretimi(self):

        while True:
            frame=self.görüntü_çek()
            frame = cv2.flip(frame,0)
            frame,lockedOrNot,pwm_verileri = self.Yolo_frame_işleme(frame)
        
            asyncio.run(self.coroutine(frame,lockedOrNot,pwm_verileri))

if __name__ == '__main__':

    yer_istasyonu = Yerİstasyonu()

    try:
        "Ana Sunucuya giriş yapıyor."
        giris_kodu = yer_istasyonu.connect_to_anasunucu("algan", "53SnwjQ2sQ")
    except (ConnectionError , Exception) as e:
        print("Anasunucu veya Server oluşturma hatası: ", e)

        #Eğer Bağlantı hatası olursa While içinde tekrar bağlanmayı deneyecek
        connection=False
        while not connection:
            giris_kodu = yer_istasyonu.connect_to_anasunucu("algan", "53SnwjQ2sQ")
            connection=True

    yer_istasyonu.Görüntü_sunucusu_oluştur()
    yer_istasyonu.PWM_sunucusu_oluştur()

    #PWM_thread = threading.Thread(target= yer_istasyonu.)
    Udp_thread = threading.Thread(target= yer_istasyonu.kilitlenme_ve_pwm_üretimi )

    Udp_thread.start()
    #Udp_thread.start()