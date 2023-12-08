import socket
import threading
import json

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
        print(f"[YENI BAGLANTI] {addr} baglandi.")

        connected = True
        while connected:
            msg_length = conn.recv(self.HEADER).decode(self.FORMAT)  #İstemciden gelen mesajın uzunluğunu alır.
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(self.FORMAT)   #İstemciden gelen mesajı alır ve kodlama formatını kullanarak çözümler.

                if msg == self.DISCONNECT_MESSAGE:   #İstemci, bağlantıyı sonlandırmak için özel bir mesaj gönderirse, bağlantıyı sonlandırır.
                    connected = False
                else:
                    try:
                        data = json.loads(msg)
                        print(f"[{addr}] JSON verileri alindi: {data}")

                    except json.JSONDecodeError:
                        print(f"[{addr}] JSON verileri gecersiz: {msg}")

        conn.close()

    def start(self):   #Sunucu başlatma metodunu tanımlar.
        self.server.listen()  #Sunucuyu dinlemeye başlar.
        print(f"[DINLENIYOR] Server Dinliyor {self.SERVER}:{self.PORT}")
        while True:
            conn, addr = self.server.accept()  #Yeni bir istemci bağlantısını kabul eder ve bağlantı nesnesi (conn) ve istemci adresi (addr) döndürür.
            thread = threading.Thread(target=self.handle_client, args=(conn, addr)) # Her yeni bağlantı için bir iş parçacığı (thread) oluşturur ve handle_client metodunu çalıştırır.
            thread.start()
            print(f"[AKTIF BAGLANTILAR] {threading.activeCount() - 1}")

if __name__ == "__main__":
    print("[BASLATILIYOR] Server baslatiliyor...")
    server = Server()
    server.start()
