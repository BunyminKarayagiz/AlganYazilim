import os
import torch
import numpy as np
import cv2
from ultralytics import YOLO


class Detection:

    def __init__(self, path):
        self.model = YOLO(path)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)

    def model_predict(self, frame,frame_id:int):
        #results = self.model.predict(frame, verbose=False)
        results = self.model.track(source=frame, conf=0.3, iou=0.5, show=False, tracker="botsort.yaml", verbose=False)
        # ----------------------detect/track etmediği durum için düzenlenecek----------------------------

        """pwm_verileri = {'pwmx': 1500, 'pwmy': 1500, 'rakip': 0, 'x': 0, 'y': 0, 'width': 0,
                            'height': 0}
        # pwm[rakip] = ekranda rakip detect ettiğimizde rakip 1 etmediğimizde 0 olacak
        # pwm[x] ve pwm[y] = tespit edilen rakibin x ve y koordiantindaki pikselleri
        # pwm[width] , pwm[height]= detect edilen rakip için çizilen dörtgenin yüksekliği ve genişliği        
        ------------------------------------------------------------------
        Yorum satirinda belirttiğim bilgiler pwm verilerine eklenmeli çünkü gödereceğimiz telemetri paketinde
        bu alanlari kullanacağimiz yerle mevcut. bknz.: haberleşme dökümani
        ----------------------------------------------------------------
        """

        """pwm_verileri = np.array([1500,1500,frame_id],dtype=np.uint32)"""
        # PWM_verisi = (pwm_x, pwm_y, frame_id, rakip, x_center, y_center, width, height)
        pwm_verileri:tuple = (1500,1500,frame_id,0,0,0,0,0)
        
        x, y = frame.shape[0], frame.shape[1]

        target_area_y1, target_area_y2 = (int(x * 0.10), int(x * 0.90))
        target_area_x1, target_area_x2 = (int(y * 0.25), int(y * 0.75))

        cv2.rectangle(frame, (target_area_x1, target_area_y1), (target_area_x2, target_area_y2), (0, 0, 255), 2) #RGB

        locked_or_not = False
        if results:
            annotated_frame = results[0].plot()

            boxes = results[0].boxes.xyxy.cpu().tolist()

            for box in boxes:
                x1, y1, x2, y2 = box
                x_center = int((x1 + x2) / 2)
                y_center = int((y1 + y2) / 2)
                width=x2-x1
                height=y2-y1
                pwm_verileri = self.coordinates_to_pwm(x_center, y_center,frame_id,width,height)

                if(target_area_x1<x1 and target_area_x2>x2 and target_area_y1<y1 and target_area_y2>y2):
                    locked_or_not = True

                return pwm_verileri, annotated_frame, locked_or_not
            
        return pwm_verileri, annotated_frame, locked_or_not

    def coordinates_to_pwm(self, x_center, y_center,frame_id,width,height):
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

        # pwm_verileri = {
        #                 'pwmx': pwm_x,
        #                 'pwmy': pwm_y,
        #                 'frame_id': frame_id
        #                 }
        
        # pwm_verileri = np.array([pwm_x,pwm_y,frame_id],dtype=np.uint32)_
        pwm_verileri:tuple = (pwm_x, pwm_y, frame_id, 1, x_center, y_center, width, height)  # X_center ve Y_center tespit edilen rakibin x y koordinatını verir. 1 değeri ise rakibin var olduğunu belli eder.

        return pwm_verileri


"""    def __call__(self):

        cap = cv2.VideoCapture(0)  # webcam

        while True:
            ret, frame = cap.read()

            if ret:
                frame = cv2.resize(frame, (640, 480))
                pwm_verileri, annotated_frame, locked_or_not = self.model_predict(frame)
                cv2.imshow("YOLOv8 Tracking", annotated_frame)
                print("PWM Verileri: ", pwm_verileri)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()


detection = Detection("C:\\Users\\asus\\AlganYazilim\\Savasan-iha\\Mustafa Berkay\\Model2024_V1.pt")
detection()"""
