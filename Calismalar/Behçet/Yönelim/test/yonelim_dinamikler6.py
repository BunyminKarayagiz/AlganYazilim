import math

class TrajectoryCalculations:
    def __init__(self):
        self.R = 6371000  # Dünya'nın ortalama yarıçapı (metre)

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

    def hesaplamalar(self, enlem, boylam, irtifa, roll, pitch, yaw, hiz, sure):
        x, y, z = self.coğrafi_koordinatlari_xyzye_donustur(enlem, boylam, irtifa)
        
        # Açılar radiyana dönüştürülür
        roll = math.radians(roll)
        pitch = math.radians(pitch)
        yaw = math.radians(yaw)
        
        # Yaw dönüşümünü uygulama (X ve Y eksenlerinde)
        vx = hiz * math.cos(yaw)
        vy = hiz * math.sin(yaw)
        vz = hiz * math.sin(pitch)
        
        # Roll dönüşümünü uygula
        vx_roll = vx
        vy_roll = vy * math.cos(roll) - vz * math.sin(roll)
        vz_roll = vy * math.sin(roll) + vz * math.cos(roll)

        # Yeni x, y, z koordinatlarını hesapla
        X = x + vx_roll * sure
        Y = y + vy_roll * sure
        Z = z + vz_roll * sure
        
        # Koordinatları coğrafi koordinatlara dönüştür
        yeni_enlem, yeni_boylam, yeni_irtifa = self.xyz_koordinatlarini_coğrafi_koordinatlara_donustur(X, Y, Z)
        
        return yeni_enlem, yeni_boylam, yeni_irtifa
    
    def start(self):
        enlem, boylam, irtifa = 41.0082, 28.9784, 100
        yeni_enlem, yeni_boylam, yeni_irtifa = self.hesaplamalar(enlem, boylam, irtifa, 0, 0, 90, 20, 10)
        print(f'Tahmin Enlem {yeni_enlem} -- Tahmin Boylam {yeni_boylam} -- Tahmin İrtifa {yeni_irtifa}')
        konum = [yeni_enlem, yeni_boylam]
        print(f'Tahmin Enlem Boylam {konum}')

clas = TrajectoryCalculations()
clas.start()
