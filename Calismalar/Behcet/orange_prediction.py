import cv2
from orange_detector import OrangeDetector
from Calismalar.Behcet.kalmanfilter_eski import KalmanFilter

cap = cv2.VideoCapture("C:\\Users\\asus\\AlganYazilim\\Calismalar\\Behcet\\orange.mp4")

# Load detector
od = OrangeDetector()

# Load Kalman filter to predict the trajectory
kf = KalmanFilter()

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (640, 480))

    if ret is False:
        break

    orange_bbox = od.detect(frame)
    x, y, x2, y2 = orange_bbox
    x_center = int((x + x2) / 2)
    y_center = int((y + y2) / 2)

    predicted = kf.predict(x_center, y_center)
    #cv2.rectangle(frame, (x, y), (x2, y2), (255, 0, 0), 4)
    cv2.circle(frame, (x_center, y_center), 20, (0, 0, 255), 4)
    cv2.circle(frame, (predicted[0], predicted[1]), 20, (255, 0, 0), 4)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(150) & 0xFF == ord('q'):
        break