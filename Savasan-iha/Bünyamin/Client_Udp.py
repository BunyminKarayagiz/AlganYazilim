import base64
import time

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
        except Exception as err:
            print("Video Gönderimi Koptu: ", err)
            self.Main_socket.close()
            connected= False
            udp_haberlesme_obj=Client(self.host)
            while not connected:
                try:
                    udp_haberlesme_obj.Main_socket.settimeout(0.001)
                    connected=True
                except Exception as err:
                    print("Video verisi koptu", err)
                    time.sleep(1)
                    pass

