# Tahmin algoritması için yapılması gerekenler(Önem sırasına göre):
#! Yapılacak-1: Matematiksel işlemlerin arttırılması ve yeni işlemlerin çoğaltılması ile tahminler, gerçek değerlere yakınlaştırılacak.
#! Yapılacak-2: Hız verilerini doğru ölçmediği farkedeldi düzeltilmesi gerekiyor!
#! Yapılacak-3: İvme verileri de oluşturulacak.
#! Yapılacak-4: Z ekseni de eklenebilir. Bu yolov8_deploy kısmında da yapılabilir.

import cv2
import numpy as np
import math

class KalmanFilter:
    def __init__(self, xCenter=None, yCenter=None):
        print("Kalman algortimasi devrede!")
        self.measurements = []
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

    def predict(self):
        statePre = self.kf.predict()
        return statePre

    def correct(self, measurement):
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