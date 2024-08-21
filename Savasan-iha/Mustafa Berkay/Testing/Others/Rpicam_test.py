import socket
import cv2
import numpy as np
import struct

# Configuration parameters
TCP_IP = "192.168.1.100"  # IP address of the Raspberry Pi
TCP_PORT = 8000
BUFFER_SIZE = 4096

# Create a TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((TCP_IP, TCP_PORT))

# Initialize OpenCV window
cv2.namedWindow('Video Stream', cv2.WINDOW_NORMAL)

data = b''
payload_size = struct.calcsize("Q")

while True:
    while len(data) < payload_size:
        packet = sock.recv(BUFFER_SIZE)
        if not packet:
            break
        data += packet
    if len(data) < payload_size:
        break

    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("Q", packed_msg_size)[0]

    while len(data) < msg_size:
        data += sock.recv(BUFFER_SIZE)

    frame_data = data[:msg_size]
    data = data[msg_size:]

    # Decode the frame
    frame = np.frombuffer(frame_data, np.uint8)
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    # Display the frame
    if frame is not None:
        cv2.imshow('Video Stream', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cv2.destroyAllWindows()
sock.close()
