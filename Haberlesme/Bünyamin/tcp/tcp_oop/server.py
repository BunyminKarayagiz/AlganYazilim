from flask import json

import main


tcp = main.TCP


class Server_TCP(tcp):

    def __init__(self):
        super().__init__()
        self.tuple=(self.server_ip,self.PORT)

    def creat_server(self):
        self.Main_Tcp.bind(self.tuple)
        self.Main_Tcp.listen()
        print("Server is listening...")
        self.conn, self.addr = self.Main_Tcp.accept()
        print(f"Connect with{self.addr}")

    def recv_message(self):

        try:
            self.data = self.conn.recv(1024)
        except Exception as err:
            print("rerv_message kısmında hata! ")
            print("ConnectionResetError: ", err)
            self.Main_Tcp.close()
            self.creat_server()

        self.result = json.dumps(self.data.decode("utf-8"))
        self.result = json.loads(self.result)
        return self.result


    def send_data_to_client(self,message):
        self.mesaj = json.dumps(message)
        self.conn.send(self.mesaj.encode("utf-8"))


    def __call__(self):
        self.creat_server()
        while True:
            self.recv_message()


server = Server_TCP()
server()