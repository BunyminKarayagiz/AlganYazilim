import cv2
import imutils
import socket
import numpy as np
import base64
import time
from datetime import datetime

class VideoReceiver:
    def __init__(self,host_ip="10.80.1.60"):
        self.host_ip = host_ip
        self.port = 9999
        self.buff_size = 65536
        self.fps =30
        self.fourcc = 0x7634706d
        self.frames_to_count = 20
        self.frame_shape = False
        self.video_file_name = None
        self.fps, self.st, self.cnt = (0, 0, 0)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.buff_size)
        self.client_socket.sendto(b'Hello', (self.host_ip, self.port))

    def receive_and_save_video(self):
        while True:
            packet, _ = self.client_socket.recvfrom(self.buff_size)
            data = base64.b64decode(packet, ' /')
            npdata = np.fromstring(data, dtype=np.uint8)
            frame = cv2.imdecode(npdata, 1)
            frame = cv2.putText(frame, 'FPS: ' + str(self.fps), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            if self.cnt == self.frames_to_count:
                try:
                    self.fps = round(self.frames_to_count / (time.time() - self.st))
                    self.st = time.time()
                    self.cnt = 0
                except ZeroDivisionError:
                    pass
            self.cnt += 1

            if not self.frame_shape:
                now = datetime.now()
                time_str = now.strftime("%d%m%Y%H%M%S")
                time_name = '_Rec_' + time_str + '.mp4'
                self.video_file_name = str(self.host_ip) + time_name
                self.out = cv2.VideoWriter(self.video_file_name, self.fourcc, self.fps,
                                           (frame.shape[1], frame.shape[0]), True)
                self.frame_shape = True

            self.out.write(frame)
            cv2.imshow("RECEIVING VIDEO", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        self.client_socket.close()
        self.out.release()

if __name__ == "__main__":
    video_receiver = VideoReceiver()
    video_receiver.receive_and_save_video()