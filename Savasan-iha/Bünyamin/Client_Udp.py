import base64

import cv2
import imutils

from udp import UDP
class Client(UDP):

    def __init__(self, host):
        super().__init__()
        self.host = host
        self.vid = cv2.VideoCapture(0)
        self.WIDTH = 640
        self.HEIGHT = 480

    def send_video(self):
        try:
            if self.vid.isOpened():
                ret, frame = self.vid.read()
                frame = imutils.resize(frame, width=self.WIDTH, height=self.HEIGHT)
                encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                message = base64.b64encode(buffer)
                self.Main_socket.sendto(message, (self.host, self.port))
        except Exception as e:
            print("Video Gönderimi Koptu: ", e)
