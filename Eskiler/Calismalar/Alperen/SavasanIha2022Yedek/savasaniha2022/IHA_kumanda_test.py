
import path
import time
import argparse
import cv2
import hesaplamalar, haberlesme
import json
from dronekit import LocationGlobalRelative
import datetime
import ast
import os

parser = argparse.ArgumentParser()
parser.add_argument('--connect', default='/dev/ttyACM0')
args = parser.parse_args()
connection_string = args.connect
# -- Tuygun Bağlantı
iha = path.Plane(connection_string)
  
while True:
    try:
        
        
        print("1:",iha.servo1)
        print("2:",iha.servo2)
        print("3:",iha.servo3)
        print("4:",iha.servo4)
        print("switch  6:",iha.ch6)
        print("switch 7:",iha.ch7)
        print("---------------------------------------")
        
        
   
        mesaj = iha.mesajlar()
        if time.time() - sure > 0.1:
            sure = time.time()
            
          

            # AUTO
            if iha.ch6 > 1400 :  # Servo6: High, Servo7: Mid
                mesaj['IHA_otonom'] = 1
                if iha.get_ap_mode() != "AUTO":
                    iha.set_ap_mode("AUTO")
            # FBWA
            if iha.ch6 > 1400 and iha.ch6 < 1600 :  # Servo6: High, Servo7: Mid
                mesaj['IHA_otonom'] = 0
                if iha.get_ap_mode() != "FBWA":
                    iha.set_ap_mode("FBWA")
            
            # RTL
            if iha.ch6 < 1400 :  # Servo6: High, Servo7: Mid
                mesaj['IHA_otonom'] = 1
                if iha.get_ap_mode() != "RTL":
                    iha.set_ap_mode("RTL")
     
            iha_tele.telemetri_gonder(mesaj)
            #print(mesaj)

    except ConnectionResetError as e:
        print("ihada veri koptu1:" + str(e))
        iha_tele.s.close()
        connected = False
        iha_tele = haberlesme.client_TCP()
        while not connected:
            try:
                iha_tele.baglan(host, port)
                iha_tele.s.settimeout(0.001)
                connected = True
            except Exception as e:
                print("ihada veri koptu2:" + str(e))
                time.sleep(1)
                pass
    except Exception as e:
        print("ihada veri koptu3:" + str(e))
        
        