import json
import time

import Server_Udp
import Server_Tcp
from path import Plane
import ana_sunucu_islemleri
import yolov5_deploy
import cv2


class Yerİstasyonu():

    def __init__(self):
        "Server Udp ve Tcp'nin objesini oluşturuyor"
        self.yolo_model = yolov5_deploy.Detection(capture_index=0, model_name="bestuçak.pt")
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

    "telemetri verisinde İHA'dan mod değişkeni geliyor. Bu mod değişkeni kullanılmak üzere ayrılıyor"

    def data_ayirici(self, data):
        mod = data["iha_mod"]
        data.popitem()
        telemetri = data
        return telemetri, mod


if __name__ == '__main__':

    "Yer istasyrronu sınıfı yapıcı metodu çağrılıyor."
    yer_istasyonu = Yerİstasyonu()

    "Udp ve tcp için objeler oluşturuldu."
    server_udp = yer_istasyonu.Server_udp
    server_tcp = yer_istasyonu.Server_tcp

    try:
        "Ana Sunucuya giriş yapıyor."
        giris_kodu = yer_istasyonu.connect_to_anasunucu("algan", "53SnwjQ2sQ")
        " Server oluşturuluyor"
        yer_istasyonu.creat_servers()

    except (ConnectionError, Exception) as e:
        print("Anasunucu veya Server oluşturma hatası: ", e)

        # Eğer Bağlantı hatası olursa While içinde tekrar bağlanmayı deneyecek
        connection = False
        while not connection:
            giris_kodu = yer_istasyonu.connect_to_anasunucu("algan", "53SnwjQ2sQ")
            yer_istasyonu.creat_servers()
            connection = True

    while True:
        try :
            "İhadan gelen görüntü ve telemetri verisini alıyor."
            data = server_tcp.recv_tcp_message()
            print(data)
            telemetri, mod = yer_istasyonu.data_ayirici(data)
            frame = server_udp.recv_frame_from_client()


            if mod == "savasan_iha":
                "Gelen frame yolo modeline sokuluyor"
                results, frame = yer_istasyonu.yolo_model.get_results(frame)
                xCord, yCord, frame, lockedOrNot = yer_istasyonu.yolo_model.plot_boxes(results, frame)

                "Modelden gelen değerler ile pwm değeri hesaplanıyor"
                pwm_verileri = yer_istasyonu.yolo_model.coordinates_to_pwm(xCord, yCord)

                "Pwm değerleri İha'ya gönderiliyor."
                server_tcp.send_data_to_client(json.dumps(pwm_verileri))

            elif mod == "kamikaze":
                pass

            "Ana sunucuya clientten aldığımız data verisini postalıyor"
            status_code, rakip_telemetri_verileri = yer_istasyonu.ana_sunucu.sunucuya_postala(telemetri)
            print("Rakip Telemetri : ", rakip_telemetri_verileri)
            server_udp.show(frame)

        except Exception as err:
            yer_istasyonu.Server_udp.Main_socket.close()
            connected= False
            yer_udp_obj=Server_Udp.Server()
            while not connected:
                try:
                    yer_istasyonu.Server_udp.create_server()
                    yer_istasyonu.Server_udp.Main_socket.settimeout(0.001)
                    connected = True
                except Exception as err:
                    print(err)
                    time.sleep(1)
                    print("Telemetri - Gorsel veri alinamadi.", err)
                    pass
