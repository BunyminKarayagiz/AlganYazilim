import vincenty
import sympy as sp
from sympy import Eq, symbols, solve
import numpy as np
import matplotlib.pyplot as plt
try:
    target_locations =((40.23270730	,29.00266170),
(40.23260920	,29.00547270),
(40.23131490	,29.00581600),
(40.23151170	,29.00257590))

    home_konumu = (40.2306557, 29.0010148)

    fence_konumları=((40.23281400,	29.00449100,25),
    (40.23203590,	29.00566580	,25),
    (40.23142980	,29.00416370,25	))



    wp_kartezyen = []
    fence_kartezyen = []


    def wp_konum_hesapla(target_locations):
        for i in target_locations:
            y_ussu = (i[0], home_konumu[1])
            x_ussu = (home_konumu[0], i[1])

            y_mesafe = vincenty.vincenty(y_ussu, home_konumu)
            x_mesafe = vincenty.vincenty(x_ussu, home_konumu)
            #x i negatif yapmak için  boylamının home boylamından küçük olması gerekir
            if i[1] < home_konumu[1]:
                x_mesafe = x_mesafe * -1000
            else:
                x_mesafe = x_mesafe * 1000
            #y i negatif yapmak için enlemi home enleminin altında olması gerekir
            if i[0] < home_konumu[0]:
                y_mesafe = y_mesafe * -1000
            else:
                y_mesafe = y_mesafe * 1000

            nokta = (x_mesafe, y_mesafe)
            wp_kartezyen.append(nokta)
        return wp_kartezyen

    def fence_konum_hesapla(fence_konumları):
        for i in fence_konumları:
            y_ussu = (i[0], home_konumu[1])
            x_ussu = (home_konumu[0], i[1])

            x_mesafe = vincenty.vincenty(x_ussu, home_konumu)
            y_mesafe = vincenty.vincenty(y_ussu, home_konumu)
            # Burada eğer konum home konumunun olunda kalıyorsa x_mesafe değerini -1 ile çarp
            if i[1] < home_konumu[1]:
                x_mesafe = x_mesafe * -1000
            else:
                x_mesafe = x_mesafe * 1000

            if i[0] < home_konumu[0]:
                y_mesafe = y_mesafe * -1000
            else:
                y_mesafe = y_mesafe * 1000
            nokta = (x_mesafe, y_mesafe, i[2])
            fence_kartezyen.append(nokta)
        return fence_kartezyen

    def dogru_denklemi_olustur(x1, x2, y1, y2):
        m = (y2 - y1) / (x2 - x1)
        x_katsayı = m
        sabit = -m * x1 + y1
        x, y = sp.symbols('x y')
        dogru_denklemi = Eq(y, x_katsayı * x + sabit)
        return dogru_denklemi

    def cember_denklemi(a, b, radius):
        r = radius
        # çember denklemi (x-a)^2 + (y-b)^2 = r^2
        x, y = sp.symbols('x y')
        cember_denklemi = Eq((x - a) ** 2 + (y - b) ** 2, r ** 2)
        return cember_denlemi


    def kesisim_kontrol(nokta1, nokta2, cember):
        h, k, r = cember
        dx = nokta2[0] - nokta1[0]
        dy = nokta2[1] - nokta1[1]
        if dx != 0:
            m = dy / dx
            b = nokta1[1] - m * nokta1[0]
            # Çemberin merkezi ile doğru parçası arasındaki en kısa mesafe
            d = abs(m * h - k + b) / np.sqrt(m ** 2 + 1)
        else:
            # Eğer doğru dikeyse, x koordinatları aynıdır ve mesafe hesaplanabilir
            d = abs(nokta1[0] - h)

        # Çemberin içinde mi dışında mı kontrolü
        return d <= r


    def yeni_nokta_olusturma(nokta1, nokta2, cember):
        h, k, r = cember
        dx, dy = nokta2[0] - nokta1[0], nokta2[1] - nokta1[1]
        egim = dy / dx  # İki nokta arasındaki eğim
        normal_egim = -1 / egim  # Dik doğrunun eğimi
        uzaklik = r * 1.5
        yeni_x = h + uzaklik / np.sqrt(1 + normal_egim ** 2)
        yeni_y = k + normal_egim * (yeni_x - h)

        return (yeni_x, yeni_y)


    #burada noktaları kartezyen sisteme dönüştürüyoruz
    wp_konum_hesapla(target_locations)
    print(wp_kartezyen)
    fence_konum_hesapla(fence_konumları)
    print(fence_kartezyen)
    #burada ise kesişim noktalarını buluyoruz
    kesisim=[]
    yeni_wp_kartezyen=[]
    for wp in wp_kartezyen:
        try:
            sonraki_konum = wp_kartezyen[wp_kartezyen.index(wp) + 1]

        except:
            sonraki_konum = wp_kartezyen[0]
            yeni_wp_kartezyen.append(wp)

        for fence in fence_kartezyen:
            dogru = dogru_denklemi_olustur(wp[0],sonraki_konum[0] ,wp[1] ,sonraki_konum[1] )
            cember = cember_denklemi(fence[0], fence[1], fence[2])
            kesisin_varmi=kesisim_kontrol(wp, sonraki_konum, fence)
            if kesisin_varmi==True:
                yeni_nokta=yeni_nokta_olusturma(wp, sonraki_konum, fence)
                yeni_wp_kartezyen.append(yeni_nokta)



    print(yeni_wp_kartezyen)
    cemberler=fence_kartezyen
    noktalar=wp_kartezyen

    plt.figure(figsize=(6, 6))

    # Çemberleri çiz
    for i in cemberler:
        h, k, radius = i
        theta = np.linspace(0, 2*np.pi, 100)
        x = h + radius * np.cos(theta)
        y = k + radius * np.sin(theta)
        plt.plot(x, y)

    # Noktaları çiz
    for p in noktalar:
        plt.plot(p[0], p[1], 'ro')  # 'ro' kırmızı nokta anlamına gelir

    # Kesişim noktalarını çiz
    for yeni in yeni_wp_kartezyen:
        plt.plot(yeni[0], yeni[1], 'go')  # 'go' yeşil nokta anlamına gelir
    # Eksen isimleri
    plt.xlabel('X ekseni')
    plt.ylabel('Y ekseni')

    # Başlık
    plt.title('Kartezyen Koordinat Sistemi Üzerinde Çemberler, Noktalar ve Dörtgen')

    # Izgara
    plt.grid(color='grey', linestyle='--', linewidth=0.5)

    # Eşit oranlı eksenler
    plt.gca().set_aspect('equal', adjustable='box')

    # Göster
    plt.show()

except KeyboardInterrupt:
    print("Programdan çıkıldı")