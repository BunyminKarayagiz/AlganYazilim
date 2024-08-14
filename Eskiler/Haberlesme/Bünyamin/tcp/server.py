import socket

HOST = "10.80.1.106"
PORT = 9000
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

tcp.bind((HOST, PORT))
tcp.listen()

conn, addr = tcp.accept()
print(f"Connect with{addr}")

while True:
    data = conn.recv(1024)
    conn.sendall(b"Server Sended")
