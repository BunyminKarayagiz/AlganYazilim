import cv2, imutils, socket
import numpy as np
import time
import base64

BUFF_SIZE = 65536
server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 			# UDP protokolü
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE) 		# UDP protokolü ayarları

host_name = socket.gethostname() 											# cihaz adı (DESKTOP-TL66S3O)
host_ip = socket.gethostbyname(host_name) 									# Bizim İP'miz


port = 9999
socket_address = (host_ip,port) 											# ip ve portu tuple hale getiriyoruz
server_socket.bind(socket_address) 											# Artık dinleme işlemi yapılıyor bu ip ve port üzerinden
print('Listening at:',socket_address)

while True:
    msg,client_adres=server_socket.recvfrom(BUFF_SIZE)
    data = base64.b64decode(msg, ' /')
    npdata = np.fromstring(data, dtype=np.uint8)
    frame = cv2.imdecode(npdata, 1)  # datayı çözümleyerek veri frame çevirir
    cv2.imshow("server VIDEO", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        server_socket.close()
        break