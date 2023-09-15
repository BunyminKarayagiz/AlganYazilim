import socket

class Client:
    def __init__(self, server, port):
        self.HEADER = 64
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        self.SERVER = server
        self.PORT = port
        self.ADDR = (self.SERVER, self.PORT)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)

    def send(self, msg):
        message = msg.encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        self.client.send(send_length)
        self.client.send(message)

if __name__ == "__main__":
    SERVER_IP = "192.168.0.6"
    PORT = 5050

    client = Client(SERVER_IP, PORT)
    client.send("ALGAN IHA")