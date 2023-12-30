import os
import torch
import numpy as np
import cv2


class Detection:

    def __init__(self, capture_index, model_name):
        self.model = self.load_model(model_name)
        self.capture_index = capture_index
        self.classes = self.model.names
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)

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

    def get_results(self,frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.score_frame(frame=frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return results,frame
    def class_to_label(self, x):
        return self.classes[int(x)]

    def plot_boxes(self,results,frame):
        labels, cord = results
        disx1, disx2, disy1, disy2 = int(frame.shape[1] * 0.25), int(frame.shape[1] * 0.75), int(
            frame.shape[0] * 0.10), int(frame.shape[0] * 0.90)
        cv2.rectangle(frame, (disx1, disy1), (disx2, disy2), (0, 0, 255), 1)
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        lockedOrNot = 0
        xCord = 0
        yCord = 0
        for i in range(n):
            row = cord[i]
            x1, y1, x2, y2 = int(row[0] * x_shape), int(row[1] * y_shape), int(row[2] * x_shape), int(row[3] * y_shape)
            width = x2 - x1
            height = y2 - y1
            xCord = (int(x1 + width / 2))
            yCord = (int(y1 + height / 2))

            if width > 32 or height > 24:

                if row[4] >= 0.735:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)

                    if (disx1 < x1 and disy1 < y1 and disx2 > x2 and disy2 > y2) and self.class_to_label(
                            labels[i]) != "":
                        disx1, disx2, disy1, disy2 = int(frame.shape[1] * 0.25), int(frame.shape[1] * 0.75), int(
                            frame.shape[0] * 0.10), int(frame.shape[0] * 0.90)
                        cv2.rectangle(frame, (disx1, disy1), (disx2, disy2), (0, 255, 0), 2)
                        lockedOrNot = 1
                    return xCord, yCord, frame, lockedOrNot

        return  xCord, yCord, frame, lockedOrNot

    def coordinates_to_pwm(self,xCord,yCord):
        screen_width = 640
        screen_height = 480
        min_pwm = 1100
        max_pwm = 1900
        pwm_x = int((xCord / screen_width) * (max_pwm - min_pwm) + min_pwm)
        pwm_y = int((yCord / screen_height) * (max_pwm - min_pwm) + min_pwm)

        if xCord == 0 and yCord == 0:
            pwm_x = 1500
            pwm_y = 1500

        #print("PWM Signal for X-Axis:", pwm_x)
        #print("PWM Signal for Y-Axis:", pwm_y)
        pwm_verileri = {'pwmx': pwm_x,
                        'pwmy': pwm_y}
        return pwm_verileri

    def __call__(self):

        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.score_frame(frame)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                xCord, yCord, frame, lockedOrNot = self.plot_boxes(results, frame)
                cv2.imshow("vid_out", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    break

        cv2.destroyAllWindows()


"""detector = Detection(capture_index=0, model_name="bestuçak.pt")
detector()"""
