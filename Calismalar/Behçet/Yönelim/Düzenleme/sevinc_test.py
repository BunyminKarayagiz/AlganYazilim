import numpy as np
import vincenty
from pymavlink import mavutil
import matplotlib.pyplot as plt
from matplotlib.path import Path
from shapely.geometry import Point, Polygon
import time

referans_konum = (37.7409072, 29.0911317)
def poligon_hesapla():
    def kartezyen_to_enlem_boylam(nokta, home_konumu):
        x_mesafe, y_mesafe = nokta
        # Enlem ve boylamı hesapla
        enlem = home_konumu[0] + y_mesafe / 111000  # 1 enlem derecesi yaklaşık 111 km'ye denk gelir
        boylam = home_konumu[1] + x_mesafe / (111000 * np.cos(np.radians(home_konumu[0])))
        nokta_yeni = (enlem, boylam)
        return nokta_yeni

    def nokta_hesapla(konum):
        i=konum
        y_ussu = (i[0], referans_konum[1])
        x_ussu = (referans_konum[0], i[1])

        y_mesafe = vincenty.vincenty(y_ussu, referans_konum)
        x_mesafe = vincenty.vincenty(x_ussu, referans_konum)
        # x i negatif yapmak için  boylamının home boylamından küçük olması gerekir
        if i[1] < referans_konum[1]:
            x_mesafe = x_mesafe * -1000
        else:
            x_mesafe = x_mesafe * 1000
        # y i negatif yapmak için enlemi home enleminin altında olması gerekir
        if i[0] < referans_konum[0]:
            y_mesafe = y_mesafe * -1000
        else:
            y_mesafe = y_mesafe * 1000
        nokta = (x_mesafe, y_mesafe, i[2])
        return nokta
    def noktayı_döndür(konum, açı):
        x, y = konum[0], konum[1]
        # Açıyı radyan cinsine çevir
        θ = np.deg2rad(açı)

        # Yeni koordinatları hesapla
        x_prime = x * np.cos(θ) - y * np.sin(θ)
        y_prime = x * np.sin(θ) + y * np.cos(θ)

        return x_prime, y_prime,



    def nokta_belirleme(konum0,hiz,yaw):
        konum=nokta_hesapla(konum0)
       # print(konum)
        # bir sonraki konumunun bulunma ihtimali en yüsek olan alanı belirleme
        #bu alan 5 nokta ile ifade edilecektir
        # a b c d e noktaları olarak isimlendirilecektir.
        #æ noktası için
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
        a=noktayı_döndür(a,-yaw)
        b=noktayı_döndür(b,-yaw)
        c=noktayı_döndür(c,-yaw)
        d=noktayı_döndür(d,-yaw)
        a=konum[0]+a[0],konum[1]+a[1]
        b=konum[0]+b[0],konum[1]+b[1]
        c=konum[0]+c[0],konum[1]+c[1]
        d=konum[0]+d[0],konum[1]+d[1]
        #print(f"a:{a}\n b:{b}\n c:{c}\n d:{d}\n e:{e}")


        return a,b,c,d


    a,b,c,d =nokta_belirleme(konum,hiz,acilar[2])
    tahmin=[(a[0],a[1]),(b[0],b[1]),(c[0],c[1]),(d[0],d[1])]
    a_=kartezyen_to_enlem_boylam(a,referans_konum)
    b_=kartezyen_to_enlem_boylam(b,referans_konum)
    c_=kartezyen_to_enlem_boylam(c,referans_konum)
    d_=kartezyen_to_enlem_boylam(d,referans_konum)
    return a_,b_,c_,d_

a_,b_,c_,d_=poligon_hesapla()