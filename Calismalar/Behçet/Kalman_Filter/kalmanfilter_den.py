import cv2
import numpy as np
import math

class KalmanFilter:
    def __init__(self, xCoord, yCoord):
        self.coord_x = xCoord
        self.coord_y = yCoord
        self.datas = []

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
        """Başlangicta böyledir:
        [[1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]] sürekli olarak güncellenir. Tahminden öncedir."""
        
        # Filtrenin bir ölçüm yaptıktan sonra kalan belirsizliğini ifade eder 
        self.kf.errorCovPost = np.array([[1.0, 0.0, 0.0, 0.0],
                                        [0.0, 1.0, 0.0, 0.0],
                                        [0.0, 0.0, 1.0, 0.0],
                                        [0.0, 0.0, 0.0, 1.0]], np.float32)
        """Başlangicta böyledir:
        [[1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]] sürekli olarak güncellenir. Tahminden sonradir."""
        
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
    
    def gelen_veriler(self):
        data = [self.coord_x, self.coord_y]
        self.datas.append(data)
        print("Datas : ", self.datas)
        return self.datas

if __name__ == "__main__":
    kf = KalmanFilter(10, 20)

    measurements = KalmanFilter.gelen_veriler

    for meas in measurements:
        measurement = np.array([[np.float32(meas[0])], [np.float32(meas[1])]])
        kf.correct(measurement)
        
        predicted_state = kf.predict()
        state_post = kf.get_state()
        speed_x = predicted_state[2]
        speead_y = predicted_state[3]
        speed = math.sqrt(speed_x**2 + speead_y**2)

        print(f"Ölçüm: {meas}")
        print(f"Tahmin Edilen Durum: {predicted_state.T}")
        print(f"Güncellenmiş Durum: {state_post.T}")
        print(f"Genel Hiz: {speed}")
        print("------")