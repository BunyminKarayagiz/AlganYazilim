import Server_Udp
import Server_Tcp
from path import Plane
import ana_sunucu_islemleri
import threading
import cv2
import yolov5_deploy
import json
import time,datetime
import os


class Yerİstasyonu():

    def __init__(self):
        self.yolo_model = yolov5_deploy.Detection(capture_index=0,model_name=("D:\\Visual Code File Workspace\\ALGAN\\AlganYazilim\\Savasan-iha\\Mustafa Berkay\\bestuçak.pt"))
        self.ana_sunucuya_giris_durumu = False
        self.ana_sunucu = ana_sunucu_islemleri.sunucuApi("http://127.0.0.1:5000")

        self.Server_tcp_json = Server_Tcp.Server(9000)
        self.Server_tcp_pwm = Server_Tcp.Server(9001)
        self.Server_udp = Server_Udp.Server()

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


    def TCP_connection_handler(self,function):
    
        try:
            self.Server_tcp_json.creat_server()
        except (ConnectionError, Exception) as e:
            print("JSON SERVER oluşturma hatası: ", e)
            connection=False
            while not connection:
                self.Server_tcp_json.creat_server()
                connection=True
   
        while True:
            data = self.Server_tcp_json.recv_tcp_message()
            function(data)

    def yolo_frame_func(self,frame):
        
        "Gelen frame yolo modeline sokuluyor"
        results,frame=yer_istasyonu.yolo_model.get_results(frame)
        xCord, yCord, frame, lockedOrNot = yer_istasyonu.yolo_model.plot_boxes(results, frame)

        "Modelden gelen değerler ile pwm değeri hesaplanıyor"
        pwm_verileri=yer_istasyonu.yolo_model.coordinates_to_pwm(xCord,yCord)

        return frame,lockedOrNot,pwm_verileri

    def UDP_connection_handler(self):
        
        try:
            self.Server_udp.create_server()
        except (ConnectionError , Exception) as e:
            print("UDP SERVER oluşturma hatası: ", e)
            connection=False
            while not connection:
                self.Server_udp.create_server()
                connection=True

        try:
            self.Server_tcp_pwm.creat_server()
        except (ConnectionError, Exception) as e:
            print("PWM SERVER oluşturma hatası: ", e)
            connection=False
            while not connection:
                self.Server_tcp_pwm.creat_server()
                connection=True


        locked_prev=0
        is_locked=0
        sent_once=0

        while True:
            frame= self.Server_udp.recv_frame_from_client()
            frame,lockedOrNot,pwm_verileri = self.yolo_frame_func(frame)

            "Rakip kilitlenme"
            if lockedOrNot == 1 and locked_prev== 0:
                start_time=time.time()
                start_now =datetime.datetime.now()
                cv2.putText(img=frame,text="ENEMY ON SIGHT",org=(50,450),fontFace=1,fontScale=1,color=(0,255,0),thickness=1)
                locked_prev=1

            if lockedOrNot == 0 and locked_prev== 1:
                cv2.putText(img=frame,text="ENEMY LOST",org=(50,450),fontFace=1,fontScale=1,color=(0,255,0),thickness=1)
                locked_prev=0
                is_locked=0
                sent_once = 0

            if lockedOrNot == 1 and locked_prev== 1:
                elapsed_time= time.time()-start_time
                cv2.putText(img=frame,text=str(round(elapsed_time,3)),org=(50,400),fontFace=1,fontScale=1,color=(0,255,0),thickness=1)
                
                if is_locked == 0:
                    cv2.putText(img=frame,text="LOCKING",org=(50,450),fontFace=1,fontScale=1,color=(0,255,0),thickness=1)

                if elapsed_time >= 4.0:
                    cv2.putText(img=frame,text="LOCKED",org=(50,450),fontFace=1,fontScale=1,color=(0,255,0),thickness=1)
                    kilitlenme_bilgisi=True
                    is_locked=1
                
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

                    self.ana_sunucu.sunucuya_postala(json.dumps(kilitlenme_bilgisi))
                    sent_once = 1

            "Pwm değerleri İha'ya gönderiliyor."
            try:
                self.Server_tcp_pwm.send_data_to_client(json.dumps(pwm_verileri).encode("utf-8"))  
            except Exception as e:
                print(e)
                
            self.Server_udp.show(frame)
    

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

    Tcp_thread = threading.Thread(target= yer_istasyonu.TCP_connection_handler ,args=( yer_istasyonu.ana_sunucu.sunucuya_postala,))
    Udp_thread = threading.Thread(target= yer_istasyonu.UDP_connection_handler )

    Tcp_thread.start()
    Udp_thread.start()