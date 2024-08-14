import tcp
import time
import json

tcp = tcp.TCP


class Client_Tcp(tcp):

    def __init__(self):
        super().__init__()

    def connect_to_server(self,to_server_host):
        self.Main_Tcp.connect((to_server_host,self.PORT))

    def send_message_to_server(self,message):
        self.Main_Tcp.send(message.encode("utf-8"))

    def recv_message(self):
        self.data=self.Main_Tcp.recv(1024)
        print(self.data)

    def __call__(self, *args, **kwargs):
        self.connect_to_server("10.241.165.166")
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

client = Client_Tcp()
client()
