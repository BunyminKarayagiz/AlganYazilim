import Haberlesme
import argparse
import path

class İha():
    def __init__(self,host):
        self.host=host
        self.Client=Haberlesme.Udp_Client(self.host)

    def IHA_MissionPlanner_Connect(self,tcp):

        parser=argparse.ArgumentParser()
        parser.add_argument('--connect',default=f'tcp:127.0.0.1:{str(tcp)}')
        args=parser.parse_args()
        connection_string=args.connect

        return path.Plane(connection_string)

if __name__ == '__main__':
    iha_obj=İha("192.168.222.180")
    iha=iha_obj.IHA_MissionPlanner_Connect(5762)
    print("a")
    while True:
        print(iha.get_ap_mode())
        iha_obj.Client.send_video()