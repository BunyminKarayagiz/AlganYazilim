import Server_Udp_yeni
import Server_Tcp_yeni
from path import Plane
import ana_sunucu_islemleri
import threading



class Yerİstasyonu():

    def __init__(self):
        self.ana_sunucuya_giris_durumu = False
        self.ana_sunucu = ana_sunucu_islemleri.sunucuApi("http://127.0.0.1:5000")

    "Ana Sunucuya Bağlanma Fonksiyonu"

    def connect_to_anasunucu(self, kullanici_adi, sifre):
        "Burada durum kodu işlemin başarı kodunu vermektedir örn:200"
        ana_sunucuya_giris_kodu, durum_kodu = self.ana_sunucu.sunucuya_giris(
            str(kullanici_adi),
            str(sifre))
        if int(durum_kodu) == 200:
            print(f"\x1b[{31}m{'Ana Sunucuya Bağlanıldı: ' + durum_kodu}\x1b[0m")  # Ana sunucuya girerkenki durum kodu.
            self.ana_sunucuya_giris_durumu = True
        return self.ana_sunucuya_giris_durumu


    def TCP_connection_handler(self,function):
        Server_tcp = Server_Tcp_yeni.Server()
        
        try:
            Server_tcp.creat_server()
        except (ConnectionError, Exception) as e:
            print("Anasunucu veya Server oluşturma hatası: ", e)
            connection=False
            while not connection:
                Server_tcp.creat_server()
                connection=True
        
        while True:
            data = Server_tcp.recv_tcp_message()
            function(data)

    def UDP_connection_handler(self):
        Server_udp = Server_Udp_yeni.Server()

        try:
            Server_udp.create_server()
        except (ConnectionError , Exception) as e:
            print("Anasunucu veya Server oluşturma hatası: ", e)
            connection=False
            while not connection:
                Server_udp.create_server()
                connection=True
        
        while True:
            frame = Server_udp.recv_frame_from_client()
            Server_udp.show(frame)
    

if __name__ == '__main__':

    yer_istasyonu = Yerİstasyonu()

    try:
        "Ana Sunucuya giriş yapıyor."
        giris_kodu = yer_istasyonu.connect_to_anasunucu("algan", "53SnwjQ2sQ")
    except (ConnectionError , Exception) as e:
        print("Anasunucu veya Server oluşturma hatası: ", e)

        #Eğer Bağlantı hatası olursa While içinde tekrar bağlanmayı deneyecek
        connection=False
        while not connection:
            giris_kodu = yer_istasyonu.connect_to_anasunucu("algan", "53SnwjQ2sQ")
            connection=True

    Tcp_thread = threading.Thread(target= yer_istasyonu.TCP_connection_handler ,args=( yer_istasyonu.ana_sunucu.sunucuya_postala,))
    Udp_thread = threading.Thread(target= yer_istasyonu.UDP_connection_handler )

    Tcp_thread.start()
    Udp_thread.start()
