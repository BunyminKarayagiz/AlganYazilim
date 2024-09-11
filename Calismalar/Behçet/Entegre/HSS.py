import numpy as np
import matplotlib.pyplot as plt
import math
import vincenty
import itertools

class HSS:
    def __init__(self, HSS, konum, roll, pitch, yaw, hiz):
        #! Bizim verilerimiz
        self.x = 0
        self.referans_konum = (40.2301684,28.9983702)
        self.g = 9.81
        self.HSS = [{"id": 0,"hssEnlem": 40.23260922,"hssBoylam": 29.00573015,"hssYaricap": 50 },
                          { "id": 1,"hssEnlem": 40.23351019,"hssBoylam": 28.99976492,"hssYaricap": 50 },
                          {"id": 2,"hssEnlem": 40.23105297, "hssBoylam": 29.00744677, "hssYaricap": 75},
                          {"id": 3,"hssEnlem": 40.23090554,"hssBoylam": 29.00221109,"hssYaricap": 150}]
        self.konum = konum
        self.roll = math.radians(roll)
        self.pitch = math.radians(pitch)
        self.yaw = math.radians(yaw)
        self.hiz = math.radians(hiz)

        #! Rakip verileri
        self.rakip_konum = (40.2301686,28.9983704)
        self.rakip_roll = 0
        self.rakip_pitch = 0
        self.rakip_yaw = 0
        self.rakip_hiz = 0

        #! HSS Verileri 
        self.hss_konum = []
        self.hss_verileri = []
    
    def yaricap_hesapla(self):
        yaricap = (self.hiz ** 2) / (self.g * math.tan(self.roll))
        return yaricap 

    def nokta_uzaklikta_dondur(self):
        uzaklik_farkX = self.rakip_konum[0] - self.konum[0]
        uzaklik_farkY = self.rakip_konum[1] - self.konum[1]
        uzaklik = np.sqrt((uzaklik_farkX ** 2) + (uzaklik_farkY ** 2))

        mesafe = self.yaricap_hesapla()

        t = mesafe / uzaklik

        x_uzaklikta= self.konum[0] + t * uzaklik_farkX
        y_uzaklikta = self.konum[1] + t * uzaklik_farkY

        return (uzaklik_farkX, uzaklik_farkY)

    def cember_olustur(self):
        yaricap = self.yaricap_hesapla()
        konum = self.nokta_uzaklikta_dondur()

        return konum, yaricap
    
    def hss_cember_olustur(self):
        for cember in len(self.HSS):
            enlem = cember['hssEnlem']
            boylam = cember['hssBoylam']
            yaricap = cember['hssYaricap']
            
            hss_konum_verilei = (enlem, boylam)
            self.hss_konum.append(hss_konum_verilei)
            (x_uzaklik, y_uzaklik) = self.nokta_hesapla(hss_konum_verilei)
            self.hss_verileri.append(x_uzaklik, y_uzaklik, yaricap)

    def cember_uzakliklari_hesapla(self):
        uzakliklar = []
        for i in len(self.hss_konum):
            x = self.nokta_hesapla(i)

    def cember_kesisim_check(self):
        pass

    def ciz(self):
        pass

    def nokta_nokta(self, nokta1, nokta2):
        x_uzaklik = abs(nokta1[0] - nokta2[0])
        y_uzaklik = abs(nokta1[1] - nokta2[1])
        
        mesafe = math.sqrt(x_uzaklik ** 2 + y_uzaklik ** 2)

        return mesafe

    def hss_uzaklik_hesaplama(self):
        pass

    def yeni_nokta_olusturma_aci(self):
        pass

    def aralarindaki_aciyi_hesapla(self):
        pass

    def nokta_hesapla(self, konum):
        i = konum
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

        nokta = (x_mesafe, y_mesafe)

        return nokta

    def hesaplamalar(self):
        pass