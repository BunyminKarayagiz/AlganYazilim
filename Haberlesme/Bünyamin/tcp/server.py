import socket

HOST = "10.241.167.40"
PORT = 9000

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

tcp.bind((HOST, PORT))

tcp.listen()

conn, addr = tcp.accept()
print(f"Connect with{addr}")
print(conn)

while True:
    data = conn.recv(1024)
    conn.sendall(b"Server Sended")
