import base64
import socket

import cv2
import numpy as np

class Server():
 #65536
 #1000000
    def __init__(self):
        self.BUFF_SIZE = 65536   # Kullanılabilecek veri bellek boyutu
        self.udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)  # UDP için temel tanımlama 
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.BUFF_SIZE)  # UDP için temel tanımlama
        self.port = 9998

        self.host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name)

    def create_server(self):
        self.udp_socket.bind((self.host_ip, self.port))
        print('Listening at:', (self.host_ip, self.port))

    def recv_frame_from_client(self):
        message , sender_adress = self.udp_socket.recvfrom(self.BUFF_SIZE)
        data = base64.b64decode(message, ' /')
        npdata = np.fromstring(data, dtype=np.uint8)
        frame = cv2.imdecode(npdata, 1)  # datayı çözümleyerek veri frame çevirir
        return frame

    def show(self, frame):
        cv2.imshow("server Video", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            self.udp_socket.close()
