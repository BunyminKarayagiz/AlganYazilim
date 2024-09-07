import numpy as np
import math

class TrajectoryCalculations:
    def __init__(self):
        self.R = 6371000 
    def coğrafi_koordinatlari_xyzye_donustur(self, enlem, boylam, irtifa):
        enlem = math.radians(enlem)
        boylam = math.radians(boylam)
        
        x = (self.R + irtifa) * math.cos(enlem) * math.cos(boylam)
        y = (self.R + irtifa) * math.cos(enlem) * math.sin(boylam)
        z = (self.R + irtifa) * math.sin(enlem)
        
        return x, y, z

    def xyz_koordinatlarini_coğrafi_koordinatlara_donustur(self, x, y, z):
        irtifa = math.sqrt(x**2 + y**2 + z**2) - self.R
        enlem = math.degrees(math.asin(z / (self.R + irtifa)))
        boylam = math.degrees(math.atan2(y, x))
        
        return enlem, boylam, irtifa

    def hesaplamalar(self, enlem, boylam, irtifa, roll, hiz, dt):
        x, y, z = self.coğrafi_koordinatlari_xyzye_donustur(enlem, boylam, irtifa)
        print("Başlangıç değerleri (x, y, z):", (x, y, z))

        roll = math.radians(roll)

        vx = hiz * math.cos(roll)
        vy = hiz * math.sin(roll)
        print("vx:", vx)
        print("vy:", vy)
        
        x_change = vx * dt
        y_change = vy * dt
        print("x_change:", x_change)
        print("y_change:", y_change)
        
        xs = x + x_change
        ys = y + y_change
        zs = z 
        
        yeni_enlem, yeni_boylam, yeni_irtifa = self.xyz_koordinatlarini_coğrafi_koordinatlara_donustur(xs, ys, zs)
        
        return yeni_enlem, yeni_boylam, yeni_irtifa

    def start(self):
        enlem, boylam, irtifa = 41.0082, 28.9784, 100
        yeni_enlem, yeni_boylam, yeni_irtifa = self.hesaplamalar(enlem, boylam, irtifa, 30, 20, 5)
        print(f'Tahmin Enlem: {yeni_enlem} -- Tahmin Boylam: {yeni_boylam} -- Tahmin İrtifa: {yeni_irtifa}')

clas = TrajectoryCalculations()
clas.start()
