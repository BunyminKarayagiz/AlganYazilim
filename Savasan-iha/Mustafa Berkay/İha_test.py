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


class client_tcp_telemetri:
    def __init__(self) -> None:
        self.IP= socket.gethostbyname(socket.gethostname())
        self.Port = 9000
        try:
            print("Socket Created...")
            self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            print("Connecting...")
            self.client_socket.connect((self.IP,self.Port))
        except Exception as e:
            print(e)

    def timer_telemetri(self,message,interval=1.0):
        while True:
            time_1 = time.time()

            while True:
                time_2= time.time()

                if (time_2 - time_1 >= interval): 
                    print("while time : True")
                    
                    #Function below
                    try:
                        data_to_send = message
                        json_data = json.dumps(data_to_send)
                        self.client_socket.send(json_data.encode("utf-8"))
                        print(f"Sent data: {json_data}")
                    except Exception as e:
                        print(f"Error sending data: {e}")
                    
                    break                 

    def close(self):
        self.client_socket.close()

class client_udp_video: 
    def __init__(self):
        self.BUFF_SIZE = 65536
        self.Main_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.Main_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.BUFF_SIZE) 
        self.port = 9999
        self.host = socket.gethostbyname(socket.gethostname())
        self.vid = cv2.VideoCapture(0)
        self.WIDTH = 640
        self.HEIGHT = 480

    def send_video(self):
        try:
            if self.vid.isOpened():
                ret, frame = self.vid.read()
                frame = imutils.resize(frame, width=self.WIDTH, height=self.HEIGHT)
                encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                message = base64.b64encode(buffer)
                self.Main_socket.sendto(message, (self.host, self.port))
        except Exception as e:
            print("Video Gönderimi Koptu: ", e)


def timer_thread(function,*args,**kwargs):
        while True:
            time_1 = time.time()

            while True:
                time_2= time.time()

                if (time_2 - time_1 >= 1): 
                    print("while time : True")
                    function(*args,**kwargs)
                    break
        
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


# def timer_thread(function,*args,**kwargs):
#         while True:
#             time_1 = time.time()

#             while True:
#                 time_2= time.time()

#                 if (time_2 - time_1 >= 1): 
#                     print("while time : True")
#                     function(*args,**kwargs)
#                     break


if __name__ == '__main__':
    iha_obj = Iha()
    iha_path = iha_obj.IHA_MissionPlanner_Connect(5762)

    video_class = client_udp_video()
    telemetri_class = client_tcp_telemetri()
     
    print("2 Sn bekleniyor...")
    time.sleep(2) #Tüm Bağlantıların Yerine Oturması için 3 sn bekleniyor

    message = iha_obj.get_telemetri_verisi(iha_path)
    print(message)
    

    Thread_telemetri = threading.Thread(target=telemetri_class.timer_telemetri,args=(message))

    Thread_vid = threading.Thread(target=video_class.send_video,args=())
    Thread_vid.start()


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