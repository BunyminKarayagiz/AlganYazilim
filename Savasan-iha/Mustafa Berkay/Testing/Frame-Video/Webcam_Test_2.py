import cv2
import time
import threading
import concurrent.futures
import Server_Udp
import YOLOv8_deploy

class Yki:
    def __init__(self) -> None:
        self.yolo_model = YOLOv8_deploy.Detection("D:\\Visual Code File Workspace\\ALGAN\\AlganYazilim\\Savasan-iha\\Mustafa Berkay\\Model2024_V1.pt")
        self.udp_sv = Server_Udp.Server()
        self.udp_sv.create_server() 
        self.frame = None
        self.lock = threading.Lock()
        self.stop_signal = False

    def process_yolo_frame(self, frame):
        """
        Process the incoming frame using the YOLO model.
        """
        pwm_data, processed_frame, locked_or_not = self.yolo_model.model_predict(frame)
        return processed_frame, locked_or_not, pwm_data

    def receive_frames(self):
        while not self.stop_signal:
            frame = self.udp_sv.recv_frame_from_client()
            with self.lock:
                self.frame = frame

    def show_webcam(self):
        prev_time = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(self.receive_frames)
            while not self.stop_signal:
                try:
                    with self.lock:
                        frame = self.frame
                    if frame is not None:
                        current_time = time.time()
                        fps = 1 / (current_time - prev_time)
                        prev_time = current_time

                        processed_frame, locked_or_not, pwm_data = self.process_yolo_frame(frame)

                        # Put FPS on the frame
                        cv2.putText(processed_frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                        cv2.imshow('Webcam', processed_frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            self.stop_signal = True
                            break
                except Exception as e:
                    print(f"An error occurred: {e}")
                    self.stop_signal = True
                    break

        # When everything is done, release the capture
        cv2.destroyAllWindows()

if __name__ == "__main__":
    yki_obj = Yki()
    yki_obj.show_webcam()
