import socket
import av
import numpy as np
import cv2

# Define the IP and port to listen on
UDP_IP = "10.80.1.85"  # Listen on all available network interfaces
UDP_PORT = 5555

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening on {UDP_IP}:{UDP_PORT}")

# Create a buffer for receiving data
buffer_size = 65535

# Create a codec context for H.264 decoding
codec = av.CodecContext.create('h264', 'r')
counter = 0
while True:
    # Receive data from the socket
    data, addr = sock.recvfrom(buffer_size)
    print(f"Received packet from {addr}")

    try:
        # Create an AVPacket from the received data
        packet = av.Packet(data)

        # Decode the packet
        frames = codec.decode(packet)

        for frame in frames:
            # Convert the frame to an image
            img = frame.to_image()

            # Convert the image to a numpy array (OpenCV format)
            frame = np.array(img)
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Display the frame
            cv2.imshow('Received Frame', frame_bgr)

            # Break the loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except av.AVError as e:
        # If decoding fails, print the error and continue
        print(f"Failed to decode frame: {e}")

# Cleanup
cv2.destroyAllWindows()
sock.close()
