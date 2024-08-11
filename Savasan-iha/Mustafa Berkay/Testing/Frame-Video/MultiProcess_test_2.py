import cv2
import multiprocessing as mp
import time
import YOLOv8_deploy
import datetime

class VideoProcessor:
    def __init__(self, model_path, capture_index=0, queue_size=1):
        self.model_path = model_path
        self.capture_index = capture_index
        self.capture_queue = mp.Queue(maxsize=queue_size)
        self.display_queue = mp.Queue(maxsize=queue_size)

        self.event_queue_1 = mp.Queue()
        self.event_1 = mp.Event()
        self.event_queue_2 = mp.Queue()
        self.event_2 = mp.Event()

        self.yolo_model = YOLOv8_deploy.Detection(self.model_path)

    def capture_frames(self):
        process_name = mp.current_process().name
        print(f"Starting Capture-process: {process_name}")

        cap = cv2.VideoCapture(self.capture_index)
        if not cap.isOpened():
            print("Error: Unable to open camera.")
            return
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if not self.capture_queue.full():
                self.capture_queue.put(frame)
        cap.release()

    def process_frames(self, event_queue, event_trigger):
        process_name = mp.current_process().name
        print(f"Starting Frame_Processing process: {process_name}")
        lockedOrNot = 0
        locked_prev = 0
        prev_frame_time = 0
        is_locked = 0
        sent_once = 0
        elapsed_time = 0
        start_time = 0
        event_message = "none"

        while True:
            if event_trigger.is_set():
                time.sleep(0.01)
                event_message = event_queue.get()
                print(f"{process_name} received event: {event_message}")
                event_trigger.clear()

            if event_message == "kilitlenme":
                if not self.capture_queue.empty():
                    frame = self.capture_queue.get()
                    new_frame_time = time.perf_counter()
                    pwm_verileri, processed_frame, lockedOrNot = self.yolo_model.model_predict(frame=frame)

                    if lockedOrNot == 1 and locked_prev == 0:
                        start_time = time.perf_counter()
                        start_now = datetime.datetime.now()
                        cv2.putText(img=processed_frame, text="HEDEF GORULDU", org=(50, 400), fontFace=1, fontScale=2, color=(0, 255, 0), thickness=2)
                        locked_prev = 1

                    if lockedOrNot == 0 and locked_prev == 1:
                        cv2.putText(img=processed_frame, text="HEDEF KAYBOLDU", org=(50, 400), fontFace=1, fontScale=2, color=(0, 255, 0), thickness=2)
                        locked_prev = 0
                        is_locked = 0
                        sent_once = 0

                    if lockedOrNot == 1 and locked_prev == 1:
                        elapsed_time = time.perf_counter() - start_time
                        cv2.putText(img=processed_frame, text=str(round(elapsed_time, 3)), org=(50, 370), fontFace=1, fontScale=1.5, color=(0, 255, 0), thickness=2)

                        if is_locked == 0:
                            cv2.putText(img=processed_frame, text="KILITLENIYOR", org=(50, 400), fontFace=1, fontScale=1.8, color=(0, 255, 0), thickness=2)
                        if elapsed_time >= 4.0:
                            cv2.putText(img=processed_frame, text="KILITLENDI", org=(50, 400), fontFace=1, fontScale=1.8, color=(0, 255, 0), thickness=2)
                            is_locked = 1
                            print("KİLİTLENME BAŞARILI\nKİLİTLENME BAŞARILI\nKİLİTLENME BAŞARILI\nKİLİTLENME BAŞARILI\n")

                    fps = 1 / (new_frame_time - prev_frame_time)
                    prev_frame_time = time.perf_counter()

                    if not self.display_queue.full():
                        self.display_queue.put((processed_frame, fps))

            elif event_message == "kamikaze":
                time.sleep(1)
                print(f"Frame_Processing({process_name} : KAMIKAZE )")

            else:
                #print("INVALID MODE...")
                pass

    def display_frames(self):
        process_name = mp.current_process().name
        print(f"Starting Display process: {process_name}")
        while True:
            if not self.display_queue.empty():
                frame, fps = self.display_queue.get()
                cv2.putText(frame, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.imshow('Webcam', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        cv2.destroyAllWindows()

    def start(self):
        p1 = mp.Process(target=self.capture_frames)
        p2 = mp.Process(target=self.process_frames, args=(self.event_queue_1, self.event_1))
        p3 = mp.Process(target=self.process_frames, args=(self.event_queue_2, self.event_2))
        p4 = mp.Process(target=self.display_frames)

        p1.start()
        p2.start()
        p3.start()
        p4.start()

        return p1,p2,p3,p4

    def trigger_event(self, event_number, message):
        if event_number == 1:
            self.event_queue_1.put(message)
            self.event_1.set()
        elif event_number == 2:
            self.event_queue_2.put(message)
            self.event_2.set()

if __name__ == '__main__':
    video_processor = VideoProcessor(model_path="D:\\Visual Code File Workspace\\ALGAN\\AlganYazilim\\Savasan-iha\\Mustafa Berkay\\Model2024_V1.pt")
    p1,p2,p3,p4 = video_processor.start()
    time.sleep(0.3)
    print("trigger in 10 sec...")
    time.sleep(8)
    
    counter = 0
    while counter < 8:
        time.sleep(3)
        video_processor.trigger_event(1,"kilitlenme")
        video_processor.trigger_event(2,"kilitlenme")
        time.sleep(5)
        video_processor.trigger_event(1,"kamikaze")
        video_processor.trigger_event(2,"kamikaze")
        counter += 1


    p1.join()
    p2.join()
    p3.join()
    p4.join()

