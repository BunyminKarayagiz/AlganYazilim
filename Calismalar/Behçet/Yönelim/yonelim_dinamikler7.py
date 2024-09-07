# Pitch burada
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

    def hesaplamalar(self, enlem, boylam, irtifa, pitch, hiz, dt):
        # Mevcut koordinatları XYZ'ye dönüştür
        x, y, z = self.coğrafi_koordinatlari_xyzye_donustur(enlem, boylam, irtifa)
        print("baslangic degerleri : ", (x, y, z))

        # Pitch açısını radyana çevir
        pitch = math.radians(pitch)
        
        vx = hiz * math.sin(pitch)
        print("vx : ", vx)

        # Yükseklik değişimini hesapla
        z_change = vx * dt
        print("z_change : ", z_change)
        yeni_enlem, yeni_boylam, yeni_irtifa = self.xyz_koordinatlarini_coğrafi_koordinatlara_donustur(x, y, z)

        yeni_irtifa += z_change

        print("yeni_z : ", yeni_irtifa)
        
        # Yeni coğrafi koordinatları hesapla
        
        return yeni_enlem, yeni_boylam, yeni_irtifa
    
    def start(self):
        enlem, boylam, irtifa = 41.0082, 28.9784, 100
        yeni_enlem, yeni_boylam, yeni_irtifa = self.hesaplamalar(enlem, boylam, irtifa, 30, 20, 5)
        print(f'Tahmin Enlem: {yeni_enlem} -- Tahmin Boylam: {yeni_boylam} -- Tahmin İrtifa: {yeni_irtifa}')
        konum = [yeni_enlem, yeni_boylam]
        print(f'Tahmin Enlem Boylam: {konum}')

clas = TrajectoryCalculations()
clas.start()