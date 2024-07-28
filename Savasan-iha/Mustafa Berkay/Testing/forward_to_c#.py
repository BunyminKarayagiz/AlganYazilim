import socket
import av
import cv2
import numpy as np
import sys

# Define the IP and port to listen on for the Raspberry Pi stream
UDP_IP = "10.241.113.143"  # Listen on all available network interfaces
UDP_PORT = 5555

# Define the IP and port to send the frames to the C# client
CSHARP_IP = "10.241.113.143"  # Replace with the IP address of the C# client
CSHARP_PORT = 11000

# Create a UDP socket to receive data from the Raspberry Pi
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# Create a UDP socket to send data to the C# client
csock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"Listening on {UDP_IP}:{UDP_PORT}")

# Create a buffer for receiving data
buffer_size = 65535

# Create a codec context for H.264 decoding
codec = av.CodecContext.create('h264', 'r')

while True:
    # Receive data from the socket
    data, addr = sock.recvfrom(buffer_size)
    print(f"Received packet from {addr}")
    print("data: ",sys.getsizeof(data))

    try:
        # Create an AVPacket from the received data
        packet = av.Packet(data)

        # Decode the packet
        frames = codec.decode(packet)

        for frame in frames:
            # Convert the frame to an image
            img = frame.to_image()

            # Convert the image to a numpy array (OpenCV format)
            frame_data = np.array(img)
            frame_data = cv2.cvtColor(frame_data, cv2.COLOR_BGR2RGB)
            
            cv2.imshow('Received Frame', frame_data)
            # Break the loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            resized_frame = cv2.resize(frame_data, (480,320), interpolation=cv2.INTER_LINEAR)

            # Encode the frame as JPEG to send to C#
            _, encoded_frame = cv2.imencode('.jpg', resized_frame)

            # # Split the encoded frame into smaller chunks
            # max_chunk_size = 64000  # Define the maximum chunk size (less than 64KB)
            # for i in range(0, len(encoded_frame), max_chunk_size):
            #     chunk = encoded_frame[i:i + max_chunk_size]

            try:
                csock.sendto(encoded_frame.tobytes(), (CSHARP_IP, CSHARP_PORT))
            except Exception as e:
                print("C# Error: ", e)


    except av.AVError as e:
        # If decoding fails, print the error and continue
        print(f"Failed to decode frame: {e}")

# Cleanup
csock.close()
sock.close()
