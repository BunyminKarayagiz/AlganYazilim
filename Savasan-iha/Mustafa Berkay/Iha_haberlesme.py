import socket
import Client_Tcp , Client_Udp
import threading
import ipConfig

class iha_haberlesme():
    def __init__(self,host_ip) -> None:
        #host_ip, raspberry'nin kendisi oluyor.

        #UDP-1 bağlantı ayarları
        self.udp_host = host_ip
        self.udp_port = 9999  #Şimdilik elle seçiliyor.Port kapatılamaz ise devamında enumerator kullanılabilir.
        self.capture_obj=Client_Udp.Client(self.udp_host,self.udp_port)

    def send_video(self):
        while True:
            self.capture_obj.send_video()
            print("FRAME SENT..")

    def hedef(self):
        pass


if __name__ == "__main__":

    iha_obj=iha_haberlesme("10.80.1.85")
    
    video_thread = threading.Thread(target=iha_obj.send_video)
    video_thread.start()
    video_thread.join()
