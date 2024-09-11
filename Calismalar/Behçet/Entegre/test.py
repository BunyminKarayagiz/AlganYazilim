import numpy as np
import matplotlib.pyplot as plt
import math
import vincenty
import itertools


x=0
referans_konum = (40.2301684,28.9983702)




def çember_oluştur(roll,hız,nokta1,nokta2):
    def hesapla_yaricap(hiz, roll_acisi):
        g = 9.81  # Yerçekimi ivmesi (m/s²)
        # Roll açısını radiana çevir
        roll_radyan = math.radians(roll)
        # Yarıçapı hesapla
        yaricap = hiz**2 / (g * math.tan(roll_radyan))
        return yaricap

    def nokta_uzaklikta_dondur(nokta1, nokta2, mesafe):
        """Nokta1'den Nokta2'ye çizilen çizgi üzerinde, Nokta1'den belirtilen mesafede olan noktayı
        bulur ve bu noktayı döndürür."""

        # İki nokta arasındaki mesafeyi hesapla
        dx = nokta2[0] - nokta1[0]
        dy = nokta2[1] - nokta1[1]
        uzunluk = np.sqrt(dx ** 2 + dy ** 2)

        # Belirtilen mesafede bir nokta bulmak için orantılama yap
        t = mesafe / uzunluk
        x_uzaklikta = nokta1[0] + t * dx
        y_uzaklikta = nokta1[1] + t * dy

        return (x_uzaklikta, y_uzaklikta)
    yaricap=hesapla_yaricap(hız,roll)
    return nokta_uzaklikta_dondur(nokta1,nokta2,yaricap),yaricap

def cember_kesisim_check(cember1, cember2):
    """
    İki çemberin kesişip kesişmediğini kontrol eder.
    cember1 ve cember2: (merkez_x, merkez_y, yarıçap)
    """
    # Çemberlerin merkezlerini ve yarıçaplarını çıkar
    h1, k1, r1 = cember1
    h2, k2, r2 = cember2

    # Merkezler arasındaki mesafeyi hesapla
    merkezler_arasi_mesafe = math.sqrt((h2 - h1) ** 2 + (k2 - k1) ** 2)

    # Çemberlerin kesişim durumunu kontrol et
    if merkezler_arasi_mesafe > r1 + r2:
        return False  # Çemberler arasında çok uzak
    elif merkezler_arasi_mesafe < abs(r1 - r2):
        return False  # Bir çember diğerinin içinde, ancak kesişmiyor
    elif merkezler_arasi_mesafe == 0 and r1 == r2:
        return True   # Çemberler tamamen üst üste
    else:
        return True   # Çemberler kesişir

def ciz(cizim_listesi):
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
def nokta_nokta(nokta1, nokta2):  # iki nokta arasındaki mesafeyi hesaplar
    x_uzaklık = abs(nokta1[0] - nokta2[0])
    y_uzaklık = abs(nokta1[1] - nokta2[1])
    mesafe = math.sqrt(x_uzaklık ** 2 + y_uzaklık ** 2)
    return mesafe
def hss_uzaklık_hesaplama(HSS_merkez, nokta, yarıçap):
    #hss yarıçapı alınır noktanın noktaya olan uzaklığı formülünden yarıçap değeri çıkartılır.
    def nokta_nokta(nokta1, nokta2):  # iki nokta arasındaki mesafeyi hesaplar
        x_uzaklık = abs(nokta1[0] - nokta2[0])
        y_uzaklık = abs(nokta1[1] - nokta2[1])
        mesafe = math.sqrt(x_uzaklık ** 2 + y_uzaklık ** 2)
        return mesafe
    mesafe= nokta_nokta(HSS_merkez, nokta)-yarıçap
    return mesafe

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


def aralarındaki_aciyi_hesapla(yaw0,yaw1):
    """bizim yaw=yaw0
    rakibin yawı=yaw1"""
    aci0=-yaw0
    aci1=-yaw1
    #rakiptan bizimkini çıkartınca açı farkını bulmuş oluyoruz.
    return aci1-aci0



def nokta_hesapla(konum):
    i = konum
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
    nokta = (x_mesafe, y_mesafe)
    return nokta


#sunucudan çekilen hss_koordinat_bilgilerİ
hss_koordinat_bilgileri= [{"id": 0,"hssEnlem": 40.23260922,"hssBoylam": 29.00573015,"hssYaricap": 50 },
                          { "id": 1,"hssEnlem": 40.23351019,"hssBoylam": 28.99976492,"hssYaricap": 50 },
                          {"id": 2,"hssEnlem": 40.23105297, "hssBoylam": 29.00744677, "hssYaricap": 75},
                          {"id": 3,"hssEnlem": 40.23090554,"hssBoylam": 29.00221109,"hssYaricap": 150}]
# Her bir HSS noktasıyla referans konum arasındaki x ve y uzaklıklarını hesapla
hss_referans_uzaklıkları = [
    {
        'id': hss['id'],  # HSS id bilgisi
        'x_uzaklık': abs(nokta_hesapla((hss['hssEnlem'], hss['hssBoylam']))[0] - nokta_hesapla(referans_konum)[0]),
        'y_uzaklık': abs(nokta_hesapla((hss['hssEnlem'], hss['hssBoylam']))[1] - nokta_hesapla(referans_konum)[1]),
        'yarıçap': hss['hssYaricap']  # Yarıçap bilgisi
    }
    for hss in hss_koordinat_bilgileri
]


# X ve Y uzaklıklarını ve yarıçapı yazdır
for hss in hss_referans_uzaklıkları:
    print(f"HSS Noktası {hss['id']}:")
    print(f"X Uzaklık: {hss['x_uzaklık']:.6f} derece, Y Uzaklık: {hss['y_uzaklık']:.6f} derece")
    print(f"Yarıçap: {hss['yarıçap']} metre\n")

#bu üsttekiler ilk başyta tek seferlik yapılacak adımlardır.
uzakliklar = [
    f"id{hss['id']}_uzaklık: {nokta_nokta((hss['x_uzaklık'], hss['y_uzaklık']), referans_konum):.2f}"
    for hss in hss_referans_uzaklıkları
]
print(uzakliklar)
#bu adıma kadar doğru çalışıyor
yaw0=90
yaw1=0
aci_farki=aralarındaki_aciyi_hesapla(yaw0,yaw1)
#açı farkı 90 dereceden küçükse
if abs(aci_farki)<90:
    #açı farkı pozitif ise - roll yapması gerek
    #açı farklı negatif ise + roll yapması gerek
    if aci_farki>0:
        yeni_nokta_olusturma_aci(nokta1,nokta2,cember,aci=0)
        #burada nokta1 değeri bizim x y cinsinden konumumuz nokta2 değeri rakibin xy cinsinden konumu
    if aci_farki>=90: # ve biz dönerken herhangi bir çemberi keseceksek bu hesaplanacak
        #bu durumda da aynı zamanda bu dönüş çemberi kesiyor mu diye bakarız
        konum,yarıçap=çember_oluştur(roll,hız,nokta1,nokta2)
        çember1=(konum[0],konum[1],yarıçap)
        çember2=HSS #kendisine en yakın olan hss bunu o mesafe döndüren listenin içindeki minimum değere sahip olan indise bakarak buluruz
        if cember_kesisim_check(çember1,çember2):
            #artık çemberin merkezine olan uzaklığımız kadar olan yarıçapta maksimum
            #roll açı değerimiz 45 derece olsun hızımızı belirleyelim
            #v=r*g*tan(roll) yapacağız
            #ve bu hareketi rakip olan uçakla aynı yaw değerine sahip olana kadar sürdüreceğiz.
            pass