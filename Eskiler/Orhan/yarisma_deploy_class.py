import cv2
from ultralytics import YOLO
import torch
import time
import numpy as np


class Detection:
    def __init__(self, capture_index):
        self.capture_index = capture_index
        self.model = self.load_model()
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)

    def load_model(self):
        model = YOLO("yolov8best.pt")
        model.fuse()

        return model

    def predict(self, frame):

        results = self.model(frame)

        return results

    def plot_bboxes(self, frame):
        disx1, disx2, disy1, disy2 = int(frame.shape[1] * 0.25), int(frame.shape[1] * 0.75), int(
            frame.shape[0] * 0.10), int(frame.shape[0] * 0.90)
        cv2.rectangle(frame, (disx1, disy1), (disx2, disy2), (0, 0, 255), 2)
        results = self.predict(frame)
        for result in results:
            boxes = result.boxes.cpu().numpy()
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0][0].astype(int), box.xyxy[0][1].astype(int), box.xyxy[0][2].astype(int), \
                                 box.xyxy[0][3].astype(int)
                if disx1 < x1 and disy1 < y1 and disx2 > x2 and disy2 > y2:
                    cv2.rectangle(frame, (disx1, disy1), (disx2, disy2), (0, 255, 0), 2)
            frame = results[0].plot()
        return frame

    def __call__(self):

        cap = cv2.VideoCapture(self.capture_index)
        assert cap.isOpened()
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        while True:

            start_time = time.time()

            ret, frame = cap.read()
            assert ret
            
            frame = self.plot_bboxes(frame)

            end_time = time.time()
            fps = 1 / np.round(end_time - start_time, 2)

            cv2.putText(frame, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            cv2.imshow('YOLOv8 Detection', frame)

            if cv2.waitKey(5) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()


detector = Detection(capture_index=0)
detector()

