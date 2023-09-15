import Haberlesme


class Yerİstasyonu():
    def __init__(self):
        self.Server=Haberlesme.Udp_Server()




if __name__ == '__main__':
    yer=Yerİstasyonu()
    yer.Server.create_server()
    while True:
        frame=yer.Server.recv_from_client()
        yer.Server.show(frame)