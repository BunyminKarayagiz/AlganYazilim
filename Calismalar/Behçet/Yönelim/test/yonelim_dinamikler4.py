import matplotlib.pyplot as plt
import numpy as np

def ciz(cizim_listesi):
    """
    Verilen cizim_listesi'ndeki her bir öğeyi, belirtilen renkte çizer:
    - Her öğe, çizilecek şekillerin listesi ve renk bilgisini içeren bir tuple olmalıdır.
    """
    plt.figure(figsize=(6, 6))

    for cizilecekler, renk in cizim_listesi:
        renk_kodlari = {'kirmizi': 'r', 'yeşil': 'g', 'mavi': 'b'}
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

cizim_listesi = [
([(0, 0, 1)], 'kirmizi'),           # Çember
([(1, 1)], 'yeşil'),                # Nokta
([(2, 2), (3, 3)], 'mavi'),         # İki nokta
]

ciz(cizim_listesi)