import cv2
import multiprocessing as mp
import YOLOv8_deploy


def capture_frames(queue, cap):
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        queue.put(frame)
    cap.release()

def worker(yolo_model,input_queue, output_queue):
    while True:
        frame = input_queue.get()
        if frame is None:  # End of processing signal
            break
        processed_frame = yolo_model.model_predict(frame=frame)
        output_queue.put(processed_frame)

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    yolo_model = YOLOv8_deploy.Detection("D:\\Visual Code File Workspace\\ALGAN\\AlganYazilim\\Savasan-iha\\Mustafa Berkay\\Model2024_V1.pt")


    input_queue = mp.Queue(maxsize=10)
    output_queue = mp.Queue(maxsize=10)
    num_workers = 1  # Number of worker processes

    # Start the frame capture process
    capture_process = mp.Process(target=capture_frames, args=(input_queue, cap))
    capture_process.start()

    # Start the worker processes
    workers = []
    for _ in range(num_workers):
        p = mp.Process(target=worker, args=(yolo_model,input_queue, output_queue))
        p.start()
        workers.append(p)

    while True:
        processed_frame = output_queue.get()
        if processed_frame is None:  # End of processing signal
            break
        cv2.imshow('Processed Frame', processed_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up
    capture_process.join()
    for _ in range(num_workers):
        input_queue.put(None)  # Send end signal to workers
    for p in workers:
        p.join()
    cv2.destroyAllWindows()
