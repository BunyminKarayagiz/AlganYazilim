import multiprocessing
import customtkinter as ctk
import time

def run_gui(queue):
    """This function will run in a separate process to start the customtkinter GUI."""
    app = ctk.CTk()
    app.geometry("400x400")

    label = ctk.CTkLabel(app, text="Waiting for data...")
    label.pack(pady=20)

    def check_queue():
        # Check for any updates in the queue from the main process
        if not queue.empty():
            data = queue.get()
            label.configure(text=f"Received: {data}")
        
        # Keep checking periodically
        app.after(100, check_queue)

    # Start checking the queue
    check_queue()
    
    app.mainloop()

def worker(queue):
    """Worker process to do heavy work and send updates to the GUI process."""
    for i in range(5):
        time.sleep(1)  # Simulate some heavy computation
        queue.put(f"Task {i} complete")  # Send a message to the GUI
    queue.put("All tasks complete!")

if __name__ == '__main__':
    # Create a multiprocessing Queue for communication
    queue = multiprocessing.Queue()

    # Start the GUI process
    gui_process = multiprocessing.Process(target=run_gui, args=(queue,))
    gui_process.start()

    # Start the worker process
    worker_process = multiprocessing.Process(target=worker, args=(queue,))
    worker_process.start()

    # Wait for the worker process to complete
    worker_process.join()

    # Terminate the GUI process after work is done
    gui_process.terminate()
