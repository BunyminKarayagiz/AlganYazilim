import numpy as np
import threading
import time
from multiprocessing import Queue

class PWMProcessor:
    def __init__(self, event_map):
        self.event_map = event_map
        self.stored_packets = {}
        self.lock = threading.Lock()

    def kalman_predict(self, numpy_arr, arr_size):
        # Placeholder for Kalman filter prediction logic
        # Return some prediction for now
        return np.mean(numpy_arr, axis=0)

    def pwm_gonder(self, pwm_array):
        # Placeholder for sending the predicted pwm data
        print("Predicted PWM:", pwm_array)

    def process_data(self):
        pwm_data_queue, pwm_trigger = self.event_map[5]

        while True:
            try:
                pwm_array = pwm_data_queue.get_nowait()
            except Exception as e:
                # No data available in the queue
                time.sleep(0.01)
                continue

            with self.lock:
                packet_id = pwm_array[2]
                self.stored_packets[packet_id] = pwm_array

                if len(self.stored_packets) >= 5:
                    sorted_ids = sorted(self.stored_packets.keys())
                    sorted_packets = [self.stored_packets[pid] for pid in sorted_ids[:5]]

                    # Remove the used packets
                    for pid in sorted_ids[:5]:
                        del self.stored_packets[pid]

                    stored_packets_np = np.array(sorted_packets, dtype=np.uint32)
                    print("Packet Ready:\n", stored_packets_np, "\n")
                    predicted_pwm = self.kalman_predict(numpy_arr=stored_packets_np, arr_size=5)
                    self.pwm_gonder(pwm_array=predicted_pwm)

    def start_processing(self):
        processing_thread = threading.Thread(target=self.process_data)
        processing_thread.daemon = True
        processing_thread.start()

# Example usage
if __name__ == "__main__":
    # Create a multiprocessing queue
    pwm_data_queue = Queue()
    pwm_data_queue.g
    # Create a sample event map with the pwm_data_queue
    event_map = {5: (pwm_data_queue, None)}

    # Create an instance of PWMProcessor
    pwm_processor = PWMProcessor(event_map)
    
    # Start processing the data in a separate thread
    pwm_processor.start_processing()

    # Simulate adding data to the queue
    for i in range(20):
        pwm_data_queue.put(np.array([i, i+1, i+13], dtype=np.uint32))  # Simulate packet IDs 13 to 32
        time.sleep(0.01)  # Simulate some delay in data arrival
