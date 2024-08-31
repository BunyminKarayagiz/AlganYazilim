import socket
from colorama import Fore, init
from prediction_algorithm_try import KalmanFilter
import time

#! HSS verilerinin çekildiği bölüm
class StatusReceiver:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 65432
        init(autoreset=True)

    def receive_status(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(Fore.GREEN + "Hava Savunma Sisteminden Mesaj Bekleniyor...")
            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"Bağlanti kuruldu: {addr}")
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        status = data.decode('utf-8').split(',')[0]
                        if status == "active":
                            print(Fore.GREEN + "Hava savunma sistemi aktiftir.")
                        elif status == "inactive":
                            print(Fore.RED + "Hava savunma sistemi pasiftir.")

    def hss_start(self):
        self.receive_status()

#! Kalman filtresinden gelen verilerin ekleneceği bölüm
class kalmanfilterReceiver:
    def __init__(self):
        self.kf = KalmanFilter()
        self.datas = []

    def veri_cekme(self):
        measurements = [(320, 240), (330, 245), (340, 250), (350, 255), (360, 260)]
        for measurement in measurements:
            self.kf.add_measurements([measurement])
            self.datas.append(measurement)
        # print("Kalman Gelen Veriler: ", self.datas)
        return self.datas
    
    def start(self):
        return self.veri_cekme()

#! Yönelim verilerinin çekileceği bölüm
#class yonelimReceiver:

kalman = kalmanfilterReceiver()
hss = StatusReceiver()

veriler = kalman.start()
hss_data = hss.start()

print(veriler)
print(hss_data)