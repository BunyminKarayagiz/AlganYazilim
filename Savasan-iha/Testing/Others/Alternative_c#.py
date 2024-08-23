import cv2
import socket
import struct
import msgpack
import msgpack_numpy as m
import time

# Register numpy serialization with msgpack
m.patch()

# Setup socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('10.80.1.51', 8485))
server_socket.listen(0)

print("Server listening on port 8485")

conn, addr = server_socket.accept()

# Path to the local video file (use raw string or double backslashes)
video_file = r'C:\Users\user\Desktop\test.mp4'

# Open the video file
cap = cv2.VideoCapture(video_file)

# Check if video file opened successfully
if not cap.isOpened():
    print("Error opening video file")
    exit()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.resize(frame, (640, 480)) 
    # Serialize frame using msgpack
    data = msgpack.packb(frame, use_bin_type=True)
    # Send message length first
    message_size = struct.pack("L", len(data))

    # Then send the data
    conn.sendall(message_size + data)

    # Introduce a small delay to simulate real-time streaming (optional)
    time.sleep(0.033)  # Adjust this to your needs (e.g., 0.033 for ~30 FPS)

cap.release()
conn.close()
server_socket.close()
