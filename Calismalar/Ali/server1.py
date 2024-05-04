import cv2
import imutils
import socket
import numpy as np
import time
import base64

class VideoSender:
    def __init__(self,host_ip="10.80.1.60"):
        self.host_ip = host_ip
        self.port = 9999
        self.buff_size = 65536
        self.fps, self.st, self.frames_to_count, self.cnt = (0,0,20,0)
        self.frames_to_count = 20
        self.WIDTH = 400
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.buff_size)
        self.socket_address = (self.host_ip, self.port)
        self.server_socket.bind(self.socket_address)
        print('Listening at:', self.socket_address)
        self.vid = cv2.VideoCapture(0)  #  replace 'rocket.mp4' with 0 for webcam
    def send_video(self):
        while True:
            msg, client_addr = self.server_socket.recvfrom(self.buff_size)
            print('GOT connection from ', client_addr)

            while (self.vid.isOpened()):
                _, frame = self.vid.read()
                frame = imutils.resize(frame, width=self.WIDTH)
                encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                self.message = base64.b64encode(buffer)
                self.server_socket.sendto(self.message, client_addr)
                frame = cv2.putText(frame, 'FPS: ' + str(self.fps), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow('TRANSMITTING VIDEO', frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.server_socket.close()
                    break

                if self.cnt == self.frames_to_count:
                    try:
                        self.fps = round(self.frames_to_count / (time.time() - self.st))
                        self.st = time.time()
                        self.cnt = 0
                    except ZeroDivisionError:
                        pass
                self.cnt += 1


if __name__ == "__main__":
    video_sender = VideoSender()
    video_sender.send_video()