import Haberlesme
import argparse
import path
import cv2
import Client_Tcp
import Client_Udp
class İha():
    def __init__(self,host):
        self.host=host
        self.Client_Tcp = Client_Tcp.Client(host)
        self.Client_Udp = Client_Udp.Client(host)
        self.Client_Tcp.connect_to_server()

    def IHA_MissionPlanner_Connect(self,tcp):

        parser=argparse.ArgumentParser()
        parser.add_argument('--connect',default=f'tcp:127.0.0.1:{str(tcp)}')
        args=parser.parse_args()
        connection_string=args.connect

        return path.Plane(connection_string)

if __name__ == '__main__':
    iha_obj=İha("10.241.237.125")
    iha=iha_obj.IHA_MissionPlanner_Connect(5762)

    while True:
        try:
            iha_obj.Client_Tcp.send_message_to_server("Telemetri Gonderildi.")
            iha_obj.Client_Udp.send_video()
            print("Frame Gönderildi...")
        except Exception as e:
            print(e)
