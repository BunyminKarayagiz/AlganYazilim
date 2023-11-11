import Server_Udp
import Server_Tcp
from path import Plane
import ana_sunucu_islemleri


class Yerİstasyonu():

    def __init__(self):
        "Server Udp ve Tcp'nin objesini oluşturuyor"
        self.Server_udp = Server_Udp.Server()
        self.Server_tcp = Server_Tcp.Server()
        self.ana_sunucuya_giris_durumu = False
        self.ana_sunucu = ana_sunucu_islemleri.sunucuApi("http://127.0.0.1:5000")

    "Serverrları oluşturuyor"

    def creat_servers(self):
        self.Server_udp.create_server()
        self.Server_tcp.creat_server()

    "Ana Sunucuya Bağlanma Fonksiyonu"

    def connect_to_anasunucu(self, kullanici_adi, sifre):
        "Burada durum kodu işlemin başarı kodunu vermektedir örn:200"
        ana_sunucuya_giris_kodu, durum_kodu = self.ana_sunucu.sunucuya_giris(
            str(kullanici_adi),
            str(sifre))
        if int(durum_kodu) == 200:
            print(f"\x1b[{31}m{'Ana Sunucuya Bağlanıldı: ' + durum_kodu}\x1b[0m")  # Ana sunucya girerkenki durum kodu.
            self.ana_sunucuya_giris_durumu = True
        return self.ana_sunucuya_giris_durumu


if __name__ == '__main__':

    "Yer istasyrronu sınıfı yapıcı metodu çağrılıyor."
    yer_istasyonu = Yerİstasyonu()

    "Udp ve tcp için objeler oluşturuldu."
    server_udp = yer_istasyonu.Server_udp
    server_tcp = yer_istasyonu.Server_tcp

    "Ana Sunucuya giriş yapıyor."
    giris_kodu = yer_istasyonu.connect_to_anasunucu("algan", "53SnwjQ2sQ")


    " Server oluşturuluyor"
    yer_istasyonu.creat_servers()

    while True:
        data = server_tcp.recv_tcp_message()
        frame = server_udp.recv_frame_from_client()

        "Ana sunucuya clientten aldığımız data verisini postalıyor"
        yer_istasyonu.ana_sunucu.sunucuya_postala(data)
        server_udp.show(frame)
