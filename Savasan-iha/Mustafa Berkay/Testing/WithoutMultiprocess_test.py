import cv2
import time
import YOLOv8_deploy

class test():
    def __init__(self) -> None:
        self.yolo_model = YOLOv8_deploy.Detection("D:\\Visual Code File Workspace\\ALGAN\\AlganYazilim\\Savasan-iha\\Mustafa Berkay\\Model2024_V1.pt") 
        self.cap = cv2.VideoCapture(1)
        
    def capture_frames(self):
        
        ret, frame = self.cap.read()
        return frame

    def process_frames(self,frame):
        
        prev_time = time.time()
        
        pwm_verileri, frame, locked_or_not = self.yolo_model.model_predict(frame=frame)
                
        current_time = time.time()
        elapsed = (current_time - prev_time)
        if elapsed > 0:
            fps = 1 / elapsed
        prev_time = current_time
        cv2.putText(frame, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        return frame

if __name__ == '__main__':
    obj=test()

    while True:
        frame = obj.capture_frames()
        frame = obj.process_frames(frame)

        cv2.imshow('Webcam', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
