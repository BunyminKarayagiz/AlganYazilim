import cv2
import numpy as np
import math

class KalmanFilter:
    def __init__(self, xCenter, yCenter):
        print("init calisiyor!")

        self.xCenter = xCenter
        self.yCenter = yCenter
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
        
        # kalman filtresi çalışırken errorCovPre matrisi sürekli güncellenir ve tahminlerin doğruluğu bu matrisin değerlerine göre iyileştirilir
        self.kf.errorCovPre = np.array([[1.0, 0.0, 0.0, 0.0],
                                        [0.0, 1.0, 0.0, 0.0],
                                        [0.0, 0.0, 1.0, 0.0],
                                        [0.0, 0.0, 0.0, 1.0]], np.float32)
        """
        Başlangicta böyledir:
        [[1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]] sürekli olarak güncellenir. Tahminden öncedir.
        """
        
        # Filtrenin bir ölçüm yaptıktan sonra kalan belirsizliğini ifade eder 
        self.kf.errorCovPost = np.array([[1.0, 0.0, 0.0, 0.0],
                                        [0.0, 1.0, 0.0, 0.0],
                                        [0.0, 0.0, 1.0, 0.0],
                                        [0.0, 0.0, 0.0, 1.0]], np.float32)
        """
        Başlangicta böyledir:
        [[1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]] sürekli olarak güncellenir. Tahminden sonradir.
        """
        
        self.kalman_gain = np.zeros((4, 2), dtype=np.float32)

    def predict(self):
        statePre = self.kf.predict()
        print("precit calisiyor!")
        return statePre

    def correct(self, measurement):
        print("correct calisiyor!")
        self.kf.correct(measurement)

    def get_state(self):
        print("correct calisiyor!")
        return self.kf.statePost
    
    def add_measurement(self):
        print("measurement calisiyor!")
        measure = [self.xCenter, self.yCenter]
        self.measurements.append(measure)
        measurements = self.measurements

        for meas in measurements:
            print("for calisiyor!")
            measurement = np.array([[np.float32(meas[0])], [np.float32(meas[1])]])
            self.kf.correct(measurement)
            
            predicted_state = KalmanFilter.predict()
            state_post = KalmanFilter.get_state()
            speed_x = predicted_state[2]
            speead_y = predicted_state[3]
            speed = math.sqrt((speed_x**2) + (speead_y**2))

            print(f"Ölçüm: {meas}")
            print(f"Tahmin Edilen Durum: {predicted_state.T}")
            print(f"Güncellenmiş Durum: {state_post.T}")
            print(f"Genel Hiz: {speed}")
            print("------")
        
KalmanFilter(100, 200)