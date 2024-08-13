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

detection = Detection("C:\\Users\\asus\\AlganYazilim_1.3\\Calismalar\\Behcet\\V5_best.pt")
detection()