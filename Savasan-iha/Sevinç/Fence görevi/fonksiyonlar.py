import vincenty
import numpy as np
import sympy as sp
from sympy import Eq, symbols, solve
import matplotlib.pyplot as plt

home_konumu = (40.2306557, 29.0010148)

def wp_nokta_okuma(dosya_adi):
    with open(dosya_adi, 'r') as dosya:
        # Dosyadan her satırı oku
        satirlar = dosya.readlines()

    # Verileri saklamak için bir sözlük oluştur
    veri_sozlugu = {}
    # 1. satırı ve 2. satırı sil
    satirlar.pop(0)
    satirlar.pop(0)
    noktalar = []
    # Her satırı döngüye alın
    for satir in satirlar:
        # Satırı tab karakterine göre ayırın
        degerler = satir.strip().split('\t')
        # 9. ve 10. değerleri enlem ve boylam olarak alın
        enlem = float(degerler[8])
        boylam = float(degerler[9])
        # Noktalar listesine bir tuple olarak ekleyin
        noktalar.append((enlem, boylam))
    return noktalar


def fencenokta_okuma(dosya_adi):
    with open(dosya_adi, 'r') as dosya:
        # Dosyadan her satırı oku
        satirlar = dosya.readlines()

    # Verileri saklamak için bir sözlük oluştur
    veri_sozlugu = {}
    # 1. satırı ve 2. satırı sil
    satirlar.pop(0)
    satirlar.pop(0)
    noktalar = []
    # Her satırı döngüye alın
    for satir in satirlar:
        # Satırı tab karakterine göre ayırın
        degerler = satir.strip().split('\t')
        # 9. ve 10. değerleri enlem ve boylam olarak alın
        enlem = float(degerler[8])
        boylam = float(degerler[9])
        radius = float(degerler[4])
        # Noktalar listesine bir tuple olarak ekleyin
        noktalar.append((enlem, boylam, radius))
    return noktalar


def wp_konum_hesapla(target_locations):
    wp_kartezyen = []
    for i in target_locations:
        y_ussu = (i[0], home_konumu[1])
        x_ussu = (home_konumu[0], i[1])

        y_mesafe = vincenty.vincenty(y_ussu, home_konumu)
        x_mesafe = vincenty.vincenty(x_ussu, home_konumu)
        # x i negatif yapmak için  boylamının home boylamından küçük olması gerekir
        if i[1] < home_konumu[1]:
            x_mesafe = x_mesafe * -1000
        else:
            x_mesafe = x_mesafe * 1000
        # y i negatif yapmak için enlemi home enleminin altında olması gerekir
        if i[0] < home_konumu[0]:
            y_mesafe = y_mesafe * -1000
        else:
            y_mesafe = y_mesafe * 1000
        nokta = (x_mesafe, y_mesafe)
        wp_kartezyen.append(nokta)
    return wp_kartezyen


def fence_konum_hesapla(fence_konumları):
    fence_kartezyen = []
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
    return cember_denklemi


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

    return d <= r


def yeni_nokta_olusturma(nokta1, nokta2, cember):
    h, k, r = cember  # Çemberin merkezi (h, k) ve yarıçapı r
    dx, dy = nokta2[0] - nokta1[0], nokta2[1] - nokta1[1]  # İki nokta arasındaki fark
    mesafe = np.sqrt(dx ** 2 + dy ** 2)  # İki nokta arasındaki mesafe
    egim = dy / dx  # İki nokta arasındaki eğim
    normal_egim = -1 / egim  # Dik doğrunun eğimi

    # Çemberin merkezinden geçen ve iki noktayı birleştiren doğruya dik olan doğrunun denklemi
    # y - k = normal_egim * (x - h)
    # Bu doğru üzerinde, çemberin yarıçapından daha uzakta bir nokta belirleyelim
    # Bu nokta, çemberin dışına çıkacak ve çemberi dolaşacak bir yol belirlememizi sağlar
    # Örneğin, çemberin yarıçapının 1.5 katı uzaklıkta bir nokta seçelim
    uzaklik = r * 1.5
    yeni_x = h + uzaklik / np.sqrt(1 + normal_egim ** 2)
    yeni_y = k + normal_egim * (yeni_x - h)

    return (yeni_x, yeni_y)


def yeni_nokta_olusturma2(nokta1, nokta2, cember):
    h, k, r = cember  # Çemberin merkezi (h, k) ve yarıçapı r
    dx, dy = nokta2[0] - nokta1[0], nokta2[1] - nokta1[1]  # İki nokta arasındaki fark
    mesafe = np.sqrt(dx ** 2 + dy ** 2)  # İki nokta arasındaki mesafe
    egim = dy / dx  # İki nokta arasındaki eğim
    normal_egim = -1 / egim  # Dik doğrunun eğimi

    # Çemberin merkezinden geçen ve iki noktayı birleştiren doğruya dik olan doğrunun denklemi
    # y - k = normal_egim * (x - h)
    # Bu doğru üzerinde, çemberin yarıçapından daha uzakta bir nokta belirleyelim
    # Bu nokta, çemberin dışına çıkacak ve çemberi dolaşacak bir yol belirlememizi sağlar
    # Örneğin, çemberin yarıçapının 1.5 katı uzaklıkta bir nokta seçelim
    uzaklik = r * 1.5
    yeni_x = h + uzaklik / np.sqrt(1 + normal_egim ** 2)
    yeni_y = k + normal_egim * (yeni_x - h)

    # 180 derece kaydırılmış nokta için, mevcut noktanın tam tersi yönde olmalı
    # Bu, mevcut noktadan çemberin merkezine olan vektörü alıp ters çevirerek yapılabilir
    kaydirilmis_x = h - (yeni_x - h)
    kaydirilmis_y = k - (yeni_y - k)

    return (kaydirilmis_x, kaydirilmis_y)


def kartezyen_to_enlem_boylam(nokta, home_konumu):
    x_mesafe, y_mesafe = nokta
    # Enlem ve boylamı hesapla
    enlem = home_konumu[0] + y_mesafe / 111000  # 1 enlem derecesi yaklaşık 111 km'ye denk gelir
    boylam = home_konumu[1] + x_mesafe / (111000 * np.cos(np.radians(home_konumu[0])))
    nokta_yeni = (enlem, boylam)
    return nokta_yeni


def WPnoktaları_dosyaya_yaz(noktalar, dosya_adi):
    with open(dosya_adi, 'w') as dosya:
        #
        dosya.write("QGC WPL 110\n")
        # İlk noktayı yaz (genellikle home point olarak kullanılır)
        dosya.write("0\t1\t0\t16\t0\t0\t0\t0\t40.2320505\t29.0042872\t100.220000\t1\n")
        # Her bir noktayı dosyaya yazdır
        for i, (enlem, boylam) in enumerate(noktalar, start=1):
            # Enlem ve    boylamı noktadan sonra sadece 8 hanesini alacak şekilde yazdır
            dosya.write(f"{i}\t0\t3\t16\t0.00000000\t0.00000000\t0.00000000\t0.00000000\t{enlem:.8f}\t{boylam:.8f}\t100.000000\t1\n")
    # Dosyayı kapat
    dosya.close()
    dosya_ici = open(dosya_adi, 'r')
    print(dosya_ici.read())
    return



def ciz(*args):
    """
    Verilen parametreleri çizer:
    - Eğer bir parametre liste ise ve içindeki elemanlar 3 elemanlıysa, çember çizer.
    - Eğer bir parametre liste ise ve içindeki elemanlar 2 elemanlıysa, noktaları çizer.
    - Eğer bir parametre liste değilse ve 2 elemanlıysa, tek bir nokta çizer.
    - Eğer bir parametre liste ise ve içinde 3 eleman varsa, sadece çember çizer.
    """
    plt.figure(figsize=(6, 6))

    for arg in args:
        if isinstance(arg, list):
            if all(len(item) == 3 for item in arg):
                # Çemberleri çiz
                for h, k, radius in arg:
                    theta = np.linspace(0, 2 * np.pi, 100)
                    x = h + radius * np.cos(theta)
                    y = k + radius * np.sin(theta)
                    plt.plot(x, y)
            elif all(len(item) == 2 for item in arg):
                # Noktaları çiz
                for x, y in arg:
                    plt.plot(x, y, 'ro')  # 'ro' kırmızı nokta anlamına gelir
        elif isinstance(arg, tuple) and len(arg) == 2:
            # Tek bir nokta çiz
            plt.plot(arg[0], arg[1], 'ro')  # 'ro' kırmızı nokta anlamına gelir
        elif isinstance(arg, tuple) and len(arg) == 3:
            # Sadece çember çiz
            h, k, radius = arg
            theta = np.linspace(0, 2 * np.pi, 100)
            x = h + radius * np.cos(theta)
            y = k + radius * np.sin(theta)
            plt.plot(x, y)

    # Eksen isimleri
    plt.xlabel('X ekseni')
    plt.ylabel('Y ekseni')

    # Başlık
    plt.title('Kartezyen Koordinat Sistemi Üzerinde Çemberler ve Noktalar')

    # Izgara
    plt.grid(color='grey', linestyle='--', linewidth=0.5)

    # Eşit oranlı eksenler
    plt.gca().set_aspect('equal', adjustable='box')

    # Göster
    plt.show()

def nokta_silme(nokta,noktalar):
    #noktalar içindeki noktayı sil
    noktalar.remove(nokta)
    return


def nokta_cember_icinde_mi(nokta, cember):
    h, k, r = cember  # Çemberin merkezi (h, k) ve yarıçapı r
    x, y = nokta  # Kontrol edilecek nokta (x, y)

    # Noktanın çemberin merkezine olan uzaklığı
    uzaklik = np.sqrt((x - h) ** 2 + (y - k) ** 2)

    # Uzaklık yarıçaptan küçükse nokta çemberin içindedir
    return uzaklik < r

