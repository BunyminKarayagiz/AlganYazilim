import os
import torch
import numpy as np
import cv2
from ultralytics import YOLO
from kalmanfilter_den import KalmanFilter
import math

class Detection:

    def __init__(self, path):
        self.model = YOLO(path)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)
        self.datas = []

    def model_predict(self, frame,frame_id):
        #results = self.model.predict(frame, verbose=False)
        results = self.model.track(source=frame, conf=0.75, iou=0.5, show=False, tracker="botsort.yaml", verbose=False)
        # ----------------------detect/track etmediği durum için düzenlenecek----------------------------

        """pwm_verileri = {
                        'pwmx': 1500,
                        'pwmy': 1500,
                        'frame_id':frame_id
                        }"""
        
        pwm_verileri = np.array([1500,1500,frame_id],dtype=np.uint32)
        
        x, y = frame.shape[0], frame.shape[1]

        target_area_y1, target_area_y2 = (int(x * 0.10), int(x * 0.90))
        target_area_x1, target_area_x2 = (int(y * 0.25), int(y * 0.75))

        cv2.rectangle(frame, (target_area_x1, target_area_y1), (target_area_x2, target_area_y2), (255, 0, 0), 2) #RGB

        locked_or_not = False
        if results:
            kf = KalmanFilter()
            annotated_frame = results[0].plot()

            boxes = results[0].boxes.xyxy.cpu().tolist()

            for box in boxes:
                x1, y1, x2, y2 = box
                x_center = int((x1 + x2) / 2)
                y_center = int((y1 + y2) / 2)

                pwm_verileri = self.coordinates_to_pwm(x_center, y_center, frame_id)

                """#! Kalman filtesinin kullanildigi bolum
                predicted = kf.predict(x_center, y_center)

                kalman_x = int(predicted[0])
                kalman_y = int(predicted[1])
                kalman_vx = int(predicted[2])
                kalman_vy = int(predicted[3])

                tahmini_hiz = math.sqrt((kalman_vx)**2 + (kalman_vy)**2)
                gercek_konum = [x_center, y_center]
                tahmin = [kalman_x, kalman_y]

                print("Rakinin su anki konumu: ", gercek_konum)
                print("Rakibin gideceği konumlarin tahmini: ", tahmin)
                print("Rakibin hiz tahmini", tahmini_hiz)"""

                data = [x_center, y_center]
                self.datas.append(data)
                print("Datas : ", self.datas)
                

                if(target_area_x1<x1 and target_area_x2>x2 and target_area_y1<y1 and target_area_y2>y2):
                    locked_or_not = True

                return pwm_verileri, annotated_frame, locked_or_not
            
        return pwm_verileri, annotated_frame, locked_or_not

    def coordinates_to_pwm(self, x_center, y_center, frame_id):
        screen_width = 640
        screen_height = 480
        min_pwm = 1100
        max_pwm = 1900
        
        pwm_x = int((x_center / screen_width) * (max_pwm - min_pwm) + min_pwm)
        pwm_y = int((y_center / screen_height) * (max_pwm - min_pwm) + min_pwm)

        if pwm_y > 1500:
            fark = pwm_y - 1500
            pwm_y = 1500 - fark
        else : 
            fark = 1500 - pwm_y
            pwm_y = 1500 + fark

        if x_center == 0 and y_center == 0:
            pwm_x = 1500
            pwm_y = 1500

        """pwm_verileri = {
                        'pwmx': pwm_x,
                        'pwmy': pwm_y,
                        'frame_id': frame_id
                        }"""
        pwm_verileri = np.array([pwm_x,pwm_y,frame_id],dtype=np.uint32)

        return pwm_verileri

    def __call__(self):

        cap = cv2.VideoCapture(0)  # webcam

        frame_id = 0

        while True:
            ret, frame = cap.read()

            if ret:
                frame = cv2.resize(frame, (640, 480))

                pwm_verileri, annotated_frame, locked_or_not = self.model_predict(frame, frame_id)
                cv2.imshow("YOLOv8 Tracking", annotated_frame)
                print("PWM Verileri: ", pwm_verileri, "\n")
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

class KalmanFilter:
    def __init__(self):
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
        """ Başlangicta böyledir:
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
        """ Başlangicta böyledir:
        [[1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]] sürekli olarak güncellenir. Tahminden sonradır.
        """
        
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

if __name__ == "__main__":
    kf = KalmanFilter()

    measurements = [[433, 69], [423, 103], [418, 118], [415, 131], [412, 143], [411, 153], [414, 180], [420, 193], [422, 199], [424, 203], 
                    [425, 205], [422, 206], [421, 206], [418, 206], [415, 205], [409, 205], [405, 205], [402, 205], [396, 205], [393, 205], 
                    [381, 203], [378, 203], [371, 202], [361, 202], [355, 202], [348, 202], [344, 202], [342, 203], [334, 202], [331, 201], 
                    [330, 202], [323, 202], [319, 202], [308, 202], [305, 203], [296, 203], [292, 203], [289, 203], [283, 203], [279, 203], 
                    [276, 203], [273, 203], [270, 203], [267, 202], [264, 202], [261, 203], [259, 202], [257, 203], [255, 203], [253, 203], 
                    [251, 203], [249, 204], [248, 204], [246, 204], [245, 204], [243, 204], [242, 204], [239, 204], [238, 203], [237, 203], 
                    [235, 203], [233, 202], [231, 202], [228, 202], [226, 202], [223, 201], [221, 201], [219, 200], [216, 200], [214, 199], 
                    [212, 198], [209, 197], [207, 196], [206, 195], [204, 194], [202, 193], [200, 191], [199, 191], [197, 190], [195, 189], 
                    [194, 188], [192, 186], [190, 185], [188, 183], [186, 180], [184, 178], [181, 176], [180, 175], [179, 173], [177, 170], 
                    [176, 169], [175, 167], [175, 166], [174, 163], [174, 161], [174, 159], [174, 157], [175, 155], [175, 152], [180, 134], 
                    [184, 131], [186, 130], [187, 130], [189, 129], [190, 129], [193, 129], [194, 129], [196, 128], [197, 128], [199, 128], 
                    [201, 128], [202, 128], [203, 128], [205, 128], [207, 129], [209, 129], [210, 128], [212, 128], [215, 128], [222, 129], 
                    [224, 128], [227, 128], [229, 128], [232, 128], [235, 128], [238, 128], [241, 128], [243, 128], [246, 128], [249, 127], 
                    [252, 128], [254, 128], [257, 128], [260, 127], [264, 127], [266, 128], [270, 128], [273, 128], [276, 127], [279, 128], 
                    [283, 128], [286, 127], [289, 127], [292, 127], [295, 127], [302, 126], [303, 127], [307, 128], [311, 128], [317, 128], 
                    [321, 129], [335, 130], [339, 130], [342, 129], [345, 130], [348, 130], [352, 130], [355, 130], [358, 131], [361, 131], 
                    [364, 131], [367, 132], [370, 132], [372, 133], [375, 134], [378, 135], [393, 138], [396, 138], [399, 139], [405, 140], 
                    [407, 141], [410, 142], [412, 143], [415, 144], [425, 150], [430, 153], [434, 157], [434, 157], [435, 160], [437, 162], 
                    [445, 172], [446, 174], [448, 178], [448, 200], [436, 225], [422, 237], [420, 239], [417, 240], [408, 244], [406, 245], 
                    [385, 250], [373, 252], [357, 254], [346, 256], [342, 256], [339, 256], [333, 256], [331, 255], [327, 255], [319, 254], 
                    [316, 254], [306, 252], [302, 251], [300, 250], [297, 250], [294, 249], [292, 249], [289, 248], [286, 248], [284, 247], 
                    [280, 246], [272, 242], [270, 241], [268, 241], [267, 240], [265, 239], [263, 238], [262, 237], [260, 236], [259, 234], 
                    [258, 233], [257, 232], [251, 226], [251, 224], [250, 222], [249, 221], [248, 218], [248, 215], [247, 213], [246, 210], 
                    [246, 208], [243, 198], [243, 196], [244, 194], [245, 192], [246, 191], [249, 188], [251, 187], [253, 186], [256, 185], 
                    [268, 180], [271, 178], [275, 177], [282, 175], [285, 174], [288, 173], [291, 172], [295, 172], [298, 171], [301, 171], 
                    [314, 170], [317, 169], [321, 170], [324, 170], [328, 169], [331, 170], [334, 170], [338, 170], [342, 170], [346, 170], 
                    [362, 172], [366, 172], [369, 173], [372, 173], [374, 174], [377, 174], [380, 175], [383, 176], [391, 181], [393, 182], 
                    [395, 184], [397, 186], [399, 186], [401, 187], [405, 190], [406, 191], [408, 193], [420, 210], [420, 212], [421, 216], 
                    [422, 218], [419, 232], [397, 230], [391, 229], [369, 224], [359, 222], [354, 219], [350, 218], [345, 216], [341, 212], 
                    [337, 205], [334, 196], [335, 124], [357, 85], [368, 69], [381, 51], [394, 37], [406, 25]]

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

detection = Detection("C:\\Users\\asus\\AlganYazilim_1.3\\Calismalar\\Behcet\\V5_best.pt")
kalman = KalmanFilter()

detection()
kalman()