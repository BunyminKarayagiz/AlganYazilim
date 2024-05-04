import cv2
from ultralytics import YOLO
import torch


class Detection:

    def __init__(self):
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
        xCord = 0
        yCord = 0
        rival_statement = 0
        disx1, disx2, disy1, disy2 = int(frame.shape[1] * 0.25), int(frame.shape[1] * 0.75), int(
            frame.shape[0] * 0.10), int(frame.shape[0] * 0.90)
        cv2.rectangle(frame, (disx1, disy1), (disx2, disy2), (0, 0, 255), 2)
        results = self.predict(frame)
        for result in results:
            boxes = result.boxes.cpu().numpy()
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0][0].astype(int), box.xyxy[0][1].astype(int), box.xyxy[0][2].astype(int), \
                                 box.xyxy[0][3].astype(int)
                width = x2 - x1
                height = y2 - y1
                xCord = (int(x1 + width / 2))
                yCord = (int(y1 + height / 2))
                center2 = (xCord, yCord)
                if box.conf[0] > 0.7:
                    """frame = results[0].plot()"""
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.circle(frame, center2, 1, (0, 0, 0), -1)
                    print(center2)
                    rival_statement = 1
                return frame, xCord, yCord, rival_statement
        return frame, xCord, yCord, rival_statement

    def coordinates_to_pwm(self, frame):

        screen_width = 640
        screen_height = 480
        min_pwm = 1100
        max_pwm = 1900
        frame, xCord, yCord, rival_statement = self.plot_bboxes(frame)
        pwm_x = int((xCord / screen_width) * (max_pwm - min_pwm) + min_pwm)
        pwm_y = int((yCord / screen_height) * (max_pwm - min_pwm) + min_pwm)

        if xCord == 0 and yCord == 0:
            pwm_x = 1500
            pwm_y = 1500

        print("PWM Signal for X-Axis:", pwm_x)
        print("PWM Signal for Y-Axis:", pwm_y)
        return pwm_x, pwm_y

    def __call__(self):
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if ret:
                frame, xCord, yCord, rival_statement = self.plot_bboxes(frame)
                cv2.imshow("vid_out", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    break

        cv2.destroyAllWindows()


d1 = Detection()
d1()



