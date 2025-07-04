# This is client code to receive video frames over UDP
import cv2, imutils, socket
import numpy as np
import time
import base64

BUFF_SIZE = 65536
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP protokolü
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)  # UDP protokolü ayarları
host_name = socket.gethostname()  # cihaz adı (DESKTOP-TL66S3O)
host_ip = socket.gethostbyname(host_name)  # Client tarafında buraya server'ın ip'si yazılmalı
print(host_ip)
port = 9999
message = b'Hello'

client_socket.sendto(message, (
host_ip, port))  # Burada client tarafından ilk mesaj gönderiliyor böylelikle server tarafı isteğe sürekli cevap veriyor
fps, st, frames_to_count, cnt = (0, 0, 20, 0)
while True:
    packet, _ = client_socket.recvfrom(
        BUFF_SIZE)  # istemcinin adresini (IP adresi ve port numarası) ve gönderdiği mesajı döndürür.
    data = base64.b64decode(packet, ' /')  # server tarafından gelen base64lü mesajı çözümlüyor.
    npdata = np.fromstring(data,
                           dtype=np.uint8)  # metinsel bir formatta temsil edilen görüntü verisini NumPy dizisine dönüştürür
    frame = cv2.imdecode(npdata, 1)  # datayı çözümleyerek veri frame çevirir
    frame = cv2.putText(frame, 'FPS: ' + str(fps), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.imshow("RECEIVING VIDEO", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        client_socket.close()
        break
    if cnt == frames_to_count:
        try:
            fps = round(frames_to_count / (time.time() - st))
            st = time.time()
            cnt = 0
        except:
            pass
    cnt += 1
