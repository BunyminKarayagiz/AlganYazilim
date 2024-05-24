from ultralytics import YOLO
import cv2
from collections import Counter
import time
from YOLOv8_deploy import Detection

# Load the model
model = YOLO('models/Model2024_V1.pt')

# Open the video source
# cap = cv2.VideoCapture(0)  # webcam
cap = cv2.VideoCapture("C:\\Users\\demir\\Projects\\AlganYazilim\\Savasan-iha\\Eda\\eda\\datas\\ucus_3.mp4")  # video

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()
    if not success:
        break

    # Resize the frame
    frame = cv2.resize(frame, (640, 480))

    # Run YOLOv8 tracking on the frame
    results = model.track(source=frame, conf=0.3, iou=0.5, show=False, tracker="bytetrack.yaml")
    # results = model.predict(frame)

    # Visualize the results on the frame
    if results:
        annotated_frame = results[0].plot()
        cv2.imshow("YOLOv8 Tracking", annotated_frame)

        # Get the class IDs for all detections in the frame
        # class_ids = results[0].boxes.cls = "Target"

        boxes = results[0].boxes.xyxy.cpu().tolist()
        for box in boxes:
            x1, y1, x2, y2 = box

            x_center = int((x1 + x2) / 2)
            y_center = int((y1 + y2) / 2)
            print(
                f"Top-left: ({x1}, {y1}), Top-right: ({x2}, {y1}), Bottom-left: ({x1}, {y2}), Bottom-right: ({x2}, {y2})")
            print(x_center, y_center)
    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()
