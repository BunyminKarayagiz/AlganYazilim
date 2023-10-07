import os
from datetime import datetime

import torch
import numpy as np
import cv2
import time
import re
from pyzbar import pyzbar
import hesaplamalar

class Detector:
    detectorObj = None

    def __init__(self, capture_index, model_name, vid_out):
        self.capture_index = capture_index
        self.vid_out = vid_out
        self.model = self.load_model(model_name)
        self.classes = self.model.names
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)

    def get_video_capture(self):
        return cv2.VideoCapture(self.capture_index)

    def load_model(self, model_name):
        modelName = "bestuçak.pt"
        if model_name:
            model = torch.hub.load((os.getcwd()) + "\\ultralytics_yolov5_master", 'custom', source='local',
                                   path=modelName, force_reload=True)
        return model

    def score_frame(self, frame):
        self.model.to(self.device)
        frame = [frame]
        results = self.model(frame)
        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        return labels, cord

    def class_to_label(self, x):
        return self.classes[int(x)]

    def plot_boxes(self, results, frame):
        global count
        labels, cord = results
        bgr1 = (120, 120, 120)
        bgr = (0, 0, 255)
        bgr2 = (0, 184, 255)
        disx1, disx2, disy1, disy2 = int(frame.shape[1] * 0.25), int(frame.shape[1] * 0.75), int(
            frame.shape[0] * 0.10), int(frame.shape[0] * 0.90)
        cv2.rectangle(frame, (disx1, disy1), (disx2, disy2), (0, 0, 255), 1)
        centerOfRectx = int((disx1 + disx2) / 2)
        centerOfRecty = int((disy1 + disy2) / 2)
        centerOfRect = (int((disx1 + disx2) / 2), int((disy1 + disy2) / 2))


        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        maximum_alan = 0
        center = centerOfRect

        xCord = 0
        yCord = 0
        width = 0
        height = 0
        lockedOrNot = 0

        for i in range(n):
            row = cord[i]
            x1, y1, x2, y2 = int(row[0] * x_shape), int(row[1] * y_shape), int(row[2] * x_shape), int(row[3] * y_shape)
            alan = (x2 - x1) * (y2 - y1)
            width = x2 - x1
            height = y2 - y1
            # time1 = time.time() - counter

            if (width > 32 or height > 24):
                if row[4] >= 0.735 and alan >= maximum_alan:
                    #print(alan)
                    maximum_alan = alan
                    counterCoefficient = 0
                    xCord = (int(x1 + width / 2))
                    yCord = (int(y1 + height / 2))
                    center = centerOfRect
                    center2 = (xCord, yCord)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 1)
                    cv2.putText(frame, self.class_to_label(labels[i]) + f" {round(float(row[4]), 2)}",
                                (x1, y1),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, bgr, 2)
                    cv2.circle(frame, center2, 2, (bgr2), -1)
                    cv2.line(frame, (centerOfRect), (center2), (bgr2), 1)

                    if (disx1 < x1 and disy1 < y1 and disx2 > x2 and disy2 > y2) and self.class_to_label(
                            labels[i]) != "":
                        disx1, disx2, disy1, disy2 = int(frame.shape[1] * 0.25), int(frame.shape[1] * 0.75), int(
                            frame.shape[0] * 0.10), int(frame.shape[0] * 0.90)
                        cv2.rectangle(frame, (disx1, disy1), (disx2, disy2), (0, 255, 0), 2)
                        lockedOrNot = 1

                    return 1, center, xCord, yCord, width, height, frame, lockedOrNot

        return 0, center, xCord, yCord, width, height, frame, lockedOrNot

    def qr_detection(self, imgOriginal):
        x1, x2, y1, y2 = int(imgOriginal.shape[1] * 0.25), int(imgOriginal.shape[1] * 0.75) \
            , int(imgOriginal.shape[0] * 0.10), int(
            imgOriginal.shape[0] * 0.90)  # Gelen videoya dikdörtgen çizmek için koordinat almaktadır

        roi = imgOriginal[y1:y2,x1:x2]  # Roi değişkeni orijinal resim içine çizilen dörtgenin arasındaki görüntüyü alır.

        #qr_code_list = pyzbar.decode(roi)

        qr_code_list=pyzbar.decode(imgOriginal)  #640x480 için

        cv2.rectangle(imgOriginal, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Gelen videoya dikdörtgen çizmektedir

        for qr_code in qr_code_list:
            data = qr_code.data.decode("utf-8")
            print(data)
            pts = np.array([qr_code.polygon], np.int32)
            pts = pts.reshape((-1, 1, 2))
            #cv2.polylines(roi, [pts], True, (255, 0, 255), 5)
            cv2.polylines(imgOriginal, [pts], True, (255, 0, 255), 5)
            pts2 = qr_code.rect

            cv2.putText(imgOriginal, data, (pts2[0], pts2[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 255), 2)
            #cv2.putText(roi, data, (pts2[0], pts2[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 255), 2)

            if data != None:
                x1, x2, y1, y2 = int(imgOriginal.shape[1] * 0.25), int(imgOriginal.shape[1] * 0.75) \
                    , int(imgOriginal.shape[0] * 0.10), int(imgOriginal.shape[0] * 0.90)
                cv2.rectangle(imgOriginal, (x1, y1), (x2, y2), (0, 255, 0), 2)

            return qr_code.data, imgOriginal

        return None, imgOriginal

    def __call__(self):
        print(f"[INFO] Working with video: {self.capture_index}")

        cap = self.get_video_capture()

        width1 = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height1 = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        codec = cv2.VideoWriter_fourcc(*'mp4v')  ##(*'XVID')
        out = cv2.VideoWriter(self.vid_out, codec, fps, (width1, height1))
        frame_no = 1

        cv2.namedWindow("vid_out", cv2.WINDOW_NORMAL)
        while True:
            ret, frame = cap.read()
            if ret:
                """print(f"[INFO] Working with frame {frame_no} ")"""

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.score_frame(frame)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                aaaa,center, xxx, yyy, width, height, frame,boul = self.plot_boxes(results, frame)
                print(str(xxx) + " pwm     " + str(yyy) + " pwm")
                #_, frame = self.qr_detection(frame)
                # cv2.imshow("vid_out", frame)
                pwmX, pwmY = hesaplamalar.yonver(xxx, yyy, width, height, 100)

                """print(pwmX, pwmY)"""

                cv2.imshow("vid_out", frame)

                """if self.vid_out:
                    print(f"[INFO] Saving output video. . . ")
                    out.write(frame)"""

                if cv2.waitKey(1) & 0xFF == 27:
                    break
                frame_no += 1

        """print(f"[INFO] Clening up. . . ")"""
        ### releaseing the writer
        out.release()
        cv2.destroyAllWindows()


detector = Detector(capture_index=0, model_name="bestuçak.pt", vid_out="out.mp4")
Detector.detectorObj = detector
"""detector()"""
