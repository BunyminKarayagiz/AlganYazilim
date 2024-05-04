import json

from tcp import TCP


class Server(TCP):

    def __init__(self):
        super().__init__()

    def creat_server(self):
        self.Main_Tcp.bind((self.server_ip, self.PORT))
        self.Main_Tcp.listen()
        print("Server is listening...")
        self.conn, self.addr = self.Main_Tcp.accept()
        print(f"Connect with{self.addr}")

    def recv_tcp_message(self):
        self.data = self.conn.recv(1024)
        self.data = self.data.decode()
        return json.loads(self.data)

    def send_data_to_client(self, message):
        self.conn.send(message.encode("utf-8"))
