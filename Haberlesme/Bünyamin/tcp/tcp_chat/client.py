import json
import main

tcp = main.TCP


class Client_Tcp(tcp):

    def __init__(self):
        super().__init__()

    def connect_to_server(self, to_server_host):
        self.Main_Tcp.connect((to_server_host, self.PORT))

    def send_message_to_server(self):
        message = input("> ")
        message = json.dumps(message)
        self.Main_Tcp.send(message.encode("utf-8"))

    def recv_message(self):
        self.data = self.Main_Tcp.recv(1024)
        print(self.data)

    def __call__(self, *args, **kwargs):
        self.connect_to_server("10.80.1.81")
        while True:
            self.send_message_to_server()
            self.recv_message()


client = Client_Tcp()
client()
