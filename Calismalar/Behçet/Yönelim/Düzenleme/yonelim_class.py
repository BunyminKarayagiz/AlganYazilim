import math
import numpy as np
import time  # Gecikme eklemek için gerekli
import matplotlib.pyplot as plt
from pymavlink import mavutil
from colorama import Fore, init

class yonelim:
    def __init__(self, enlem, boylam, irtifa, roll, pitch, yaw, hiz, zaman):
        self.R = 6371000
        self.enlem = enlem
        self.boylam = boylam
        self.irtifa = irtifa
        self.roll = np.deg2rad(roll)
        self.pitch = np.deg2rad(pitch)
        self.yaw = np.deg2rad(yaw)
        self.hiz = hiz
        self.zaman = zaman
        self.g = 9.81
        self.konumlar = []
        init(autoreset=True)
        self.konum_hesapla()

    def mission_planner_connect(self):
        iha = mavutil.mavlink_connection('tcp:127.0.0.1:5762')
        return iha
    
    def mission_planner_veri_alma(self):
        iha = self.mission_planner_connect()
        # ATTITUDE mesajını al
        msg = iha.recv_match(type='ATTITUDE', blocking=True)
        if msg is not None and msg.get_type() == 'ATTITUDE':
            roll = msg.roll
            pitch = msg.pitch
            yaw = msg.yaw
            print(Fore.RED + f'ROLL : {roll} PİTCH : {pitch} YAW : {yaw}')
        else:
            roll = pitch = yaw = None  # Eğer mesaj alınamazsa None döndür

        # VFR_HUD mesajını al
        msg = iha.recv_match(type='VFR_HUD', blocking=True)
        if msg is not None and msg.get_type() == 'VFR_HUD':
            speed = msg.groundspeed
        else:
            speed = None  

        msg = iha.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        if msg is not None and msg.get_type() == 'GLOBAL_POSITION_INT':
            x = msg.lat / 1e7
            y = msg.lon / 1e7
            z = msg.relative_alt / 1000
        else:
            x = y = z = None  

        acilar = (roll, pitch, yaw)
        konum = (x, y, z)
        hiz = speed

        return acilar, konum, hiz

    def coğrafi_koordinatlari_xyzye_donustur(self):
        enlem = math.radians(self.enlem)
        boylam = math.radians(self.boylam)
        
        x = (self.R + self.irtifa) * math.cos(enlem) * math.cos(boylam)
        y = (self.R + self.irtifa) * math.cos(enlem) * math.sin(boylam)
        z = (self.R + self.irtifa) * math.sin(enlem)
        
        return x, y, z

    def xyz_koordinatlarini_coğrafi_koordinatlara_donustur(self, x, y, z):
        irtifa = math.sqrt(x**2 + y**2 + z**2) - self.R
        enlem = math.degrees(math.asin(z / (self.R + irtifa)))
        boylam = math.degrees(math.atan2(y, x))
        
        return enlem, boylam, irtifa
    
    def roll_donus(self, x, y, z):
        y_prime = y * np.cos(self.roll) - z * np.sin(self.roll)
        z_prime = y * np.sin(self.roll) + z * np.cos(self.roll)
        return x, y_prime, z_prime
    
    def pitch_donus(self, x, y, z):
        x_prime = x * np.cos(self.pitch) + z * np.sin(self.pitch)
        z_prime = -x * np.sin(self.pitch) + z * np.cos(self.pitch)
        return x_prime, y, z_prime
    
    def yaw_donus(self, x, y, z):
        x_prime = x * np.cos(self.yaw) - y * np.sin(self.yaw)
        y_prime = x * np.sin(self.yaw) + y * np.cos(self.yaw)
        return x_prime, y_prime, z
    
    def konum_hesapla(self):
        while True:  # Sonsuz döngü
            veriler = self.mission_planner_veri_alma()  # Mission Planner'dan veri al
            roll, pitch, yaw = veriler[0]
            enlem, boylam, irtifa = veriler[1]
            hiz = veriler[2]

            # Yeni verileri güncelle
            if roll is not None and pitch is not None and yaw is not None:
                self.roll = np.deg2rad(roll)
                self.pitch = np.deg2rad(pitch)
                self.yaw = np.deg2rad(yaw)
            if enlem is not None and boylam is not None and irtifa is not None:
                self.enlem = enlem
                self.boylam = boylam
                self.irtifa = irtifa
            if hiz is not None:
                self.hiz = hiz

            x, y, z = self.coğrafi_koordinatlari_xyzye_donustur()

            for i in range(10):
                x, y, z = self.yaw_donus(x, y, z)
                x, y, z = self.pitch_donus(x, y, z)
                x, y, z = self.roll_donus(x, y, z)

                x += self.hiz * self.zaman * np.cos(self.yaw) * np.cos(self.pitch)
                y += self.hiz * self.zaman * np.sin(self.yaw) * np.cos(self.pitch)
                z += self.hiz * self.zaman * np.sin(self.pitch)

                enlem, boylam, irtifa = self.xyz_koordinatlarini_coğrafi_koordinatlara_donustur(x, y, z)
                self.konumlar.append((enlem, boylam, irtifa))

                print((enlem, boylam, irtifa))

            print("Mission Planner Verileri: ", veriler)

            # Gecikme eklemek için time.sleep kullanın
            time.sleep(1)  # 1 saniyelik gecikme, ihtiyaca göre ayarlanabilir

        # Bu return ifadesi sonsuz döngü içinde olduğu için asla çalışmayacak, ancak döngüyü manuel olarak durdurursanız son konumu almak için kullanılabilir.
        return self.konumlar[-1]

# Örnek başlatma
yonelim_start = yonelim(41.0086, 28.9802, 100, 0, 20, 0, 20, 5)