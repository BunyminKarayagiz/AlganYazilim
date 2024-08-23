"""import cv2
import numpy as np

class KalmanFilter:
    def __init__(self, dynamParams: int, measureParams: int, controlParams: int = 0, type: int = cv2.CV_32F) -> None:
        # Kalman Filter'in yapılandırmasını yapıyoruz
        self.kf = cv2.KalmanFilter(dynamParams, measureParams, controlParams, type)

        # Matrislerin başlangıç değerlerini tanımlıyoruz
        self.kf.transitionMatrix = np.eye(dynamParams, dtype=type)  # Durum geçiş matrisi
        self.kf.measurementMatrix = np.eye(measureParams, dynamParams, dtype=type)  # Ölçüm matrisi
        self.kf.processNoiseCov = np.eye(dynamParams, dtype=type) * 1e-4  # İşlem gürültü matrisi
        self.kf.measurementNoiseCov = np.eye(measureParams, dtype=type) * 1e-1  # Ölçüm gürültü matrisi
        self.kf.errorCovPre = np.eye(dynamParams, dtype=type)  # Önceki hata kovaryans matrisi
        self.kf.statePre = np.zeros((dynamParams, 1), dtype=type)  # Önceki durum
        self.kf.statePost = np.zeros((dynamParams, 1), dtype=type)  # Son durum
        
        # Kontrol matrisi ve kontrol vektörünü tanımlıyoruz
        self.kf.controlMatrix = np.zeros((dynamParams, controlParams), dtype=type)  # Kontrol matrisi
        self.kf.control = np.zeros((controlParams, 1), dtype=type)  # Kontrol vektörü

    def predict(self, control: np.ndarray | None = None) -> np.ndarray:
        if control is not None:
            self.kf.control = control
        return self.kf.predict()

    def correct(self, measurement: np.ndarray) -> np.ndarray:
        return self.kf.correct(measurement)

# Kalman Filtresi nesnesini oluşturuyoruz
kf = KalmanFilter(dynamParams=4, measureParams=2, controlParams=1)

# Örnek kontrol ve ölçüm verileri
control_input = np.array([[1]], dtype=np.float32)  # Örneğin, bir hız artırma kontrolü
measurement = np.array([[0.5], [0.7]], dtype=np.float32)  # Ölçüm verileri

# Tahmin yapıyoruz
predicted_state = kf.predict(control=control_input)
print("Predicted State:", predicted_state)

# Ölçüm verileri ile düzeltme yapıyoruz
corrected_state = kf.correct(measurement)
print("Corrected State:", corrected_state)"""


import torch
import cupy as cp

print(torch.version.cuda)

a = cp.array([1, 2, 3, 4, 5])
print(a)