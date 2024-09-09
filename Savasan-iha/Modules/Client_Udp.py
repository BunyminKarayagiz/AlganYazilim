import base64
import socket
import cv2
import imutils
       

class Client():

    def __init__(self, host, port):
        self.BUFF_SIZE = 65536  # Kullanılabilecek veri bellek boyutu
        self.Main_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)  # UDP için temel tanımlama   " (socket.SOCK_DGRAM) ifadesi udp olduğunu belirtiyor."
        self.Main_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.BUFF_SIZE)
        
        self.host = host
        self.port = port #9999
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
