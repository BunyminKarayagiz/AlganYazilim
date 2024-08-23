import multiprocessing
import time

class EventProcess:
    def __init__(self):
        self.manager = multiprocessing.Manager()
        self.event = self.manager.Event()
        self.trigger_process = multiprocessing.Process(target=self.trigger_event)
        self.wait_process = multiprocessing.Process(target=self.wait_for_event_stop)

    def trigger_event(self):
        """Method that triggers the event."""
        print("Trigger process: Waiting for 5 seconds before triggering the event...")
        time.sleep(5)
        self.event.set()
        print("Trigger process: Event has been triggered.")

    def wait_for_event_stop(self):
        """Method that runs until the event is triggered."""
        print("Wait process: Running until the event is triggered...")
        while not self.event.is_set():
            print("Wait process: Event not set yet, continuing to run...")
            time.sleep(1)
        print("Wait process: Event has been triggered! Stopping the process...")

    def start_processes(self):
        """Method to start both processes."""
        self.trigger_process.start()
        self.wait_process.start()

    def join_processes(self):
        """Method to wait for both processes to complete."""
        self.trigger_process.join()
        self.wait_process.join()

if __name__ == "__main__":
    event_process = EventProcess()
    event_process.start_processes()
    event_process.join_processes()
    print("Main process: Both processes have completed.")
