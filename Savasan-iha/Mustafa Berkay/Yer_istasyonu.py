import Server_Udp_yeni
import Server_Tcp_yeni
from path import Plane
import ana_sunucu_islemleri
import threading
import cv2
import yolov5_deploy
import json
import time


class Yerİstasyonu():

    def __init__(self):
        self.yolo_model = yolov5_deploy.Detection(capture_index=0,model_name="bestuçak.pt")
        self.ana_sunucuya_giris_durumu = False
        self.ana_sunucu = ana_sunucu_islemleri.sunucuApi("http://127.0.0.1:5000")

        self.Server_tcp = Server_Tcp_yeni.Server()

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
            self.Server_tcp.creat_server()
        except (ConnectionError, Exception) as e:
            print("Anasunucu veya Server oluşturma hatası: ", e)
            connection=False
            while not connection:
                self.Server_tcp.creat_server()
                connection=True
        
        while True:
            data = self.Server_tcp.recv_tcp_message()
            function(data)

    def yolov5_frame(self,frame):
        
        "Gelen frame yolo modeline sokuluyor"
        results,frame=yer_istasyonu.yolo_model.get_results(frame)
        xCord, yCord, frame, lockedOrNot = yer_istasyonu.yolo_model.plot_boxes(results, frame)

        "Modelden gelen değerler ile pwm değeri hesaplanıyor"
        pwm_verileri=yer_istasyonu.yolo_model.coordinates_to_pwm(xCord,yCord)

        return frame,lockedOrNot,pwm_verileri

    def UDP_connection_handler(self):
        Server_udp = Server_Udp_yeni.Server()

        try:
            Server_udp.create_server()
        except (ConnectionError , Exception) as e:
            print("Anasunucu veya Server oluşturma hatası: ", e)
            connection=False
            while not connection:
                Server_udp.create_server()
                connection=True
                
        kilitlenme_bilgisi=False
        locked_prev=0
        is_locked=0
        sent_once=0
        
        while True:
            frame= Server_udp.recv_frame_from_client()
            frame,lockedOrNot,pwm_verileri = self.yolov5_frame(frame)

            "Rakip kilitlenme"
            if lockedOrNot == 1 and locked_prev== 0:
                start_time=time.time()
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
                    self.ana_sunucu.sunucuya_postala(kilitlenme_bilgisi)
                    sent_once = 1

                

            "Pwm değerleri İha'ya gönderiliyor." #TODO
            #self.Server_tcp.send_data_to_client(pwm_verileri.encode())

            Server_udp.show(frame)
    

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

