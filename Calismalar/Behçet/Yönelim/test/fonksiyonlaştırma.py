import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import vincenty



def konum_hesaplama(konum,v,roll,yaw0):
    g= 9.81
    referans_konum=(37.7348492,29.0947473)

    def kartezyen_to_enlem_boylam(nokta, home_konumu):
        x_mesafe, y_mesafe = nokta
        # Enlem ve boylamı hesapla
        enlem = home_konumu[0] + y_mesafe / 111000  # 1 enlem derecesi yaklaşık 111 km'ye denk gelir
        boylam = home_konumu[1] + x_mesafe / (111000 * np.cos(np.radians(home_konumu[0])))
        nokta_yeni = (enlem, boylam)
        return nokta_yeni
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
        nokta = (x_mesafe, y_mesafe, i[2])

        return nokta
    def noktayı_döndür(konum, açı):
        x, y = konum[0], konum[1]
        # Açıyı radyan cinsine çevir
        θ = np.deg2rad(açı)

        # Yeni koordinatları hesapla
        x_prime = x * np.cos(θ) - y * np.sin(θ)
        y_prime = x * np.sin(θ) + y * np.cos(θ)

        return x_prime, y_prime




    def dönüş_yarıçapı(v, roll):
        g = 9.81
        return (v ** 2) / (g * np.tan(roll))


    def yaw_değişimi(v, r, roll, dt):
        return v * np.tan(roll) / r * dt


    def dairesel_hareket(konum, roll, v, dt):
        yaw = konum[2]
        roll = np.deg2rad(roll)

        x, y = konum[0], konum[1]
        r = dönüş_yarıçapı(v, roll)
        yaw_degisim = yaw_değişimi(v, r, roll, dt)


        if roll < 0:
            yaw -= yaw_degisim
        else:
            yaw += yaw_degisim


        x += v * np.sin(yaw) * dt
        y += v * np.cos(yaw) * dt

        return x, y, yaw


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



    konum=nokta_hesapla(konum)
    #şimdi konum ne olursa olsun öncelikle konum değerindeki yaw değerini 0 olarak almamız gerekecek
    konumlar=[]
    konum=(konum[0],konum[1],0)
    konumlar.append(konum)



    for i in range(10):

        x,y,yaw=dairesel_hareket(konum,60,20,0.1)
        konum=(x,y,yaw)
        konumlar.append((konum[0],konum[1],yaw))
        print(konum)

    son_konum=konumlar[-1]
    son=noktayı_döndür(son_konum,-yaw0)
    print(son)
    son=kartezyen_to_enlem_boylam(son, referans_konum)
    print(son)

    return son
konum=(37.7348492,29.0947473,270)
son=konum_hesaplama(konum,0.1,20,270)