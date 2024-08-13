import cv2
from orange_detector import OrangeDetector as od
from Calismalar.Behcet.kalmanfilter_eski import KalmanFilter as kf

cap = cv2.VideoCapture("C:\\Users\\asus\\AlganYazilim\\Calismalar\\Behçet\\ucus_deneme.mp4")

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (640, 480))

    if ret is False:
        break

    orange_bbox = od.detect(frame)
    
    x1, y1, x2, y2 = orange_bbox

    predicted = kf.predict(x_center, y_center)

    #! çerçeveden tahmin etme
    # cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 4 )

    #! merkez nokasından tahmin etme
    x_center = int((x1 + x2) / 2)
    y_center = int((y1 + y2) / 2)
    cv2.rectangle(frame, x_center, y_center, 20, (255, 0, 0), -1)
    cv2.rectangle(frame, (predicted[0], predicted[1]), 20, (255, 0, 255), 4)


    cv2.imshow("Video", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()