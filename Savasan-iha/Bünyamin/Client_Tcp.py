from tcp import TCP
import time
import json


class Client(TCP):

    def __init__(self, host):
        "main.py dosyasındaki TCP classındaki constructure u buraya aktarır."
        super().__init__()
        self.to_server_host = host

    def connect_to_server(self):
        "IP'sini aldığımız servera connect atar."
        self.Main_Tcp.connect((self.to_server_host, self.PORT))

    def send_message_to_server(self, message):
        "message adlı metni gönderir."
        self.Main_Tcp.send(message.encode("utf-8"))

    def client_recv_message(self):
        "Sunucudan gelen veriyi -max 1024 byte- alır ve ekrana yazdırır."
        self.data = self.Main_Tcp.recv(1024)
        print(self.data)
        print("Data Alındı")
        return self.data

    """def __call__(self, *args, **kwargs):
        "Belirtilen IP adresine saniyede bir kez message gönderilir."
        to_server_host = "10.241.165.166"
        self.connect_to_server(to_server_host)
        telemetri = {'takim_numarasi': 4,
                     'iha_enlem': 0.0,
                     'iha_boylam': 0.0,
                     'iha_irtifa': -0.808,
                     'iha_dikilme': -22.35449539868347,
                     'iha_yonelme': 46.64746337061367,
                     'iha_yatis': -1.4423654114208542,
                     'iha_hiz': 0.0,
                     'iha_batarya': 100,
                     'iha_otonom': 0,
                     'iha_kilitlenme': 0,
                     'hedef_merkez_X': 383,
                     'hedef_merkez_Y': 299,
                     'hedef_genislik': 26,
                     'hedef_yukseklik': 37,
                     'gps_saati': {'saat': 0, 'dakika': 0, 'saniye': 0, 'milisaniye': 0}, 'mod': 'kilitlenme'}

        message = json.dumps(telemetri)
        while True:
            self.send_message_to_server(message)
            time.sleep(1)
"""
