import socket


class Tcp:
    def __init__(self, host="127.0.0.1", port=65432):
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def conn(self):
        self.s.bind((self.host, self.port))
        self.s.listen()
        x, addr = self.s.accept()

        print(f"Connected by {addr}")

        while True:
            data = x.recv(1024)
            if not data:
                break
            x.sendall(data)


if __name__ == "__main__":
    tcp = Tcp()
    tcp.conn()
