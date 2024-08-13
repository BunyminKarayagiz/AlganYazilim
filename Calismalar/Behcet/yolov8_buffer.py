import os
import torch
import numpy as np
import cv2
from ultralytics import YOLO
from Calismalar.Behcet.kalmanfilter_eski import KalmanFilter
import multiprocessing
import concurrent.futures
import time


class Detection:

    def __init__(self, path):
        self.model = YOLO(path)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)
        self.frame_queue = multiprocessing.Queue(maxsize=10)
        self.stop_event = multiprocessing.Event()

    def model_predict(self, frame, frame_id):
        results = self.model.track(source=frame, conf=0.7, iou=0.5, show=False, tracker="botsort.yaml", verbose=False)

        pwm_verileri = np.array([1500, 1500, frame_id], dtype=np.uint32)
        
        x, y = frame.shape[0], frame.shape[1]

        target_area_y1, target_area_y2 = (int(x * 0.10), int(x * 0.90))
        target_area_x1, target_area_x2 = (int(y * 0.25), int(y * 0.75))

        cv2.rectangle(frame, (target_area_x1, target_area_y1), (target_area_x2, target_area_y2), (255, 0, 0), 2)

        locked_or_not = False
        if results:
            annotated_frame = results[0].plot()
            boxes = results[0].boxes.xyxy.cpu().tolist()

            for box in boxes:
                x1, y1, x2, y2 = box
                x_center = int((x1 + x2) / 2)
                y_center = int((y1 + y2) / 2)

                pwm_verileri = self.coordinates_to_pwm(x_center, y_center, frame_id)

                if (target_area_x1 < x1 and target_area_x2 > x2 and target_area_y1 < y1 and target_area_y2 > y2):
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
        else: 
            fark = 1500 - pwm_y
            pwm_y = 1500 + fark

        if x_center == 0 and y_center == 0:
            pwm_x = 1500
            pwm_y = 1500

        pwm_verileri = np.array([pwm_x, pwm_y, frame_id], dtype=np.uint32)
        return pwm_verileri

    def buffer_doldurma(self):
        cap = cv2.VideoCapture(0)
        frame_id = 0

        while not self.stop_event.is_set():
            ret, frame = cap.read()
            frame = cv2.flip(frame, -1)
            if ret:
                if self.frame_queue.full():
                    self.frame_queue.get()
                self.frame_queue.put((frame, frame_id)) 
                frame_id += 1

        cap.release()

    def buffer_process(self):
        kf = KalmanFilter()
        with concurrent.futures.ProcessPoolExecutor() as executor:
            print("with içine girdi!")
            while not self.stop_event.is_set() or not self.frame_queue.empty():
                print("while or içine girdi!")
                #! tüm sorun burada buranın içine girmiyor
                if self.frame_queue.qsize() >= 10:
                    frame, frame_id = self.frame_queue.get()
                    pwm_verileri, annotated_frame, locked_or_not = self.model_predict(frame, frame_id)

                    frames = [self.frame_queue.get() for _ in range(10)]
                    results = list(executor.map(self.buffer_doldurma, frames))
                    for pwm_verileri, annotated_frame in results:
                        print("for results içine girdi!")

                        predicted = kf.predict(pwm_verileri[0], pwm_verileri[1])
                        predict = {
                            'tahmin_x': predicted[0],
                            'tahmin_y': predicted[1]
                        }

                        if predicted is not None:
                            print("predict None içine girdi!")
                            cv2.circle(annotated_frame, (predicted[0], predicted[1]), 100, (0, 0, 255), -1)
                            cv2.imshow("YOLOv8 Tracking", annotated_frame)
                        
                        print("PWM Verileri:", pwm_verileri)
                        print(predict, "\n")

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    self.stop_event.set()

        cv2.destroyAllWindows()

    def __call__(self):
        fill_process = multiprocessing.Process(target=self.buffer_doldurma)
        process_process = multiprocessing.Process(target=self.buffer_process)

        fill_process.start()
        process_process.start()

        fill_process.join()
        process_process.join()

if __name__ == "__main__":
    detection = Detection("C:\\Users\\asus\\AlganYazilim\\Calismalar\\Behcet\\V5_best.pt")
    detection()
