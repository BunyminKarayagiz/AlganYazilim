import argparse
import path_px as pt
import time

def IHA_MissionPlanner_Connect(tcp_port=5762):
        parser = argparse.ArgumentParser()
        parser.add_argument('--connect', default=f'tcp:127.0.0.1:{str(tcp_port)}')
        args = parser.parse_args()
        connection_string = args.connect
        return pt.Plane(connection_string)

if __name__ == "__main__":
        iha_path=IHA_MissionPlanner_Connect()
        mainloop = True
        mode = ""

        mode = (iha_path.get_ap_mode())
        print(mode)

        while mainloop:
                if not iha_path.is_armed():
                        print("ARMING...")
                        iha_path.arm_mavlink()
                        print("ARM SUCCESS..")
                        
                time.sleep(0.3)