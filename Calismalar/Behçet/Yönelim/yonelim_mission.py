import numpy as np
from colorama import init, Fore
import cv2
import time
from pymavlink import mavutil

class KalmanFilter:
    def __init__(self):
        print(Fore.RED + "Kalman Filtresi ile Yönelim Algoritması DEVREDE!")
        init(autoreset=True)
        
        # Kalman Filter parametreleri
        self.kf = cv2.KalmanFilter(9, 6)
        
        # Geçiş Matrisi (Basitleştirilmiş)
        self.kf.transitionMatrix = np.eye(9, dtype=np.float32)
        
        # Ölçüm Matrisi (Özelleştirilmiş)
        self.kf.measurementMatrix = np.array([
            [1, 0, 0, 0, 0, 0, 0, 0, 0],   # enlem
            [0, 1, 0, 0, 0, 0, 0, 0, 0],   # boylam
            [0, 0, 1, 0, 0, 0, 0, 0, 0],   # roll
            [0, 0, 0, 1, 0, 0, 0, 0, 0],   # pitch
            [0, 0, 0, 0, 1, 0, 0, 0, 0],   # yaw
            [0, 0, 0, 0, 0, 1, 0, 0, 0],   # hız
        ], dtype=np.float32)
        
        # Gürültü Kovaryansları (Optimize Edilmiş)
        self.kf.processNoiseCov = np.eye(9, dtype=np.float32) * 1e-2
        self.kf.measurementNoiseCov = np.eye(6, dtype=np.float32) * 1e-1
        
        # Hata Kovaryansları
        self.kf.errorCovPre = np.eye(9, dtype=np.float32)
        self.kf.errorCovPost = np.eye(9, dtype=np.float32)

    def predict(self):
        return self.kf.predict()
    
    def correct(self, measurement):
        return self.kf.correct(measurement)

def get_mavlink_data(connection):
    # Mission Planner'dan veri almak için bir bağlantı oluşturuyoruz
    msg = connection.recv_match(type=['ATTITUDE', 'GPS_RAW_INT'], blocking=True)
    
    # Veriyi işleyip uygun formata getiriyoruz
    if msg:
        if msg.get_type() == 'ATTITUDE':
            return np.array([
                msg.roll, msg.pitch, msg.yaw
            ], dtype=np.float32)
        elif msg.get_type() == 'GPS_RAW_INT':
            return np.array([
                msg.lat / 1e7, msg.lon / 1e7, 0, 0, 0, 0
            ], dtype=np.float32)
    return None

def test_kalman_filter(kf, connection):
    # Başlangıç durumu
    initial_state = np.array([100, 50, 10, 5, 2, 20, 1000, 0, 0], dtype=np.float32)
    kf.kf.statePre = initial_state

    # Ölçümleri filtreye yedirme ve tahminleme
    start_time = time.time()
    for _ in range(200):  # 200 ölçüm döngüsü
        measurement = get_mavlink_data(connection)
        if measurement is not None:
            np.set_printoptions(suppress=True)
            predicted_state = kf.predict()
            print(Fore.GREEN + f"Ölçülen Durum: {measurement}")
            print(Fore.RED + f"Tahmin edilen durum: {predicted_state.ravel()}")
            corrected_state = kf.correct(measurement)
            print(Fore.BLUE + f"Düzeltilmiş durum: {corrected_state.ravel()}")
            print("----------------------------\n")
        time.sleep(1)  # 1 saniyede bir veri al
    end_time = time.time()
    print(Fore.CYAN + f"Toplam Süre: {end_time - start_time} saniye")

# MAVLink bağlantısını başlat
connection = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)  # Bağlantı noktası ve baud rate'i ayarlayın

# Kalman filtresini test et
kf = KalmanFilter()
test_kalman_filter(kf, connection)
