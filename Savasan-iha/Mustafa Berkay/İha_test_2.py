import socket
import argparse
import cv2
import json
import numpy as np
import path
import imutils
import base64
import time
import threading


class Iha():
    def __init__(self):
        pass

    def IHA_MissionPlanner_Connect(self, tcp_port):
        parser = argparse.ArgumentParser()
        parser.add_argument('--connect', default=f'tcp:127.0.0.1:{str(tcp_port)}')
        args = parser.parse_args()
        connection_string = args.connect

        return path.Plane(connection_string)

    def IHA_Raspberry_Connect(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--connect', default='/dev/ttyACM0')
        args = parser.parse_args()
        connection_string = args.connect
        return path.Plane(connection_string)

    def get_telemetri_verisi(self, iha: path.Plane):
        self.telemetri_verisi = {
            "takim_numarasi": 1,
            "iha_enlem": float("{:.7f}".format(iha.pos_lat)),
            "iha_boylam": float("{:.7f}".format(iha.pos_lon)),
            "iha_irtifa": float("{:.2f}".format(iha.pos_alt_rel)),
            "iha_dikilme": float("{:.2f}".format(iha.att_pitch_deg)),
            "iha_yonelme": float("{:.2f}".format(iha.att_heading_deg)),
            "iha_yatis": float("{:.2f}".format(iha.att_roll_deg)),
            "iha_hiz": float("{:.2f}".format(iha.groundspeed)),
            "iha_batarya": iha.get_battery(),
            "iha_otonom": 0,
            "iha_kilitlenme": 0,
            "hedef_merkez_X": 0,
            "hedef_merkez_Y": 0,
            "hedef_genislik": 0,
            "hedef_yukseklik": 0,
            "gps_saati": {
                "saat": iha.gps_time.hour,  # datetime.datetime.now().hour,
                "dakika": iha.gps_time.minute,  # datetime.datetime.now().minute,
                "saniye": iha.gps_time.second,  # datetime.datetime.now().second,
                "milisaniye": iha.gps_time.microsecond // 1000,  # int(datetime.datetime.now().microsecond//1000)
            }
        }
        return self.telemetri_verisi

    def change_mod(self, mod_kodu, iha: path.Plane):
        telemetri = self.get_telemetri_verisi(iha)
        print(mod_kodu)
        if mod_kodu == "FBWA":
            telemetri["iha_otonom"] = 0
        else:
            telemetri["iha_otonom"] = 1
        if iha.get_ap_mode() != str(mod_kodu):
            iha.set_ap_mode(str(mod_kodu))




# UDP
udp_host = socket.gethostbyname(socket.gethostname())
udp_port = 9998
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# TCP,
tcp_host = socket.gethostbyname(socket.gethostname())
tcp_port = 9001
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.connect((tcp_host, tcp_port))
print('Connected to TCP server...')


def send_video():
    vid = cv2.VideoCapture(0,cv2.CAP_DSHOW)

    while True:
        try:
            if vid.isOpened():
                ret, frame = vid.read()
                frame = imutils.resize(frame, width=640, height=480)
                encoded_frame, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                data = base64.b64encode(buffer)
                udp_socket.sendto(data, (udp_host, udp_port))

                cv2.imshow('Video from Client', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e :
            print(e)

    vid.release()
    cv2.destroyAllWindows()

# Function to send JSON data via TCP at one-second intervals
def send_json():
    next_send_time = time.time()+1

    while True:

        raw_data = iha_obj.get_telemetri_verisi(iha_path)
        json_string_encoded = json.dumps(raw_data).encode('utf-8')

        # 1 saniye geçene kadar burada dönecek.
        while time.time() < next_send_time:
            pass

        # Json verisi gönderilir.
        tcp_socket.send(json_string_encoded)
        print(iha_obj.get_telemetri_verisi(iha_path))

        next_send_time += 1
        print("1 second passed...")


if __name__ == '__main__':
    iha_obj = Iha()
    iha_path = iha_obj.IHA_MissionPlanner_Connect(5762)

    print("2 Sn bekleniyor...")
    time.sleep(2) #Tüm Bağlantıların Yerine Oturması için 2 sn bekleniyor

    print(iha_obj.get_telemetri_verisi(iha_path))

    # Start UDP video sending thread
    video_thread = threading.Thread(target=send_video)
    video_thread.start()

    # Start TCP JSON data sending thread

    json_thread = threading.Thread(target=send_json,args=())
    json_thread.start()

    video_thread.join()
    json_thread.join()
    
    # Clean up the sockets
    udp_socket.close()
    tcp_socket.close()


    while True:
        try:
            if iha_path.servo6 > 1600 and iha_path.servo7 > 1600:
                iha_obj.change_mod("AUTO", iha_path)
            elif 1400 < iha_path.servo6 < 1600 and iha_path.servo7 > 1600:
                iha_obj.change_mod("RTL", iha_path)
            elif iha_path.servo6 < 1400 and iha_path.servo7 > 1600:
                iha_obj.change_mod("FBWA", iha_path)
        except Exception as e:
            print(e)