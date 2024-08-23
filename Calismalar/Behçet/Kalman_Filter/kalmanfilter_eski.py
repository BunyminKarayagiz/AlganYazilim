import cv2
import numpy as np

class KalmanFilter:
    
    kf = cv2.KalmanFilter(4, 2)
    kf.measurementMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1]], np.float32)
    kf.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
    datas = []
    

    def predict(self, coordX, coordY):

        data = [coordX, coordY]
        self.datas.append(data)
        
        if len(self.datas) > 50:
            self.datas = self.datas[-50:]

        print("Kalman Rakip Veri Dizisi : ", self.datas)

        measured = np.array([[np.float32(coordX)], [np.float32(coordY)]])
        self.kf.correct(measured)
        predicted = self.kf.predict()

        x, y = float(predicted[0]), float(predicted[1])
        vx, vy = float(predicted[2]), float(predicted[3])

        return x, y, vx, vy