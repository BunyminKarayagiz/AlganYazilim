import os
import torch
import numpy as np
import cv2
from ultralytics import YOLO

class Detection2:
 
    def __init__(self, path):
        self.model = YOLO(path)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)

    def model_predict(self, frame, frame_id=0):
        results = self.model.track(source=frame, conf=0.8, iou=0.5, show=False, tracker="botsort.yaml", verbose=False)

        # pwm_veriler = (frame_id, iha_kilitlenme, hedef_merkez_x, hedef_merkez_y, hedef_genislik, hedef_yukseklik)
        telemetri_verileri:tuple = (frame_id, 0, 0, 0, 0, 0)
        kalman_data:tuple = (0, 0 ,0)
        
        x, y = frame.shape[0], frame.shape[1]

        target_area_y1, target_area_y2 = (int(x * 0.10), int(x * 0.90))
        target_area_x1, target_area_x2 = (int(y * 0.25), int(y * 0.75))

        cv2.rectangle(frame, (target_area_x1, target_area_y1), (target_area_x2, target_area_y2), (0, 0, 255), 2) # RGB

        locked_or_not = False
        highest_confidence = 0
        best_box = None

        if results:
            annotated_frame = results[0].plot()
            boxes = results[0].boxes.xyxy.cpu().tolist()
            confidences = results[0].boxes.conf.cpu().tolist()

            for box, conf in zip(boxes, confidences):
                if conf > highest_confidence:
                    highest_confidence = conf
                    best_box = box

            if best_box:
                x1, y1, x2, y2 = best_box
                x_center = int((x1 + x2) / 2)
                y_center = int((y1 + y2) / 2)
                box_width = x2 - x1
                box_height = y2 - y1

                kalman_data = (x_center, y_center,1)
                telemetri_verileri = (frame_id, 1, x_center, y_center, box_width, box_height)

                if (box_width >= x*0.05) and (box_height >= y*0.05):

                    if(target_area_x1 < x1 and target_area_x2 > x2 and target_area_y1 < y1 and target_area_y2 > y2):
                        locked_or_not = True

                    return telemetri_verileri,  kalman_data, annotated_frame, locked_or_not

        return telemetri_verileri, kalman_data, annotated_frame, locked_or_not
    
    def coordinates_to_pwm(self, x_center, y_center, frame_id, width, height):
        screen_width = 640
        screen_height = 480
        min_pwm = 1100
        max_pwm = 1900
        
        pwm_x = int((x_center / screen_width) * (max_pwm - min_pwm) + min_pwm)
        pwm_y = int((y_center / screen_height) * (max_pwm - min_pwm) + min_pwm)

        if pwm_y > 1500:
            fark = pwm_y - 1500
            pwm_y = 1500 - fark
        else: 
            fark = 1500 - pwm_y
            pwm_y = 1500 + fark

        if x_center == 0 and y_center == 0:
            pwm_x = 1500
            pwm_y = 1500

        pwm_verileri:tuple = (pwm_x, pwm_y, frame_id, 1, x_center, y_center, width, height)

        return pwm_verileri

    """def __call__(self):
        cap = cv2.VideoCapture(0)  # webcam

        while True:
            ret, frame = cap.read() 

            if ret:
                frame = cv2.resize(frame, (640, 480))
                pwm_verileri, annotated_frame, locked_or_not, kalmanPWM = self.model_predict(frame)
                cv2.imshow("YOLOv8 Tracking", annotated_frame)
                print("PWM Verileri: ", pwm_verileri)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

detection = Detection("C:\\Users\\asus\\AlganYazilim\\Calismalar\\Behçet\\Kalman_Filter\\KALMAN NİHAİ\\Model_2024_V6_best.pt")
detection()"""