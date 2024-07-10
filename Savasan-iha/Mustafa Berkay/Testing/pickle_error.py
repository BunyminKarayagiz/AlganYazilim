import multiprocessing as mp
import time
import Server_Udp
import Server_Tcp
import hesaplamalar
import mavproxy2
import asyncio
import threading
from qr_detection import QR_Detection

class test():
    def __init__(self,queue_size = 1) -> None:    
        self.Server_udp = Server_Udp.Server()
        self.görüntü_sunucusu = False

        self.capture_queue = mp.Queue(maxsize=queue_size)
        self.display_queue = mp.Queue(maxsize=queue_size)
        self.event_queue_1 = mp.Queue()
        self.event_1 = mp.Event()
        self.event_queue_2 = mp.Queue()
        self.event_2 = mp.Event()

        self.qr = QR_Detection()

    def Görüntü_sunucusu_oluştur(self):
        self.Server_udp = Server_Udp.Server()
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
        self.görüntü_sunucusu = connection_status
        return connection_status
    
    def start(self):
        p1 = mp.Process(target=self.process)
        p1 .start()
        p1.join()

    def process(self):
        print(mp.current_process().name)
        self.Görüntü_sunucusu_oluştur()

if __name__ == "__main__":
    test_obj = test(1)
    test_obj.start()