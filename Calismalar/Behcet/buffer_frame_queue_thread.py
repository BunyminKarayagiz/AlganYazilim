#! Kalman filtresi için buffer üzerinden frame çekme.

import cv2
import numpy as np
import queue
import threading

# Buffer oluştur
buffer_size = 10  # Buffer boyutu
frame_buffer = queue.Queue(maxsize=buffer_size)

# Kameradan okuma ve durduma 
stop_event = threading.Event()

# Kamera okuma fonksiyonu
def read_camera():
    cap = cv2.VideoCapture(0)  # Webcam kullanımı

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_buffer.full():
            frame_buffer.get()  # Buffer doluysa en eski çerçeveyi çıkar

        frame_buffer.put(frame)  # Yeni çerçeveyi buffer'a ekle

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()

# Görüntü işleme fonksiyonu
"""def process_frames():
    while True:
        if not frame_buffer.empty():
            frame = frame_buffer.get()  # Buffer'dan bir çerçeve al

            # Burada görüntü işleme kodunuzu ekleyin
            cv2.imshow("Processed Frame", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            stop_event.set()
            break
    cv2.destroyAllWindows()"""

    #! buffer üzerinden çekilen son 5 frame. her biri 1 saniye boyunca gösterilecek
def process_frames():
    while not stop_event.is_set():
        if frame_buffer.qsize() >= 5:  # Buffer'da en az 5 görüntü varsa
            frames = []
            for _ in range(5):
                frames.append(frame_buffer.get())  # Buffer'dan son 5 görüntüyü al
            
            # Son 5 görüntüyü ekranda göster
            for i, frame in enumerate(frames):
                cv2.imshow(f"Frame {i+1}", frame)
            
            """# Her görüntüyü sırayla göstermek için bir süre bekle
            cv2.waitKey(1000)  # 1 saniye bekle"""

            # Gösterilen görüntüleri kapat
            for i in range(5):
                cv2.destroyWindow(f"Frame {i+1}")
            
        if cv2.waitKey(1) & 0xFF == ord("q"):
            stop_event.set()
            break
        
    cv2.destroyAllWindows()

# Okuma ve işleme için iki ayrı thread oluştur
read_thread = threading.Thread(target=read_camera)
process_thread = threading.Thread(target=process_frames)

# Thread'leri başlat
read_thread.start()
process_thread.start()

# Thread'lerin tamamlanmasını bekle
read_thread.join()
process_thread.join()