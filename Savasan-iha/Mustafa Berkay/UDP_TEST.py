import Server_Udp

class iha():
    def __init__(self) -> None:
        self.Server_udp = Server_Udp.Server()

    def Görüntü_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_udp.create_server()
                connection_status=True
                print("UDP : SERVER OLUŞTURULDU")
            except (ConnectionError , Exception) as e:
                print("UDP SERVER: oluştururken hata : ", e)
            #    print("UDP SERVER'A 3 saniye içinden yeniden bağlanılıyor...\n")
            #   self.Server_udp.close_socket()
            #   self.Server_udp = Server_Udp.Server()
            #   self.Server_udp.create_server() #TODO DÜZENLEME GELEBİLİR
                
        self.görüntü_sunucusu=connection_status
        return connection_status
    
    def görüntü_çek(self):
            try:
                frame= self.Server_udp.recv_frame_from_client()
                return frame
            except:
                print("UDP: GÖRÜNTÜ ALINIRKEN HATA..")

if __name__ == "__main__":
    obj=iha()
    obj.Görüntü_sunucusu_oluştur()
    
    while True:
        print("FRAME ÖNCESİ")
        frame=obj.görüntü_çek()
        obj.Server_udp.show(frame)