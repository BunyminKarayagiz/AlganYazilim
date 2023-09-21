import oop_tcp


tcp=oop_tcp.TCP

class Client_Tcp(tcp):

    def __init__(self):
        super().__init__()

    def connect_to_server(self,to_server_host):
        self.Main_Tcp.connect((to_server_host,self.PORT))
    def send_message_to_server(self,message):
        self.Main_Tcp.sendall(message)

    def recv_message(self):
        self.data=self.Main_Tcp.recv(1024)
        print(self.data)


    def __call__(self, *args, **kwargs):
        self.connect_to_server("10.241.167.40")
        while True:
            self.send_message_to_server(b"anani sikim")

client=Client_Tcp()
client()