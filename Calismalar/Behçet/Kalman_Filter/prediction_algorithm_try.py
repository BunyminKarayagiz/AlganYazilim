"""Tahmin algoritmasi için yapilmasi gerekenler(Önem sirasina göre)"""
# Yapıldı: prediction_algorithm, yolov8_depoloy koduna entegre edilecek. Oradan gelen verilerle kalman filtresi çalıaşacak. 
#! Amaç: Matematiksel işlemlerin arttırılması ve yeni işlemlerin çoğaltılması ile tahminler, gerçek değerlere yakınlaştırılacak.
#! Yapılacak: Hız verilerini doğru ölçmediği farkedeldi düzeltilmesi gerekiyor! Hızı doğru ölçebildiğimizden emin olmamız lazım. Çünkü konum hız ile bulunuyor.
# Yapıldı: İvme verileri oluşturulacak.
#! Yapılacak: Üç boyutlu takip eklenecek. Bu yolov8_deploy kısmında da yapılabilir.
#! Yapılacak: Önceden bilinen verilerle kalman filtresinin çalışmasına bakılacak.
#! Hızlanma(Acceleration) Modeline bakılacak. 
#! Denenebilir: Eğer her şey düzenli çalışırsa çoklu kalman yaklaşımı uygulanabilir.

import cv2
import numpy as np
import math
import time
from colorama import Fore, init

class KalmanFilter:
    def __init__(self, xCenter=None, yCenter=None):
        print(Fore.RED + "Kalman algoritmasi devrede!")
        init(autoreset=True)
        self.measurements = []
        self.kf = cv2.KalmanFilter(6, 2)

        self.kf.transitionMatrix = np.array([[1, 0, 1, 0, 0.5, 0],
                                             [0, 1, 0, 1, 0, 0.5],
                                             [0, 0, 1, 0, 1, 0],
                                             [0, 0, 0, 1, 0, 1],
                                             [0, 0, 0, 0, 1, 0],
                                             [0, 0, 0, 0, 0, 1]], dtype=np.float32)
        # 0.5: 1/2at^2 den geliyor
        
        self.kf.measurementMatrix = np.array([[1, 0, 0, 0, 0, 0],
                                              [0, 1, 0, 0, 0, 0]], dtype=np.float32)
        
        self.kf.processNoiseCov = np.array([[1e-1, 0, 0, 0, 0, 0],
                                            [0, 1e-1, 0, 0, 0, 0],
                                            [0, 0, 1e-1, 0, 0, 0],
                                            [0, 0, 0, 1e-1, 0, 0],
                                            [0, 0, 0, 0, 1e-1, 0],
                                            [0, 0, 0, 0, 0, 1e-1]], dtype=np.float32)
                
        self.kf.measurementNoiseCov = np.array([[1e-1, 0],
                                                [0, 1e-1]], dtype=np.float32)
        
        self.kf.errorCovPre = np.array([[1, 0, 0, 0, 0, 0],
                                        [0, 1, 0, 0, 0, 0],
                                        [0, 0, 1, 0, 0, 0],
                                        [0, 0, 0, 1, 0, 0],
                                        [0, 0, 0, 0, 1, 0],
                                        [0, 0, 0, 0, 0, 1]], dtype=np.float32)
                
        self.kf.errorCovPost = np.array([[1, 0, 0, 0, 0, 0],
                                        [0, 1, 0, 0, 0, 0],
                                        [0, 0, 1, 0, 0, 0],
                                        [0, 0, 0, 1, 0, 0],
                                        [0, 0, 0, 0, 1, 0],
                                        [0, 0, 0, 0, 0, 1]], dtype=np.float32)
        
        self.kf.gain = np.array([[1, 0, 0, 0, 0, 0],
                                [0, 1, 0, 0, 0, 0],
                                [0, 0, 1, 0, 0, 0],
                                [0, 0, 0, 1, 0, 0],
                                [0, 0, 0, 0, 1, 0],
                                [0, 0, 0, 0, 0, 1]], dtype=np.float32)
        """
        #* bakilacak
        self.kf.controlMatrix = np.array([[0, 0],
                                 [0, 0],
                                 [1, 0],
                                 [0, 1],
                                 [0, 0],
                                 [0, 0]], dtype=np.float32)
        """

    def predict(self):
        
        statePre = self.kf.predict()
        return statePre
    
    def predict(self):
        """
        #* bakilacak
        acceleration = 0.5
        braking = 0.1
        control_input = np.array([[acceleration], [braking]], dtype=np.float32)
        statePre = self.kf.predict()
        self.kf.statePre += self.kf.controlMatrix @ control_input
        """
        statePre = self.kf.predict()
        self.kf.errorCovPre = self.kf.transitionMatrix @ self.kf.errorCovPost @ self.kf.transitionMatrix.T + self.kf.processNoiseCov
        return statePre


    def correct(self, measurement):
        start_time = time.perf_counter()

        S = self.kf.measurementMatrix @ self.kf.errorCovPre @ self.kf.measurementMatrix.T + self.kf.measurementNoiseCov
        K = self.kf.errorCovPre @ self.kf.measurementMatrix.T @ np.linalg.inv(S)

        y = measurement - (self.kf.measurementMatrix @ self.kf.statePre)

        self.kf.statePost = self.kf.statePre + K @ y

        I = np.eye(self.kf.transitionMatrix.shape[0], dtype=np.float32)
        self.kf.errorCovPost = (I - K @ self.kf.measurementMatrix) @ self.kf.errorCovPre

        elapsed_time = time.perf_counter() - start_time
        print(f"Correct işlemi Süresi: {elapsed_time:.9f} saniye")

        return self.kf.statePost

    def get_state(self):
        return self.kf.statePost
    
    def coordinat_pwm(self, xCoord, yCoord):
        screen_width = 640
        screen_height = 480

        min_pwm = 1100
        max_pwm = 1900

        pwm_x = int((xCoord / screen_width) * (max_pwm - min_pwm) + min_pwm)
        pwm_y = int((yCoord / screen_height) * (max_pwm - min_pwm) + min_pwm)

        if pwm_y > 1500:
            fark = pwm_y - 1500
            pwm_y = 1500 - fark
        else : 
            fark = 1500 - pwm_y
            pwm_y = 1500 + fark

        if xCoord == 0 and yCoord == 0:
            pwm_x = 1500
            pwm_y = 1500

        pwm_kalman:tuple = (pwm_x, pwm_y)

        return pwm_kalman    

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

            coordinat_pwm = self.coordinat_pwm(x, y)

            np.set_printoptions(suppress=True)
            print(Fore.BLUE + f"Tahmin PWM : {coordinat_pwm}") 
            print(f"Son ölçüm: {self.measurements[-1]}")
            print(Fore.GREEN + f"Tahmin edilen durum: {predicted_state.T}")
            print(f"Güncellenmiş durum: {state_post.T}")
            print(f"Hiz: {speed}")
            print("------")