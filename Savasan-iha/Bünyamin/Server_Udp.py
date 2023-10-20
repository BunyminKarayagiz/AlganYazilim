import base64
import socket

import cv2
import numpy as np

from udp import UDP

class Server(UDP):

    def __init__(self):
        super().__init__()
        self.host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name)

    def create_server(self):
        self.socket_adress = (self.host_ip, self.port)
        self.Main_socket.bind(self.socket_adress)
        print('Listening at:', self.socket_adress)

    def recv_frame_from_client(self):
        msg, client_adress = self.Main_socket.recvfrom(self.BUFF_SIZE)
        print("mesaj alındı : ", client_adress)
        data = base64.b64decode(msg, ' /')
        npdata = np.fromstring(data, dtype=np.uint8)
        frame = cv2.imdecode(npdata, 1)  # datayı çözümleyerek veri frame çevirir
        return frame

    def show(self, frame):
        cv2.imshow("server VIDEO", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            self.Main_socket.close()

