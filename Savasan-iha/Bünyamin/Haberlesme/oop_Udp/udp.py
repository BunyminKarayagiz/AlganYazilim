import socket


class UDP:
    def __init__(self):
        self.BUFF_SIZE = 65536     # Kullanılabilecek veri bellek boyutu
        self.Main_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # UDP için temel tanımlama   " (socket.SOCK_DGRAM) ifadesi udp olduğunu belirtiyor."
        self.Main_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.BUFF_SIZE)    # UDP için temel tanımlama
        self.port = 9999


class Udp_Server(UDP):

    def __init__(self):
        super().__init__()
        self.host_name=socket.gethostname()
        self.host_ip=socket.gethostbyname(self.host_name)
    def create_server(self):
        self.socket_adress=(self.host_ip,self.port)
        self.Main_socket.bind(self.socket_adress)
        print('Listening at:', self.socket_adress)





class Udp_Client(UDP):

    def __init__(self):
        super().__init__()


server=Udp_Server()
server.create_server()