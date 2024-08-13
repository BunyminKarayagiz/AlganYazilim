from Calismalar.Behcet.kalmanfilter_eski import KalmanFilter
import cv2

img = cv2.imread("C:\\Users\\asus\\AlganYazilim\\Calismalar\\Behcet\\blue_image.png")

ball_positions = [(50, 100), (100, 100), (150, 100), (200, 100), (250, 100), (300, 100), (350, 100), (400, 100), (450, 100)]

if img is None:
    print("resim okunmuyor")

# Kalman filtesini ekle
kf = KalmanFilter()

for pt in ball_positions:
    print("veri tipi:", type(pt))
    cv2.circle(img, pt, 15, (0, 20, 220), -1)
    predicted = kf.predict(pt[0], pt[1])

    cv2.circle(img, predicted, 15, (20, 220, 0), 4)

"""for i in range(10):
    predicted = kf.predict(predicted[0], predicted[1])
    cv2.circle(img, predicted, 15, (20, 220, 0), 4)"""

cv2.imshow('IMG', img)
cv2.waitKey(0)

"""img = cv2.imread('blue_background.webp')

ball_positions = [(50, 100), (100, 100), (150, 100), (200, 200), (250, 100), (300, 100), (350, 100), (400, 100), (450, 100)]

for pt in ball_positions:
    cv2.circle(img, pt, 15, (0, 20, 220), -1)

    predicted = kf.predict(pt[0], pt[1])

    cv2.circle(img, predicted, 15, (220, 20, 0), 4)

predicted1 = kf.predict(predicted[0], predicted[1])
cv2.circle(img, predicted1, 15, (20, 220, 0), 4)

predicted2 = kf.predict(predicted1[0], predicted1[1])
cv2.circle(img, predicted2, 15, (20, 220, 0), 4)

cv2.imshow("Img", img)
cv2.waitKey(0)"""