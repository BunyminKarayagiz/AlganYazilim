import cv2, imutils, socket
import numpy as np
import time
import base64

BUFF_SIZE = 65536
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP protokolü
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)  # UDP protokolü ayarları

host_name = socket.gethostname()  # cihaz adı (DESKTOP-TL66S3O)
host_ip = socket.gethostbyname(host_name)  # Client tarafında buraya server'ın ip'si yazılmalı
port = 9999

vid = cv2.VideoCapture(0)
WIDTH = 640
HEIGHT = 480
while True:
    if vid.isOpened():
        ret, frame = vid.read()
        frame = imutils.resize(frame, width=WIDTH, height=HEIGHT)
        encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        message = base64.b64encode(buffer)
        client_socket.sendto(message, (host_ip, port))
        cv2.imshow("client", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            client_socket.close()
            break
