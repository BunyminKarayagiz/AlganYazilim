import socket

class Server():

    def __init__(self,PORT):
        self.server_ip = socket.gethostbyname(socket.gethostname())
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.PORT = PORT

    def creat_server(self):
        self.tcp_socket.bind((self.server_ip, self.PORT))
        self.tcp_socket.listen()
        print("TCP-Server is listening...")
        self.conn, self.addr = self.tcp_socket.accept()
        print(f"Connect with{self.addr}")

    def recv_tcp_message(self):
        self.data = self.conn.recv(1024)
        self.data = self.data.decode()
        print(self.data)
        return self.data

    def send_data_to_client(self, message):
        self.conn.sendall(message)

    def close_socket(self):
        self.tcp_socket.close()