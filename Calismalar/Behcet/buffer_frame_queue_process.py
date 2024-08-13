import cv2
import numpy as np
import multiprocessing as mp

# Buffer boyutu
buffer_size = 10
camera = 0

# Kamera okuma fonksiyonu
def read_camera(frame_queue, stop_event):
    cap = cv2.VideoCapture(camera)  # Webcam kullanımı

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_queue.full():
            frame_queue.get()  # Buffer doluysa en eski çerçeveyi çıkar

        frame_queue.put(frame)  # Yeni çerçeveyi buffer'a ekle

    cap.release()

# Görüntü işleme fonksiyonu
def process_frames(frame_queue, stop_event):

    while not stop_event.is_set():
        if frame_queue.qsize() >= 5:  # Buffer'da en az 5 görüntü varsa
            frames = []
            
            for _ in range(5):
                frames.append(frame_queue.get())  # Buffer'dan son 5 görüntüyü al

            # Son 5 görüntüyü ekranda göster
            for i, frame in enumerate(frames):
                cv2.imshow(f"Frame {i+1}", frame)

            # Her görüntüyü sırayla göstermek için bir süre bekle
            cv2.waitKey(1000)  # 1 saniye bekle

            # Gösterilen görüntüleri kapat
            for i in range(5):
                cv2.destroyWindow(f"Frame {i+1}")

        if cv2.waitKey(1) & 0xFF == ord("q"):
            stop_event.set()
            break
        
    cv2.destroyAllWindows()

if __name__ == "__main__":
    frame_queue = mp.Queue(maxsize=buffer_size)
    stop_event = mp.Event()

    read_process = mp.Process(target=read_camera, args=(frame_queue, stop_event))
    process_process = mp.Process(target=process_frames, args=(frame_queue, stop_event))

    # Process'leri başlat
    read_process.start()
    process_process.start()

    # Process'lerin tamamlanmasını bekle
    read_process.join()
    process_process.join()