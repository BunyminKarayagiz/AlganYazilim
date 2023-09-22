import oop_tcp


tcp=oop_tcp.TCP
class Server_TCP(tcp):

    def __init__(self):
        super().__init__()

    def creat_server(self):
        self.Main_Tcp.bind((self.server_ip,self.PORT))
        self.Main_Tcp.listen()
        print("Server is listening...")
        self.conn,self.addr=self.Main_Tcp.accept()
        print(f"Connect with{self.addr}")
    def recv_message(self):
        self.data=self.conn.recv(1024)
        print(self.data)
    def send_data_to_client(self,message):
        self.conn.sendall(message)


    def __call__(self, *args, **kwargs):
        self.creat_server()
        while True:
            self.recv_message()

server=Server_TCP()
server()