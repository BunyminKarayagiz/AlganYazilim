import numpy as np
import cv2

class KalmanFilter:
    def __init__(self):
        # Kalman Filter parametreleri
        self.kf = cv2.KalmanFilter(9, 6)
        self.kf = KalmanFilter
        self.measurements = []
        
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
        
        # Başlangıç durumu
        self.kf.statePre = np.zeros((9, 1), dtype=np.float32)

    def set_initial_state(self, state):
        """Başlangıç durumunu ayarla."""
        self.kf.statePre = np.array(state, dtype=np.float32).reshape((9, 1))

    def predict(self):
        """Tahmin yap."""
        return self.kf.predict()

    def correct(self, measurement):
        """Ölçüm verileri ile düzeltme yap."""
        return self.kf.correct(np.array(measurement, dtype=np.float32).reshape((6, 1)))

    def next_position(self):
        """Bir adim tahmin yaparak bir sonraki pozisyonu döndür."""
        return self.kf.predict()
    
    def add_measurement(self, enlem, boylam, roll, pitch, yaw, hiz):
        measurement = [enlem, boylam, roll, pitch, yaw, hiz]
        self.measurements.append(measurement)

        for meas in self.measurements:
            enlem, boylam, roll, pitch, yaw, hiz = meas
            predicted_state = self.predict()
            corrected_state = self.correct(meas)
            next_position = self.next_position()

            print(f"Ölçülen Durum: {measurement}")
            print(f"Tahmin edilen durum: {predicted_state.ravel()}")
            print(f"Düzeltilmiş durum: {corrected_state.ravel()}")
            print(f"Bir sonraki pozisyon tahmini: {next_position.ravel()}")
            print("----------------------------")

"""# Örnek kullanım
if __name__ == "__main__":
    kf = KalmanFilter()

    # Başlangıç durumu
    initial_state = [100, 50, 10, 5, 2, 20, 1000, 0, 0]
    kf.set_initial_state(initial_state)

    # Ölçümler
    measurements = [
        [100.1, 50.2, 10.1, 5.1, 2.1, 20.1],
        [100.2, 50.4, 10.2, 5.2, 2.2, 20.3],
        [100.3, 50.6, 10.3, 5.3, 2.3, 20.5],
        [100.4, 50.8, 10.4, 5.4, 2.4, 20.7],
        [100.5, 51.0, 10.5, 5.5, 2.5, 20.9],
        [100.6, 51.2, 10.6, 5.6, 2.6, 21.0],
        [100.7, 51.4, 10.7, 5.7, 2.7, 21.2],
        [100.8, 51.6, 10.8, 5.8, 2.8, 21.4],
        [100.9, 51.8, 10.9, 5.9, 2.9, 21.6],
        [101.0, 52.0, 11.0, 6.0, 3.0, 21.8]
    ]

    # Ölçümleri filtreye yedirme ve tahminleme
    for measurement in measurements:
        predicted_state = kf.predict()
        corrected_state = kf.correct(measurement)
        print(f"Ölçülen Durum: {measurement}")
        print(f"Tahmin edilen durum: {predicted_state.ravel()}")
        print(f"Düzeltilmiş durum: {corrected_state.ravel()}")
        print("----------------------------")

    # Bir sonraki pozisyonu tahmin et
    next_position = kf.get_next_position()
    print(f"Bir sonraki pozisyon tahmini: {next_position.ravel()}")"""
