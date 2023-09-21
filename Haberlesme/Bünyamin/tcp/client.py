import socket

HOST = "10.80.1.106"  # The server's hostname or IP address
PORT = 9000  # The port used by the server

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

tcp.connect((HOST, PORT))

while True:
    tcp.sendall(b"Hello, world")
    data = tcp.recv(1024)
    print(f"Received {data!r}")
