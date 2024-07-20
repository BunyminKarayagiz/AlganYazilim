import vincenty
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from sympy import Eq
import math
import json
import ana_sunucu_islemleri

home_konumu = (40.2287349, 28.9975977)
x=20#bu uzaklık bizim yeni oluşturulan noktamının çemberden kaç merte uzakla oluşturulmasını belirleyecektir
ucus_alanı=[(40.2336863,29.0000814),(40.2338296,29.0095121),(40.2291281,29.0093994),(40.230709,29.001857),(40.2321751,29.0007842)]



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
        #  eğer 4. sütundaki değer 16 ise 9. ve 10. değerleri enlem ve boylam olarak alın
        if degerler[3] == '16':
            enlem = float(degerler[8])
            boylam = float(degerler[9])
            noktalar.append((enlem, boylam))
    return noktalar


def fence_dosya_kaydetme(fence_konumları,ucus_alanı, dosya_adi):

    ucus_alanı_miktarı = len(ucus_alanı)
    fence_konumları_miktarı = len(fence_konumları)

    with open(dosya_adi, 'w') as dosya:
        dosya.truncate(0)
        dosya.write("QGC WPL 110\n")
        dosya.write("0\t1\t0\t16\t0\t0\t0\t0\t40.2320505\t29.0042872\t100.220000\t1\n")
        for i, konum in enumerate(ucus_alanı, start=1):
            dosya.write(
                f"{i}\t0\t0\t5001\t5.00000000\t0.00000000\t0.00000000\t0.00000000\t{konum[0]}\t{konum[1]}\t100.000000\t1\n")
        for j, konum in enumerate(fence_konumları, start=ucus_alanı_miktarı + 1):
            dosya.write(
                f"{j}\t0\t0\t5004\t{float(konum[2]):.8f}\t0.00000000\t0.00000000\t0.00000000\t{konum[0]}\t{konum[1]}\t100.000000\t1\n")


def fencenokta_okuma(dosya_adi):
    with open(dosya_adi, 'r') as dosya:
        ucus_alanları = []
        noktalar = []
        # Dosyadan her satırı oku
        satirlar = dosya.readlines()

    # Verileri saklamak için bir sözlük oluştur
    veri_sozlugu = {}
    # 1. satırı ve 2. satırı sil
    satirlar.pop(0)
    satirlar.pop(0)

    # Her satırı döngüye alın
    for satir in satirlar:
        # Satırı tab karakterine göre ayırın
        degerler = satir.strip().split('\t')
        # 9. ve 10. değerleri enlem ve boylam olarak alın
        enlem = float(degerler[8])
        boylam = float(degerler[9])
        radius = float(degerler[4])
        if degerler[3]=='5004':
            noktalar.append((enlem, boylam, radius))
        elif degerler[3]=='5001':
            ucus_alanları.append((enlem, boylam))

    return noktalar


def wp_konum_hesapla(target_locations,ucusalani):
    wp_kartezyen = []
    ucus_alani=[]
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
    for i in ucusalani:
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
        ucus_alani.append(nokta)

    return wp_kartezyen,ucus_alani



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




#bu fonksiyon kesişim hesaplama işlemini enklem oluşturarak gerçekleştiriyor.
"""
def kesisim_kontrol(nokta1,nokta2,fence):
    def cember_denklemi(cember):
        a, b, radius = cember
        r = radius
        # çember denklemi (x-a)^2 + (y-b)^2 = r^2
        x, y = sp.symbols('x y')
        cember_denklemi = Eq((x - a) ** 2 + (y - b) ** 2, r ** 2)
        return cember_denklemi

    def dogru_denklemi_olustur(nokta1, nokta2):
        x2, y2 = nokta2
        x1, y1 = nokta1
        # print("x1:",x1,"y1:",y1)
        # print("x2:",x2,"y2:",y2)
        if x2 - x1 == 0:
            # x1 ve x2 aynı olduğunda, dikey bir doğru söz konusudur.
            # Bu durumda, 'x' sabit bir değer alır ve 'y' herhangi bir değer alabilir.
            x_katsayı = 0
            sabit = x1
            x, y = sp.symbols('x y')
            # Dikey doğru denklemi: x = sabit
            dogru_denklemi = Eq(x, sabit)
        else:
            # x1 ve x2 farklı olduğunda, normal bir doğru denklemi oluşturulur.
            m = (y2 - y1) / (x2 - x1)
            x_katsayı = m
            sabit = -m * x1 + y1
            x, y = sp.symbols('x y')
            # Yatay olmayan doğru denklemi: y = mx + b
            dogru_denklemi = Eq(y, x_katsayı * x + sabit)
        return dogru_denklemi

    dogru_denklemi=dogru_denklemi_olustur(nokta1,nokta2)
    cember_denklemi=cember_denklemi(fence)

    x, y = sp.symbols('x y')
    # Doğru ve çember denklemlerini çöz
    kesisim_noktaları = sp.solve((dogru_denklemi, cember_denklemi), (x, y))

    def filter_real_points(points):
        real_points = []
        for point in points:
            if all(coord.is_real for coord in point):
                point=[i/100 for i in point]
                #bu noktanın nokta 1 vwe nokta 2 arasında olup olmadığını kontrol et
                if (nokta1[0]<=point[0]<=nokta2[0] and nokta1[1]<=point[1]<=nokta2[1]) or (nokta1[0]>=point[0]>=nokta2[0] and nokta1[1]>=point[1]>=nokta2[1]):
                    real_points.append(point)
        return real_points

    kesisim_noktaları = filter_real_points(kesisim_noktaları)
    return kesisim_noktaları
"""
#bu fonksiyon kesişim hesaplama işlemini çemberin merkezine indirilen dikmenin doğrunun üzerinde olup olmadıını tespit ederek belirliyor.
def kesisim_kontrol(nokta1, nokta2, fence):
    cember_konumu = (fence[0], fence[1])
    cember_yaricapi = fence[2]

    def kesisim_noktası(nokta1, nokta2, merkez):
        # Nokta 1 ve Nokta 2'nin koordinatları
        x1, y1 = nokta1
        x2, y2 = nokta2
        xc, yc = merkez

        # Doğrunun eğimi
        if x2 - x1 != 0 and y2 - y1 != 0:
                m = (y2 - y1) / (x2 - x1)
        else:
            # Doğru dikeyse eğim sonsuz olur
            m = sp.oo

        # Doğrunun y-kesim noktası
        b = y1 - m * x1

        # Dikmenin eğimi
        if m != sp.oo or m != 0:
            perpendicular_slope = -1 / m
        else:
            # Doğru dikeyse, dikme yatay olur
            perpendicular_slope = 0

        # Dikmenin denklemi: y = perpendicular_slope * x + c
        c = yc - perpendicular_slope * xc

        # Doğru ve dikmenin kesişim noktasını bulmak için denklemleri eşitleriz
        x, y = sp.symbols('x y')
        if m != sp.oo:
            line_eq = sp.Eq(y, m * x + b)
        else:
            line_eq = sp.Eq(x, x1)

        if perpendicular_slope != 0:
            perpendicular_eq = sp.Eq(y, perpendicular_slope * x + c)
        else:
            perpendicular_eq = sp.Eq(y, yc)

        # Denklemleri çözeriz
        intersection = sp.solve((line_eq, perpendicular_eq), (x, y))

        return (float(intersection[x]), float(intersection[y]))

    def sinir_kontrol(intersection, point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        x, y = intersection

        # x ve y değerlerinin sınırlar içinde olup olmadığını kontrol ederiz
        within_x_bounds = min(x1, x2) <= x <= max(x1, x2)
        within_y_bounds = min(y1, y2) <= y <= max(y1, y2)

        return within_x_bounds and within_y_bounds

    def nokta_nokta(nokta1, nokta2): # iki nokta arasındaki mesafeyi hesaplar
        x_uzaklık = abs(nokta1[0] - nokta2[0])
        y_uzaklık = abs(nokta1[1] - nokta2[1])
        mesafe = math.sqrt(x_uzaklık**2 + y_uzaklık**2)
        return mesafe

    kesisim_noktası = kesisim_noktası(nokta1, nokta2, cember_konumu)
    mesafe = nokta_nokta(cember_konumu, kesisim_noktası)

    if sinir_kontrol(kesisim_noktası, nokta1, nokta2):
        if mesafe <= cember_yaricapi:
            return True
    return False




def yeni_nokta_olusturma(nokta1, nokta2, cember):


    if nokta1[1]>nokta2[1]:
        boşluk=nokta1
        nokta1=nokta2
        nokta2=boşluk



    h, k, r = cember  # Çemberin merkezi (h, k) ve yarıçapı r
    dx, dy = nokta2[0] - nokta1[0], nokta2[1] - nokta1[1]  # İki nokta arasındaki fark

    # İki nokta arasındaki mesafe
    mesafe = np.sqrt(dx ** 2 + dy ** 2)

    # Eğer dx sıfırsa, dikey bir doğru var demektir.
    if dx == 0:
        # Dikey doğru için yeni noktaları hesaplayın.
        yeni_x = nokta1[0]  # x koordinatı sabit kalır.
        # y koordinatları için çemberin üst ve altında iki nokta seçin.
        yeni_y1 = k + r
        yeni_y2 = k - r
        # İki nokta arasındaki mesafeye göre uygun olanı seçin.
        if abs(nokta1[1] - yeni_y1) < abs(nokta1[1] - yeni_y2):
            return (yeni_x, yeni_y1)
        else:
            return (yeni_x, yeni_y2)
    else:
        # Eğimi hesaplayın
        egim = dy / dx
        # Dik doğrunun eğimi
        normal_egim = -1 / egim

        uzaklik = r+x
        yeni_x = h + uzaklik / np.sqrt(1 + normal_egim ** 2)
        yeni_y = k + normal_egim * (yeni_x - h)

        return (yeni_x, yeni_y)


def yeni_nokta_olusturma2(nokta1, nokta2, cember):

    if nokta1[1]>nokta2[1]:
        boşluk=nokta1
        nokta1=nokta2
        nokta2=boşluk


    h, k, r = cember  # Çemberin merkezi (h, k) ve yarıçapı r
    dx, dy = nokta2[0] - nokta1[0], nokta2[1] - nokta1[1]  # İki nokta arasındaki fark

    # İki nokta arasındaki mesafe
    mesafe = np.sqrt(dx ** 2 + dy ** 2)

    # Eğer dx sıfırsa, dikey bir doğru var demektir.
    if dx == 0:
        # Dikey doğru için yeni noktaları hesaplayın.
        yeni_x = nokta1[0]  # x koordinatı sabit kalır.
        # y koordinatları için çemberin üst ve altında iki nokta seçin.
        yeni_y1 = k + r
        yeni_y2 = k - r
        # İki nokta arasındaki mesafeye göre uygun olanı seçin.
        if abs(nokta1[1] - yeni_y1) < abs(nokta1[1] - yeni_y2):
            return (yeni_x, yeni_y1)
        else:
            return (yeni_x, yeni_y2)
    else:
        # Eğimi hesaplayın
        egim = dy / dx
        # Dik doğrunun eğimi
        normal_egim = -1 / egim
        uzaklik = r * 1.5
        yeni_x = h + uzaklik / np.sqrt(1 + normal_egim ** 2)
        yeni_y = k + normal_egim * (yeni_x - h)

        kaydirilmis_x = h - (yeni_x - h)
        kaydirilmis_y = k - (yeni_y - k)

        return (kaydirilmis_x, kaydirilmis_y)
def yeni_nokta_olusturma_aci(nokta1, nokta2, cember, aci=0):
    h, k, r = cember  # Çemberin merkezi (h, k) ve yarıçapı r
    dx, dy = nokta2[0] - nokta1[0], nokta2[1] - nokta1[1]  # İki nokta arasındaki fark
    mesafe = np.sqrt(dx ** 2 + dy ** 2)  # İki nokta arasındaki mesafe
    egim = dy / dx  # İki nokta arasındaki eğim
    normal_egim = -1 / egim  # Dik doğrunun eğimi

    # Çemberin merkezinden geçen ve iki noktayı birleştiren doğruya dik olan doğrunun denklemi
    # y - k = normal_egim * (x - h)
    # Bu doğru üzerinde, çemberin yarıçapından daha uzakta bir nokta belirleyelim
    uzaklik = r * 1 +x
    temel_x = h + uzaklik / np.sqrt(1 + normal_egim ** 2)
    temel_y = k + normal_egim * (temel_x - h)

    # Açıyı radyana çevir
    aci_radyan = np.radians(aci)
    # Cosinus ve sinus değerlerini hesapla
    cos_degeri = np.cos(aci_radyan)
    sin_degeri = np.sin(aci_radyan)

    # Yeni noktayı hesapla
    yeni_x = h + (temel_x - h) * cos_degeri - (temel_y - k) * sin_degeri
    yeni_y = k + (temel_x - h) * sin_degeri + (temel_y - k) * cos_degeri

    return (yeni_x, yeni_y)

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
        dosya.write(f"{len(noktalar)+1}\t0\t3\t177\t1.00000000\t500.00000000\t0.00000000\t0.00000000\t0.00000000\t0.00000000\t0.00000000\t1\n") # du jump komutu ekler
    # Dosyayı kapat
    dosya.close()
    dosya_ici = open(dosya_adi, 'r')
    return


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
    #grafiğin altında açıklama yap renkleri ve neyi gösterdiğini açıkla
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


def nokta_cember_icinde_mi(nokta, cember):
    try:
        h, k, r = cember  # Çemberin merkezi (h, k) ve yarıçapı r
    except ValueError as e:
        print(f"Hata: {e}. cember değişkeninin değeri: {cember}")
        return False

    x, y = nokta  # Kontrol edilecek nokta (x, y)

    # Noktanın çemberin merkezine olan uzaklığı
    uzaklik = np.sqrt((x - h) ** 2 + (y - k) ** 2)

    # Uzaklık yarıçaptan küçükse nokta çemberin içindedir
    return uzaklik < r

def nokta_alanın_içinde_mi(nokta, vertices):
    x, y = nokta
    n = len(vertices)
    inside = False

    p1x, p1y = vertices[0]
    for i in range(n + 1):
        p2x, p2y = vertices[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside
def aci_hesapla(önceki_nokta,wp,sonraki_nokta):

    # Noktaların koordinatlarını girin (örnek: A(x1, y1), B(x2, y2), C(x3, y3))
    x1, y1 = önceki_nokta  # A noktası
    x2, y2 = wp  # B noktası
    x3, y3 = sonraki_nokta  # C noktası

    # Vektörleri hesaplayın
    vektor_AB = (x2 - x1, y2 - y1)
    vektor_AC = (x3 - x2, y3 - y2)

    # İç çarpımı ve vektör uzunluklarını hesaplayın
    ic_carpim = vektor_AB[0] * vektor_AC[0] + vektor_AB[1] * vektor_AC[1]
    uzunluk_AB = math.sqrt(vektor_AB[0] ** 2 + vektor_AB[1] ** 2)
    uzunluk_AC = math.sqrt(vektor_AC[0] ** 2 + vektor_AC[1] ** 2)

    # Açıyı hesaplayın (radyan cinsinden)
    aci_radyan = math.acos(ic_carpim / (uzunluk_AB * uzunluk_AC))

    # Açıyı derece cinsinden dönüştürün
    aci_derece = math.degrees(aci_radyan)
    return aci_derece




def nokta_nokta(nokta1,nokta2): #iki nokta arasındaki mesafeyi hesaplar
    x_uzaklık=abs(nokta1[0]-nokta2[0])
    y_uzaklık=abs(nokta1[1]-nokta2[1])
    mesafe=math.sqrt(x_uzaklık**2+y_uzaklık**2)
    return mesafe



def nokta_gecerli_mi(nokta, fence_kartezyen, ucus_alanı_kartezyen):
    for cember in fence_kartezyen:
        if nokta_cember_icinde_mi(nokta, cember):
            return False
        if nokta_alanın_içinde_mi(nokta, ucus_alanı_kartezyen) == False:
            return False
    return True
def aci_hesaplama(a, b, c):
    vektor_a = (a[0] - b[0], a[1] - b[1])
    vektor_b = (c[0] - b[0], c[1] - b[1])

    # İki vektörün iç çarpımını hesapla
    ic_carpim = vektor_a[0] * vektor_b[0] + vektor_a[1] * vektor_b[1]

    # Vektörlerin uzunluklarını hesapla
    uzunluk_a = math.sqrt(vektor_a[0] ** 2 + vektor_a[1] ** 2)
    uzunluk_b = math.sqrt(vektor_b[0] ** 2 + vektor_b[1] ** 2)

    # İki vektör arasındaki açıyı hesapla
    if uzunluk_a * uzunluk_b == 0:
        return "Vektör uzunlukları sıfır olamaz."

    cos_theta = ic_carpim / (uzunluk_a * uzunluk_b)
    theta = math.degrees(math.acos(cos_theta))

    return theta


def genislet_ve_yakinlastir(onceki_nokta, orta_nokta, sonraki_nokta, genisletme_miktari):
    """
    Önceki, orta ve sonraki noktalar arasındaki açıyı genişletir ve noktaları yakınlaştırır.

    Args:
        onceki_nokta (tuple): Önceki noktanın koordinatları (x1, y1).
        orta_nokta (tuple): Orta noktanın koordinatları (x2, y2).
        sonraki_nokta (tuple): Sonraki noktanın koordinatları (x3, y3).
        genisletme_miktari (float): Açıyı genişletmek için kullanılacak faktör (örneğin 0.9).

    Returns:
        tuple: Yeni orta noktanın koordinatları.
    """
    # İki vektörü hesapla
    vektor_A = (sonraki_nokta[0] - orta_nokta[0], sonraki_nokta[1] - orta_nokta[1])
    vektor_B = (orta_nokta[0] - onceki_nokta[0], orta_nokta[1] - onceki_nokta[1])

    # İki vektörün iç çarpımını hesapla
    dot_product = vektor_A[0] * vektor_B[0] + vektor_A[1] * vektor_B[1]

    # Vektörlerin uzunluklarını hesapla
    uzunluk_A = math.sqrt(vektor_A[0] ** 2 + vektor_A[1] ** 2)
    uzunluk_B = math.sqrt(vektor_B[0] ** 2 + vektor_B[1] ** 2)

    # Ensure no division by zero
    if uzunluk_A == 0 or uzunluk_B == 0:
        raise ValueError("One of the vectors has zero length")

    # Açıyı hesapla (radyan cinsinden)
    cos_aci = dot_product / (uzunluk_A * uzunluk_B)

    # Clamp the value to be within the range [-1, 1]
    cos_aci = max(-1.0, min(1.0, cos_aci))

    aci_radyan = math.acos(cos_aci)

    # Açıyı genişlet
    yeni_aci_radyan = aci_radyan * genisletme_miktari

    # Yeni orta noktanın yönünü hesapla
    genisletme_vektoru = (
        orta_nokta[0] - onceki_nokta[0],
        orta_nokta[1] - onceki_nokta[1]
    )

    uzunluk_genisletme = math.sqrt(genisletme_vektoru[0] ** 2 + genisletme_vektoru[1] ** 2)

    if uzunluk_genisletme == 0:
        raise ValueError("Expansion vector has zero length")

    yeni_orta_x = onceki_nokta[0] + uzunluk_genisletme * math.cos(yeni_aci_radyan)
    yeni_orta_y = onceki_nokta[1] + uzunluk_genisletme * math.sin(yeni_aci_radyan)

    return (yeni_orta_x, yeni_orta_y)
def connect_to_anasunucu():
    api = ana_sunucu_islemleri.sunucuApi("http://127.0.0.1:5000")
    "Burada durum kodu işlemin başarı kodunu vermektedir örn:200"
    ana_sunucuya_giris_durumu = False
    ana_sunucuya_giris_kodu, durum_kodu = api.sunucuya_giris(
        str("algan"),
        str("53SnwjQ2sQ"))
    try:
        if int(durum_kodu) == 200:
            print(f"\x1b[{31}m{'Ana Sunucuya Bağlanıldı: ' + durum_kodu}\x1b[0m")  # Ana sunucya girerkenki durum kodu.
            ana_sunucuya_giris_durumu = True
    except ValueError:
        print(f"\x1b[{31}m{'Ana Sunucuya Bağlanılamadı: ' + durum_kodu}\x1b[0m")

    return ana_sunucuya_giris_durumu
def hss_coordinat():
    api = ana_sunucu_islemleri.sunucuApi("http://127.0.0.1:5000")
    status_code, coordinat_text = api.get_hava_savunma_coord()
    coordinat_text = json.loads(coordinat_text)
    return coordinat_text


def elemandan_sonrasina_ekle(liste, hedef_eleman, yeni_eleman):

    # Hedef elemanın indeksini bulma
    index = liste.index(hedef_eleman)

    # Yeni elemanı hedef elemandan sonra ekleme
    liste.insert(index + 1, yeni_eleman)
def orta_nokta(nokta1,nokta2):
    x1,y1=nokta1
    x2,y2=nokta2
    orta_nokta_x=(x1+x2)/2
    orta_nokta_y=(y1+y2)/2
    return (orta_nokta_x,orta_nokta_y)


def calculate_turn_angle(nokta1,nokta2,nokta3):
    # Vektörleri oluştur
    x1,y1=nokta1
    x2,y2=nokta2
    x3,y3=nokta3
    v1_x, v1_y = x1 - x2, y1 - y2
    v2_x, v2_y = x3 - x2, y3 - y2

    # Skaler çarpım
    dot_product = v1_x * v2_x + v1_y * v2_y

    # Vektörlerin büyüklükleri
    magnitude_v1 = math.sqrt(v1_x ** 2 + v1_y ** 2)
    magnitude_v2 = math.sqrt(v2_x ** 2 + v2_y ** 2)

    # Kosinüs teoremi
    cos_theta = dot_product / (magnitude_v1 * magnitude_v2)

    # Açı (radyan cinsinden)
    theta_radians = math.acos(cos_theta)

    # Açı (derece cinsinden)
    theta_degrees = math.degrees(theta_radians)

    return theta_degrees
