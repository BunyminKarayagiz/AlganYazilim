import socket
import threading

class Server:
    def __init__(self):
        self.HEADER = 64
        self.PORT = 5050
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.SERVER, self.PORT)
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MESSAGE = "!DISCONNECT"

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)

    def handle_client(self, conn, addr):
        print(f"[YENI BAGLANTI ] {addr} baglandi.")

        connected = True
        while connected:
            msg_length = conn.recv(self.HEADER).decode()
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(self.FORMAT)
                if msg == self.DISCONNECT_MESSAGE:
                    connected = False
                print(f"[{addr}] {msg}")

        conn.close()

    def start(self):
        self.server.listen()
        print(f"[DINLENIYOR] Server dinlemede... {self.SERVER} ")
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()
            print(f"[BAGLANTI AKTIF] {threading.activeCount() - 1}")


if __name__ == "__main__":
    print("[BASLATILIYOR] Server baslatiliyor...")
    server = Server()
    server.start()