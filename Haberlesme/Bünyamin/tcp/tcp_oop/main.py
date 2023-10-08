import socket


class TCP:
    def __init__(self):
        self.host_name = socket.gethostname()
        self.server_ip = socket.gethostbyname(self.host_name)
        self.PORT = 9000
        self.Main_Tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
