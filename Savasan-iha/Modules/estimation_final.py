import numpy as np
import vincenty
from pymavlink import mavutil
import matplotlib.pyplot as plt
from matplotlib.path import Path
from shapely.geometry import Point, Polygon
import time

def poligon_hesapla():

    def connect():
        iha= mavutil.mavlink_connection('tcp:127.0.0.1:5762')
        return iha

    def veri_alma(iha):
        # ATTITUDE mesajını al
        msg = iha.recv_match(type='ATTITUDE', blocking=True)
        if msg is not None and msg.get_type() == 'ATTITUDE':
            roll = msg.roll
            pitch = msg.pitch
            yaw = msg.yaw
        else:
            roll = pitch = yaw = None  # Eğer mesaj alınamazsa None döndür

        # VFR_HUD mesajını al
        msg = iha.recv_match(type='VFR_HUD', blocking=True)
        if msg is not None and msg.get_type() == 'VFR_HUD':
            speed = msg.groundspeed
        else:
            speed = None  # Eğer mesaj alınamazsa None döndür

        # GLOBAL_POSITION_INT mesajını al
        msg = iha.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        if msg is not None and msg.get_type() == 'GLOBAL_POSITION_INT':
            x = msg.lat / 1e7  # Derece cinsinden enlem
            y = msg.lon / 1e7  # Derece cinsinden boylam
            z = msg.relative_alt / 1000  # Metre cinsinden yükseklik
        else:
            x = y = z = None  # Eğer mesaj alınamazsa None döndür

        acilar = (roll, pitch, yaw)
        konum = (x, y, z)
        hiz = speed

        return acilar, konum, hiz
    
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

    def ciz(cizim_listesi):
        """
        Verilen cizim_listesi'ndeki her bir öğeyi, belirtilen renkte çizer:
        - Her öğe, çizilecek şekillerin listesi ve renk bilgisini içeren bir tuple olmalıdır.
        """
        plt.figure(figsize=(6, 6))

        for cizilecekler, renk in cizim_listesi:
            renk_kodlari = {'kırmızı': 'r', 'yeşil': 'g', 'mavi': 'b'}
            cizim_rengi = renk_kodlari.get(renk, 'r')  # Varsayılan renk kırmızıdır

            if isinstance(cizilecekler, list):
                if all(len(item) == 3 for item in cizilecekler):
                    # Çemberleri çiz
                    for h, k, radius in cizilecekler:
                        theta = np.linspace(0, 2 * np.pi, 100)
                        x = h + radius * np.cos(theta)
                        y = k + radius * np.sin(theta)
                        plt.plot(x, y, cizim_rengi)
                elif all(len(item) == 2 for item in cizilecekler):
                    # Noktaları çiz
                    for x, y in cizilecekler:
                        plt.plot(x, y, cizim_rengi + 'o', markersize=5)  # 'o' nokta anlamına gelir
            elif isinstance(cizilecekler, tuple) and len(cizilecekler) == 2:
                # Tek bir nokta çiz
                plt.plot(cizilecekler[0], cizilecekler[1], cizim_rengi + 'o')
            elif isinstance(cizilecekler, tuple) and len(cizilecekler) == 3:
                # Sadece çember çiz
                h, k, radius = cizilecekler
                theta = np.linspace(0, 2 * np.pi, 100)
                x = h + radius * np.cos(theta)
                y = k + radius * np.sin(theta)
                plt.plot(x, y, cizim_rengi)

        # Eksen isimleri
        plt.xlabel('X ekseni')
        plt.ylabel('Y ekseni')
        # grafiğin altında açıklama yap renkleri ve neyi gösterdiğini açıkla
        plt.text(0, 1.3, 'Kırmızı: Yasaklı alanlar \nYeşil: Uçuş Rotası\nMavi: Uçuş Alanı',
                 horizontalalignment='left', verticalalignment='top',
                 transform=plt.gca().transAxes, fontsize=10,
                 bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
        plt.title('Kartezyen Koordinat Sistemi Üzerinde Çeşitli Şekiller')

        # Izgara
        plt.grid(color='grey', linestyle='--', linewidth=0.5)

        # Eşit oranlı eksenler
        plt.gca().set_aspect('equal', adjustable='box')

        # Göster
        plt.show()

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
    
    def nokta_poligon_icinde_mi(nokta, poligon):
        # Noktanın poligonun içinde olup olmadığını kontrol et
        path = Path(poligon)
        return path.contains_point(nokta)

    #np.set_printoptions(suppress=True)
    #poligonun tepe noktasını bulmak için
    referans_konum = (37.7348492, 29.0947473)

    np.set_printoptions(suppress=True, precision=6)

    #önceki tahmin ve şimdiki konum eşit olmalıdır
    onceki_tahmin=((0,0),(0,0),(0,0),(0,0),(0,0))
    tahmin=((0,0),(0,0),(0,0),(0,0),(0,0))
    iha= connect()
    for _ in range (3):
        acilar, konum, hiz = veri_alma(iha)
        onceki_tahmin=tahmin
        nokta=nokta_hesapla(konum)
        a,b,c,d =nokta_belirleme(konum,hiz,konum[2])
        tahmin=[(a[0],a[1]),(b[0],b[1]),(c[0],c[1]),(d[0],d[1])]
        a_=kartezyen_to_enlem_boylam(a,referans_konum)
        b_=kartezyen_to_enlem_boylam(b,referans_konum)
        c_=kartezyen_to_enlem_boylam(c,referans_konum)
        d_=kartezyen_to_enlem_boylam(d,referans_konum)
        print(f"Önceki Tahmin:{onceki_tahmin} \nNokta:{nokta} ")
        print(nokta_poligon_icinde_mi(nokta,onceki_tahmin))
        cizim_listesi = [
            (onceki_tahmin, 'kırmızı'),
            ((nokta[0],nokta[1]), 'mavi')
        ]
        ciz(cizim_listesi)
        time.sleep(0.7)
    return a_,b_,c_,d_

poligon_hesapla()