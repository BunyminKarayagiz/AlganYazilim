import socket


class Client:
    def __init__(self, host="127.0.0.1", port=65432):
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def conn_client(self):
        self.s.connect((self.host, self.port))
        while True:
            self.s.sendall(b"Hello, world")
            data = self.s.recv(1024)
            print(f"Received {data!r}")

if __name__ == "__main__":
    client = Client()
    client.conn_client()

