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
import cupy as cp

class KalmanFilter:
    def __init__(self, xCenter=None, yCenter=None):
        print("Kalman algoritmasi devrede!")
        self.measurements = []
        
        # Matrisleri numpy yerine cupy ile oluşturun
        self.transitionMatrix = cp.array([[1, 0, 1, 0, 0.5, 0],
                                         [0, 1, 0, 1, 0, 0.5],
                                         [0, 0, 1, 0, 1, 0],
                                         [0, 0, 0, 1, 0, 1],
                                         [0, 0, 0, 0, 1, 0],
                                         [0, 0, 0, 0, 0, 1]], dtype=cp.float32)
        
        self.measurementMatrix = cp.array([[1, 0, 0, 0, 0, 0],
                                          [0, 1, 0, 0, 0, 0]], dtype=cp.float32)
        
        self.processNoiseCov = cp.array([[1e-1, 0, 0, 0, 0, 0],
                                        [0, 1e-1, 0, 0, 0, 0],
                                        [0, 0, 1e-1, 0, 0, 0],
                                        [0, 0, 0, 1e-1, 0, 0],
                                        [0, 0, 0, 0, 1e-1, 0],
                                        [0, 0, 0, 0, 0, 1e-1]], dtype=cp.float32)
        
        self.measurementNoiseCov = cp.array([[1e-1, 0],
                                            [0, 1e-1]], dtype=cp.float32)
        
        self.errorCovPre = cp.array([[1, 0, 0, 0, 0, 0],
                                    [0, 1, 0, 0, 0, 0],
                                    [0, 0, 1, 0, 0, 0],
                                    [0, 0, 0, 1, 0, 0],
                                    [0, 0, 0, 0, 1, 0],
                                    [0, 0, 0, 0, 0, 1]], dtype=cp.float32)
        
        self.errorCovPost = cp.array([[1, 0, 0, 0, 0, 0],
                                     [0, 1, 0, 0, 0, 0],
                                     [0, 0, 1, 0, 0, 0],
                                     [0, 0, 0, 1, 0, 0],
                                     [0, 0, 0, 0, 1, 0],
                                     [0, 0, 0, 0, 0, 1]], dtype=cp.float32)
        
        self.gain = cp.array([[1, 0, 0, 0, 0, 0],
                              [0, 1, 0, 0, 0, 0],
                              [0, 0, 1, 0, 0, 0],
                              [0, 0, 0, 1, 0, 0],
                              [0, 0, 0, 0, 1, 0]], dtype=cp.float32)

        # Initial state
        self.statePre = cp.zeros((6, 1), dtype=cp.float32)
        self.statePost = cp.zeros((6, 1), dtype=cp.float32)
    
    def predict(self):
        self.statePre = cp.dot(self.transitionMatrix, self.statePost)
        return self.statePre

    def correct(self, measurement):
        start_time = time.perf_counter()
        
        S = cp.dot(self.measurementMatrix, cp.dot(self.errorCovPre, self.measurementMatrix.T)) + self.measurementNoiseCov
        K = cp.dot(self.errorCovPre, cp.dot(self.measurementMatrix.T, cp.linalg.inv(S)))
        
        y = measurement - cp.dot(self.measurementMatrix, self.statePre)
        
        self.statePost = self.statePre + cp.dot(K, y)
        I = cp.eye(self.transitionMatrix.shape[0], dtype=cp.float32)
        self.errorCovPost = cp.dot(I - cp.dot(K, self.measurementMatrix), self.errorCovPre)
        
        elapsed_time = time.perf_counter() - start_time
        print(f"Correct işlemi Süresi: {elapsed_time:.9f} saniye")

        return self.statePost

    def get_state(self):
        return self.statePost

    def add_measurements(self, measurements):
        for meas in measurements:
            x, y = meas
            measurement = cp.array([[cp.float32(x)], [cp.float32(y)]])
            self.measurements.append([x, y])

            self.correct(measurement)

            predicted_state = self.predict()
            state_post = self.get_state()

            speed_x = predicted_state[2].item() 
            speed_y = predicted_state[3].item()
            speed = cp.sqrt((speed_x**2) + (speed_y**2))

            cp.set_printoptions(suppress=True)
            print(f"Son ölçüm: {self.measurements[-1]}")
            print(f"Tahmin edilen durum: {predicted_state.T}")
            print(f"Güncellenmiş durum: {state_post.T}")
            print(f"Hiz: {speed}")
            print("------")