import numpy as np
import vincenty
from pymavlink import mavutil
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
import time
import math
from colorama import Fore, init

class yonelim:
    def __init__(self):
        self.konum = None
        self.hiz = None
        self.roll = None
        self.pitch = None
        self.yaw = None
        self.iha = None
        self.referans_konum = (37.7409072, 29.0911317)
        init(autoreset=True)
        self.yonelim_start()

    def connect(self):
        self.iha= mavutil.mavlink_connection('tcp:127.0.0.1:5762')
        return self.iha
    
    def veri_alma(self):
        # ATTITUDE mesajını al
        msg = self.iha.recv_match(type='ATTITUDE', blocking=True)
        if msg is not None and msg.get_type() == 'ATTITUDE':
            roll = msg.roll
            pitch = msg.pitch
            yaw = msg.yaw
        else:
            roll = pitch = yaw = None  # Eğer mesaj alınamazsa None döndür

        # VFR_HUD mesajını al
        msg = self.iha.recv_match(type='VFR_HUD', blocking=True)
        if msg is not None and msg.get_type() == 'VFR_HUD':
            speed = msg.groundspeed
        else:
            speed = None  # Eğer mesaj alınamazsa None döndür

        # GLOBAL_POSITION_INT mesajını al
        msg = self.iha.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        if msg is not None and msg.get_type() == 'GLOBAL_POSITION_INT':
            x = msg.lat / 1e7  # Derece cinsinden enlem
            y = msg.lon / 1e7  # Derece cinsinden boylam
            z = msg.relative_alt / 1000  # Metre cinsinden yükseklik
        else:
            x = y = z = None  # Eğer mesaj alınamazsa None döndür

        roll = math.degrees(roll)
        pitch = math.degrees(pitch)
        yaw = math.degrees(yaw)

        acilar = (roll, pitch, yaw)
        konum = (x, y, z)
        hiz = speed

        return acilar, konum, hiz

    def kartezyen_to_enlem_boylam(self, nokta, home_konumu):
        x_mesafe, y_mesafe = nokta
        # Enlem ve boylamı hesapla
        enlem = home_konumu[0] + y_mesafe / 111000  # 1 enlem derecesi yaklaşık 111 km'ye denk gelir
        boylam = home_konumu[1] + x_mesafe / (111000 * np.cos(np.radians(home_konumu[0])))
        nokta_yeni = (enlem, boylam)
        return nokta_yeni

    def nokta_hesapla(self, konum):
        i=konum
        y_ussu = (i[0], self.referans_konum[1])
        x_ussu = (self.referans_konum[0], i[1])

        y_mesafe = vincenty.vincenty(y_ussu, self.referans_konum)
        x_mesafe = vincenty.vincenty(x_ussu, self.referans_konum)
        
        # x i negatif yapmak için  boylamının home boylamından küçük olması gerekir
        if i[1] < self.referans_konum[1]:
            x_mesafe = x_mesafe * -1000
        else:
            x_mesafe = x_mesafe * 1000
        
        # y i negatif yapmak için enlemi home enleminin altında olması gerekir
        if i[0] < self.referans_konum[0]:
            y_mesafe = y_mesafe * -1000
        else:
            y_mesafe = y_mesafe * 1000
            
        nokta = (x_mesafe, y_mesafe, i[2])
        
        return nokta

    def noktayi_dondur(self, konum, aci):
        x, y = konum[0], konum[1]
        θ = np.deg2rad(aci)

        x_prime = x * np.cos(θ) - y * np.sin(θ)
        y_prime = x * np.sin(θ) + y * np.cos(θ)

        return x_prime, y_prime

    def noktayi_belirle(self, konum0, hiz, yaw):
        konum0 = self.konum
        hiz = self.hiz
        yaw = self.yaw

        konum=self.nokta_hesapla(konum0)
       # print(konum)
        # bir sonraki konumunun bulunma ihtimali en yüsek olan alanı belirleme
        #bu alan 5 nokta ile ifade edilecektir
        # a b c d e noktaları olarak isimlendirilecektir.

        #a noktası için
        a_x=(hiz-4)*np.cos(np.deg2rad(0))
        a_y=(hiz-3)*np.sin(np.deg2rad(0))
        a=(a_x,a_y)

        #b noktası için
        b_x=(hiz+4)*np.cos(np.deg2rad(0))
        b_y=(hiz+4)*np.sin(np.deg2rad(90))
        b=(b_x,b_y)

        #c noktası için
        c_x=(hiz+4)*np.cos(np.deg2rad(180))
        c_y=(hiz+4)*np.sin(np.deg2rad(90))
        c=(c_x,c_y)

        #d noktası için
        d_x=(hiz-4)*np.cos(np.deg2rad(180))
        d_y=(hiz-4)*np.sin(np.deg2rad(0))
        d=(d_x,d_y)
        #e noktası için
        #print(f"a:{a}\n b:{b}\n c:{c}\n d:{d}\n e:{e}")
        yaw=np.rad2deg(yaw)

        a= self.noktayi_dondur(a,-yaw)
        b= self.noktayi_dondur(b,-yaw)
        c= self.noktayi_dondur(c,-yaw)
        d= self.noktayi_dondur(d,-yaw)

        a=konum[0]+a[0],konum[1]+a[1]
        b=konum[0]+b[0],konum[1]+b[1]
        c=konum[0]+c[0],konum[1]+c[1]
        d=konum[0]+d[0],konum[1]+d[1]
        #print(f"a:{a}\n b:{b}\n c:{c}\n d:{d}\n e:{e}")

        return a,b,c,d

    def poligon_hesapla(self, x,y,speed,roll_degree,pitch_degree,rotation_yaw):
        a,b,c,d = self.noktayi_belirle(konum0=(x, y), hiz=speed, yaw=rotation_yaw)
        tahmin=[(a[0],a[1]),(b[0],b[1]),(c[0],c[1]),(d[0],d[1])]
        a_=self.kartezyen_to_enlem_boylam(a, self.referans_konum)
        b_=self.kartezyen_to_enlem_boylam(b,self.referans_konum)
        c_=self.kartezyen_to_enlem_boylam(c,self.referans_konum)
        d_=self.kartezyen_to_enlem_boylam(d,self.referans_konum)
        
        return a_,b_,c_,d_
    
    def yonelim_start(self):
        self.iha = self.connect()
        if self.iha is not None:
            while True:  # Sürekli veri çekmek için döngü
                acilar, self.konum, self.hiz = self.veri_alma()
                self.roll, self.pitch, self.yaw = acilar

                if self.konum and self.hiz is not None:
                    print(Fore.GREEN + f"Açılar: {acilar}, Konum: {self.konum}, Hız: {self.hiz}")
                    
                else:
                    print("Veri alinamadi.")
        else:
            print("Bağlanti hatasi...")

yonelim()