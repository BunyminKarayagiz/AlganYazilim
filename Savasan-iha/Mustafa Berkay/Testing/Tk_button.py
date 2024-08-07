import socket
import threading
import tkinter as tk
from tkinter import messagebox
from queue import Queue

# TCP Client function
def send_confirmation_message():
    host = '127.0.0.1'  # Replace with the server's IP address
    port = 12345        # Replace with the server's port number
    message = 'Confirmation message'
    
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connect to the server
        s.connect((host, port))
        
        # Send the message
        s.sendall(message.encode('utf-8'))
        
        # Close the connection
        s.close()
        
        # Show a success message (enqueue the result to be processed in the main thread)
        gui_queue.put(("info", "Success", "Confirmation message sent successfully!"))
    except Exception as e:
        # Show an error message (enqueue the result to be processed in the main thread)
        gui_queue.put(("error", "Error", f"Failed to send message: {e}"))

def process_gui_queue():
    try:
        while not gui_queue.empty():
            msg_type, title, message = gui_queue.get_nowait()
            if msg_type == "info":
                messagebox.showinfo(title, message)
            elif msg_type == "error":
                messagebox.showerror(title, message)
    except Exception as e:
        print(f"Error processing GUI queue: {e}")
    finally:
        # Schedule the next check
        root.after(100, process_gui_queue)

def on_send_button_click():
    # Run the TCP client function in a separate thread
    threading.Thread(target=send_confirmation_message).start()

# Create a thread-safe queue for communication between threads
gui_queue = Queue()

# Create the GUI
root = tk.Tk()
root.title("Ground Control Station")

# Create and place the button
send_button = tk.Button(root, text="Send Confirmation", command=on_send_button_click)
send_button.pack(pady=20)

# Start the periodic GUI queue processing
root.after(100, process_gui_queue)

# Run the GUI event loop
root.mainloop()
