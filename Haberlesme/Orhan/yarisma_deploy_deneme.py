import cv2
from ultralytics import YOLO



model = YOLO('yolov8best.pt')
cap = cv2.VideoCapture(0)
while cap.isOpened():

    success, frame = cap.read()
    disx1, disx2, disy1, disy2 = int(frame.shape[1] * 0.25), int(frame.shape[1] * 0.75), int(
        frame.shape[0] * 0.10), int(frame.shape[0] * 0.90)
    cv2.rectangle(frame, (disx1, disy1), (disx2, disy2), (0, 0, 255), 2)
    x_shape, y_shape = frame.shape[1], frame.shape[0]
    if success:
        results = model(frame)
        for result in results:
            boxes = result.boxes.cpu().numpy()
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0][0].astype(int), box.xyxy[0][1].astype(int), box.xyxy[0][2].astype(int), box.xyxy[0][3].astype(int)

                if disx1 < x1 and disy1 < y1 and disx2 > x2 and disy2 > y2:
                    cv2.rectangle(frame, (disx1, disy1), (disx2, disy2), (0, 255, 0), 2)



        annotated_frame = results[0].plot()
        cv2.imshow("YOLOv8 Inference", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:

        break

cap.release()
cv2.destroyAllWindows()