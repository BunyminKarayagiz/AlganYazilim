import socket
import sys
import select

class Connection():
    def __init__(self):
        self.s=socket.socket()
        self.s.connect(("localhost",1234))

    def fileno(self):
        return self.s.fileno()

    def on_read(self):
        msg= self.s.recv(1000).decode("utf8")
        print(msg)

    def send(self,msg):
        self.s.send(msg)

class Input():

    def __init__(self,sender):
        self.sender=sender
    def fileno(self):
        return sys.stdin.fileno()
    def on_read(self):
        msg= sys.stdin.readline().encode("utf8")
        self.sender.send(msg)

connection = Connection()
input_reader = Input(connection)

while True:
    readers,_,_ = select.select([connection,input_reader],[],[])

    for reader in readers:
        reader.on_read()