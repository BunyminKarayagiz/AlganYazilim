import base64
import socket
import av
from av import packet
import cv2
import numpy as np

class Server():
 #65536
 #1000000
    def __init__(self,port=5555,name="UNNAMED"):
        self.BUFF_SIZE = 65536   # Kullanılabilecek veri bellek boyutu
        self.udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)  # UDP için temel tanımlama 
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.BUFF_SIZE)  # UDP için temel tanımlama
        self.port = port
        self.name = name

        self.host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name)

    def create_server(self):
        self.udp_socket.bind((self.host_ip, self.port))
        print(f'{self.name} Server Listening at:', (self.host_ip, self.port))

    def recv_frame_from_client(self):
        frame , sender_adress = self.udp_socket.recvfrom(self.BUFF_SIZE)
        #! SADECE LOCALDE ÇALIŞTIRMAK İÇİN
        # frame = base64.b64decode(frame, ' /')
        # npdata = np.fromstring(frame, dtype=np.uint8)
        # frame = cv2.imdecode(npdata, 1)  # datayı çözümleyerek veri frame çevirir
        return frame

    def send_frame_to_client(self,frame): #! Denenmedi. Düzeltilmesi gerekebilir...
        self.conn.sendto(frame.tobytes())


    def close_socket(self):
        self.udp_socket.close()


    def show(self, frame):
        cv2.imshow("Yer_istasyonu Video", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            self.udp_socket.close()
