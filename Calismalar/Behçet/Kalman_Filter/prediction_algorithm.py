"""Tahmin algoritmasi için yapilmasi gerekenler(Önem sirasina göre)"""
# Yapıldı: prediction_algorithm, yolov8_depoloy koduna entegre edilecek. Oradan gelen verilerle kalman filtresi çalıaşacak. 
#! Amaç: Matematiksel işlemlerin arttırılması ve yeni işlemlerin çoğaltılması ile tahminler, gerçek değerlere yakınlaştırılacak.
#! Yapılacak: Hız verilerini doğru ölçmediği farkedeldi düzeltilmesi gerekiyor! Hızı doğru ölçebildiğimizden emin olmamız lazım. Çünkü konum hız ile bulunuyor.
#! Yapılacak: İvme verileri oluşturulacak.
#! Yapılacak: Üç boyutlu takip eklenecek. Bu yolov8_deploy kısmında da yapılabilir.
#! Yapılacak: Önceden bilinen verilerle kalman filtresinin çalışmasına bakılacak.
#! Hızlanma(Acceleration) Modeline bakılacak. 
#! Denenebilir: Eğer her şey düzenli çalışırsa çoklu kalman yaklaşımı uygulanabilir.

import cv2
import numpy as np
import math
import time

class KalmanFilter:
    def __init__(self, xCenter=None, yCenter=None):
        print("Kalman algortimasi devrede!")
        self.measurements = []
        # self.previous_time = time.time()
        self.kf = cv2.KalmanFilter(4, 2)
        self.kf.transitionMatrix = np.array([[1, 0, 1, 0],
                                             [0, 1, 0, 1],
                                             [0, 0, 1, 0],
                                             [0, 0, 0, 1]], np.float32)
        
        self.kf.measurementMatrix = np.array([[1, 0, 0, 0],
                                              [0, 1, 0, 0]], np.float32)
        
        self.kf.processNoiseCov = np.array([[1e-4, 0, 0, 0],
                                            [0, 1e-4, 0, 0],
                                            [0, 0, 1e-2, 0],
                                            [0, 0, 0, 1e-2]], np.float32)
        
        self.kf.measurementNoiseCov = np.array([[1e-1, 0],
                                                [0, 1e-1]], np.float32)
        
        self.kf.errorCovPre = np.array([[1.0, 0.0, 0.0, 0.0],
                                        [0.0, 1.0, 0.0, 0.0],
                                        [0.0, 0.0, 1.0, 0.0],
                                        [0.0, 0.0, 0.0, 1.0]], np.float32)
        
        self.kf.errorCovPost = np.array([[1.0, 0.0, 0.0, 0.0],
                                         [0.0, 1.0, 0.0, 0.0],
                                         [0.0, 0.0, 1.0, 0.0],
                                         [0.0, 0.0, 0.0, 1.0]], np.float32)
        
        self.kalman_gain = np.array([[1.0, 0.0, 0.0, 0.0],
                                     [0.0, 1.0, 0.0, 0.0],
                                     [0.0, 0.0, 1.0, 0.0],
                                     [0.0, 0.0, 0.0, 1.0]], np.float32)

        self.prev_velocity = np.array([0, 0], np.float32)        
    """def delta_time(self):
        current_time = time.time()
        dt = current_time - self.previous_time
        self.previous_time = current_time
        return dt"""

    def predict(self):
        """dt = self.delta_time()
        self.kf.transitionMatrix = np.array([[1, 0, dt, 0],
                                             [0, 1, 0, dt],
                                             [0, 0, 1, 0], 
                                             [0, 0, 0, 1]], np.float32)"""
        
        statePre = self.kf.predict()
        return statePre

    def correct(self, measurement):
        start_time = time.perf_counter()
        elapsed_time = time.perf_counter() - start_time
        print(f"Correct islemi Süresi: {elapsed_time:.9f} saniye")

        # alttaki yapının çalışma prensibi:
        """
        bu kisim her tahmin ve düzeltme adiminda gurultu seviyelerinin dinamik olarak ayarlanmasini saglar.
        Sistemde ani bir hiz degisimi tespit edilirse, surec gurultu koveryansi attirilir ve filtre degisikleri
        esnek olarak takip eder. Hiz sabitse gurultu koveryansi daha dusuk tutulur ve daha kararli bir tahminleme
        islemi yapilir.
        """


        current_velocity = np.array([self.kf.statePost[2], self.kf.statePost[3]], np.float32)

        velocity_change = np.linalg.norm(current_velocity - self.prev_velocity)

        if velocity_change > 1.0:
            self.kf.processNoiseCov = np.array([[1e-3, 0, 0, 0],
                                                [0, 1e-3, 0, 0],
                                                [0, 0, 1e-1, 0],
                                                [0, 0, 0, 1e-1]], np.float32)
            
        else:
            self.kf.processNoiseCov = np.array([[1e-4, 0, 0, 0],
                                                [0, 1e-4, 0, 0],
                                                [0, 0, 1e-2, 0],
                                                [0, 0, 0, 1e-2]], np.float32)
        self.prev_velocity = current_velocity
        self.kf.correct(measurement)

    def get_state(self):
        return self.kf.statePost

    def add_measurements(self, measurements):
        for meas in measurements:
            x, y = meas
            measurement = np.array([[np.float32(x)], [np.float32(y)]])
            self.measurements.append([x, y])
            self.correct(measurement)
            
            predicted_state = self.predict()
            state_post = self.get_state()
            
            speed_x = predicted_state[2].item()
            speed_y = predicted_state[3].item()

            speed = math.sqrt((speed_x**2) + (speed_y**2))

            print(f"Son ölçüm: {self.measurements[-1]}")
            print(f"Tahmin edilen durum: {predicted_state.T}")
            print(f"Güncellenmiş durum: {state_post.T}")
            print(f"Hiz: {speed}")
            # print(f"Datas : {self.measurements}")
            print("------")

            x_data = predicted_state[0]
            y_data = predicted_state[1]
            vx_data = speed_x
            vy_data = speed_y

            var_x = np.var(x_data)
            var_y = np.var(y_data)
            var_vx = np.var(vx_data)
            var_vy = np.var(vy_data)

            self.kf.errorCovPost = self.kf.errorCovPost = np.array([[var_x, 0, 0, 0],
                                             [0, var_y, 0, 0],
                                             [0, 0, var_vx, 0],
                                             [0, 0, 0, var_vy]], np.float32)          
            