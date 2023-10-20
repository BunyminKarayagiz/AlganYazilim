from multiprocessing.pool import ThreadPool

import path
import time
import argparse
import haberlesme2024_basic
import json
import os


host = "192.168.1.104"
port = 8888
port2 = 1234


zamanlistesi = []
zamanlistesi2 = []


# haberlesme veri tcp baglanma
iha_tele = haberlesme2024_basic.client_TCP()
iha_tele.connected(host, port)
print("baglandi")

"""parser = argparse.ArgumentParser()
parser.add_argument('--connect', default='/dev/ttyACM0')
args = parser.parse_args()
connection_string = args.connect"""

parser = argparse.ArgumentParser()
parser.add_argument('--connect', default='tcp:127.0.0.1:5762')
args = parser.parse_args()
connection_string = args.connect


#10.0.0.101
# -- Tuygun Bağlantı
iha = path.Plane(connection_string)


def mavlinkrouter():
    os.system('mavproxy.py --master=/dev/ttyACM0,57600 --out=udpbcast:169.254.102.128:14550')  # Yer Istasyonu IP


circlesayac = []
loiter = 0
# ilk_enlem = iha.pos_lat
# ilk_boylam = iha.pos_lon


datasayac = time.time()
g = time.time()
sure = time.time()
iha_tele.skt.settimeout(0.001)
x_right, x_left, y_up, y_down = 0, 0, 0, 0
mod = "AUTO"


def recv_tcp():
    try:
        data = iha_tele.get_telemetry()
        return json.loads(data)
    except Exception as e:
        pass


pool = ThreadPool(processes=1)
rakip = None
first = 0
qr_gidiyor = False
kalkista = False

speed = 1500
counter_FBWA = time.time()
time_difference_FBWA = 0
hiz_pwm = 1100


while True:
    try:
        mesaj = iha.mesajlar()
        mesaj['iha_otonom'] = 0
        mesaj['mod'] = mod
        iha_tele.send_telemetry(mesaj)
        print(mod)


    except ConnectionResetError as e:
        print("ihada veri koptu1:" + str(e))
        iha_tele.skt.close()
        connected = False
        iha_tele = haberlesme2024_basic.client_TCP()
        while not connected:
            try:
                iha_tele.connected(host, port)
                iha_tele.skt.settimeout(0.001)
                connected = True
            except Exception as e:
                print("ihada veri koptu2:" + str(e))
                time.sleep(1)
                pass
    except Exception as e:
        print("ihada veri koptu3:" + str(e))
