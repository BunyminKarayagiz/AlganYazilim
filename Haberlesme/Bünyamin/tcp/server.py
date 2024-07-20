import socket
import time

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

tcp.bind(("localhost", 1234))
tcp.listen()

conn, addr = tcp.accept()
print(f"Connect with{addr}")

while True:
    data = conn.recv(1024)
    print(data)
    conn.sendall(b"Server Sended safsdafdsaf")
