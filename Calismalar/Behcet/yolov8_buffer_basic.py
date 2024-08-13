from ultralytics import YOLO
import cv2
import cvzone
import math
import time
import numpy as np
import queue
from Calismalar.Behcet.kalmanfilter_eski import KalmanFilter

classNames = ["UAV"]

buffer_size = 10
prev_frame_time = 0
new_frame_time = 0

cap = cv2.VideoCapture(0)  # For Webcam
cap.set(3, 640)
cap.set(4, 480)

# cap = cv2.VideoCapture("hareketli_ucak2.mp4")
# video kayıt için fourcc ve VideoWriter tanımlama
cv2_fourcc = cv2.VideoWriter_fourcc(*'mp4v')
success, img = cap.read()
print(img.shape)
yukseklik = img.shape[0]
genislik = img.shape[1]

img = cv2.flip(img, 1)

cv2.imwrite("C:\\Users\\asus\\Desktop\\Algan\\ileri\\ornek_resim.jpg", img)
size = list(img.shape)
del size[2]
size.reverse()
video = cv2.VideoWriter("C:\\Users\\asus\\video.mp4", cv2_fourcc, 24, size) #output video name, fourcc, fps, size

model = YOLO("C:\\Users\\asus\\AlganYazilim\\Calismalar\\Behcet\\V5_best.pt")

buffer = queue.Queue(maxsize=buffer_size)
konum_verileri = []

while True:
    kf = KalmanFilter()
    ret, frame = cap.read()


    if ret:
        new_frame_time = time.time()
        success, img = cap.read()

        img = cv2.resize(img, (1280, 720), interpolation=cv2.INTER_AREA)

        results = model(img, stream=True)
        for r in results:
            boxes = r.boxes
            for box in boxes: 

                # Bounding Box
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                # cv2.rectangle(img,(x1,y1),(x2,y2),(255,0,255),3)
                w, h = x2 - x1, y2 - y1

                x_center = x2 - x1
                y_center = y2 - y1

                rakip_verileri = [x_center, y_center]

                # Confidence
                conf = math.ceil((box.conf[0] * 100)) / 100
                # Class Name
                cls = int(box.cls[0])

                currentClass = classNames[cls]

                if currentClass == "UAV" and conf >= 0.7:
                    cvzone.cornerRect(img, (x1, y1, w, h))
                    cvzone.putTextRect(img, f'{classNames[cls]} {conf}', (max(0, x1), max(35, y1)), scale=1, thickness=1)

                    cx, cy = x1 + w // 2, y1 + h // 2
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

                    cx2, cy2 = 1280 // 2, 720 // 2
                    cv2.circle(img, (cx2, cy2), 5, (255, 0, 255), cv2.FILLED)

                    cv2.rectangle(img, (120, 120), (1280-120,720-120), (255, 0, 0), 2)

                    cv2.line(img, (cx2,cy2), (cx,cy), (255, 0, 0), 1)


                    konum_verileri.append(rakip_verileri)
                    print("konum verileri: \n", konum_verileri)

                    for index, koordinat in enumerate(konum_verileri):
                        x_deger, y_deger = koordinat

                        print(f"Rakibin {index+1}. konunmu: ", koordinat)

                        """if index > 5:
                            print("KALMAN FILTRESI ILE TAHMIN ALGORITMASI DEVREYE GIRDI")
                            # Tahmin 1
                            x_deger, y_deger = konum_verileri[index-4]
                            predicted1 = kf.predict(x_deger, y_deger)

                            # Tahmin 2
                            predicted2 = kf.predict(predicted1[0], predicted1[1])
                            
                            # Tahmin 3
                            predicted3 = kf.predict(predicted2[0], predicted2[1])

                            # Tahmin 4
                            predicted4 = kf.predict(predicted3[0], predicted3[1])

                            # Tahmin 5
                            predicted5 = kf.predict(predicted4[0], predicted4[1])

                            # Nihai Tahmin
                            predicted6 = kf.predict(predicted5[0], predicted5[1])

                            predicted_frame = (int(predicted1[0]), int(predicted1[1]))

                            cv2.line(img, (x_center, y_center), (predicted1[0], predicted1[1]), (255, 0, 0), 1)"""
    cv2.imshow("Image", img)

    # video kayıt
    video.write(img)

    fps = 1 / (new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time
    print("fps: ", int(fps))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()