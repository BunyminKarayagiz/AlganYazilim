import Haberlesme

import Server_Udp
import Server_Tcp
class Yerİstasyonu():

    def __init__(self):
        self.Server_udp=Server_Udp.Server()
        self.Server_tcp=Server_Tcp.Server()

    def creat_servers(self):
        self.Server_udp.create_server()
        self.Server_tcp.creat_server()

if __name__ == '__main__':
    #   Yer istasyonu sınıfı yapıcı metodu çağrılıyor.
    yer_istasyonu=Yerİstasyonu()

    #   Udp ve tcp için objeler oluşturuldu.
    server_udp=yer_istasyonu.Server_udp
    server_tcp = yer_istasyonu.Server_tcp

    #   Server oluşturuluyor
    yer_istasyonu.creat_servers()

    while True:
        server_tcp.recv_tcp_message()
        frame=server_udp.recv_frame_from_client()
        server_udp.show(frame)