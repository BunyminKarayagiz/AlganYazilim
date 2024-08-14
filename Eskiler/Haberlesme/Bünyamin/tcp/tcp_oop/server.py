from flask import json
from main import TCP


class Server_TCP(TCP):

    def __init__(self):
        "main.py dosyasındaki TCP classındaki constructure u buraya aktarır."
        super().__init__()
        self.tuple = (self.server_ip, self.PORT)

    def creat_server(self):
        "servera bağlanıp dinlemeye başlıyor."
        self.Main_Tcp.bind(self.tuple)
        self.Main_Tcp.listen()
        print("Server is listening...")
        "'accept' sunucu soketinin çağrılması sonucu yeni bir bağlantı isteği bekler ve kabul eder "
        self.conn, self.addr = self.Main_Tcp.accept()
        "'conn' yeni bir soket nesnesini temsil eder ve client ile iletişim kurar."
        "'addr' tuple yapımız."
        print(f"Connect with{self.addr}")

    def server_recv_message(self):
        ""
        try:
            self.data = self.conn.recv(1024)
        except Exception as err:
            print("server_recv_message kısmında hata! ")
            print("ConnectionResetError: ", err)
            self.Main_Tcp.close()
            self.creat_server()

        self.result = json.dumps(self.data.decode("utf-8"))
        self.result = json.loads(self.result)
        return self.result

    def send_data_to_client(self, message):
        self.mesaj = json.dumps(message)
        self.conn.send(self.mesaj.encode("utf-8"))

    def __call__(self):
        self.creat_server()
        while True:
            self.server_recv_message()


server = Server_TCP()
server()
