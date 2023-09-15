import base64
import socket

import cv2
import numpy as np
import imutils


class UDP:
    def __init__(self):
        self.BUFF_SIZE = 65536  # Kullanılabilecek veri bellek boyutu
        self.Main_socket = socket.socket(socket.AF_INET,
                                         socket.SOCK_DGRAM)  # UDP için temel tanımlama   " (socket.SOCK_DGRAM) ifadesi udp olduğunu belirtiyor."
        self.Main_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.BUFF_SIZE)  # UDP için temel tanımlama
        self.port = 9999


class Udp_Server(UDP):

    def __init__(self):
        super().__init__()
        self.host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name)

    def create_server(self):
        self.socket_adress = (self.host_ip, self.port)
        self.Main_socket.bind(self.socket_adress)
        print('Listening at:', self.socket_adress)

    def recv_from_client(self):
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


class Udp_Client(UDP):

    def __init__(self, host):
        super().__init__()
        self.host = host
        self.vid = cv2.VideoCapture(0)
        self.WIDTH = 640
        self.HEIGHT = 480

    def send_video(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            frame = imutils.resize(frame, width=self.WIDTH, height=self.HEIGHT)
            encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            message = base64.b64encode(buffer)
            self.Main_socket.sendto(message, (self.host, self.port))

class Udp_Bussiness():
    def __init__(self,host):
        self.server=Udp_Server()
        self.client=Udp_Client(host)

    def __call__(self, *args, **kwargs):
        self.server.create_server()
        while True:
            self.client.send_video()
            frame = self.server.recv_from_client()
            self.server.show(frame)

"""if __name__ == '__main__':
    server = Udp_Server()
    client = Udp_Client("192.168.1.30")

    server.create_server()

    while True:
        client.send_video()
        frame = server.recv_from_client()
        server.show(frame)"""

bussiness=Udp_Bussiness("192.168.1.30")
bussiness()