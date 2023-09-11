# This is server code to send video frames over UDP
import cv2, imutils, socket
import numpy as np
import time
import base64

BUFF_SIZE = 65536
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP protokolü
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)  # UDP protokolü ayarları
host_name = socket.gethostname()  # cihaz adı (DESKTOP-TL66S3O)
host_ip = socket.gethostbyname(host_name)  # Bizim İP'miz
print(host_ip)
port = 9999
socket_address = (host_ip, port)  # ip ve portu tuple hale getiriyoruz
server_socket.bind(socket_address)  # Artık dinleme işlemi yapılıyor bu ip ve port üzerinden
print('Listening at:', socket_address)

vid = cv2.VideoCapture(0)  # WebCam açıyor
fps, st, frames_to_count, cnt = (0, 0, 20, 0)

while True:
    msg, client_addr = server_socket.recvfrom(
        BUFF_SIZE)  # istemcinin adresini (IP adresi ve port numarası) ve gönderdiği mesajı döndürür.
    print('GOT connection from ', client_addr)
    WIDTH = 640
    HEIGHT = 480
    while (vid.isOpened()):
        _, frame = vid.read()
        frame = imutils.resize(frame, width=WIDTH, height=HEIGHT)
        encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY,
                                                       80])  # encoded bize boole değer döndürür. çevirme doğru ise True.# Buffer ise çevrilen framenin bayt dizsini

        message = base64.b64encode(
            buffer)  # buffer adlı bayt dizisini Base64 kodlaması kullanarak metinsel bir formata çevirir. Base64 kodlaması, binary veriyi metinsel karakterlerden oluşan bir formata dönüştürerek veriyi metin tabanlı iletişim araçları üzerinde daha güvenli ve kullanılabilir hale getirir.
        server_socket.sendto(message, client_addr)  # Mesajı verilen adrese gönderiyor
        frame = cv2.putText(frame, 'FPS: ' + str(fps), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow('TRANSMITTING VIDEO', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            server_socket.close()
            break
        if cnt == frames_to_count:
            try:
                fps = round(frames_to_count / (time.time() - st))
                st = time.time()
                cnt = 0
            except:
                pass
        cnt += 1
