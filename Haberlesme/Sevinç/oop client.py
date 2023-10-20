import cv2
import socket
import numpy as np
import time
import base64

class Client:
    def __init__(self):
        self.BUFF_SIZE = 65536
        self.host_ip =socket.gethostname()
        self.port = 9999
        self.message = b'Hello'
        self.fps, self.st, self.frames_to_count, self.cnt = (0, 0, 20, 0)

class Socket(Client):
    def __init__(self):
        super().__init__()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.BUFF_SIZE)
        self.client_socket.sendto(self.message, (self.host_ip, self.port))

def video(self):
    while True:
        self.packet, _ = self.client_socket.recvfrom(self.BUFF_SIZE)
        self.data = base64.b64decode(self.packet, '/')
        self.npdata = np.fromstring(self.data, dtype=np.uint8)
        self.frame = cv2.imdecode(self.npdata, 1)
        self.frame = cv2.putText(self.frame, 'FPS: ' + str(self.fps), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        self.cv2.imshow("RECEIVING VIDEO", self.frame)
        self.key = self.cv2.waitKey(1) & 0xFF
        if self.key == ord('q'):
            self.client_socket.close()
            break
        if self.cnt == self.frames_to_count:
            try:
                self.fps = round(self.frames_to_count / (time.time() - self.st))
                self.st = time.time()
                self.cnt = 0
            except:
                pass
            self.cnt += 1
if __name__=="__main__":
    client=Socket()
    client.video()