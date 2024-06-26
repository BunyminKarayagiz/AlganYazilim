from fonksiyonlar import *
import folium
from IPython.display import display

try:
    target_locations = wp_nokta_okuma("waypoint.waypoints")
    fence_konumları, ucus_alanı = fencenokta_okuma("Fencewpoints.waypoints")
    wp_kartezyen, ucus_alanı_kartezyen = wp_konum_hesapla(target_locations, ucus_alanı)
    fence_kartezyen = fence_konum_hesapla(fence_konumları)
    kesisim = []
    yeni_wp_kartezyen = []
    eklenen_noktalar = set()  # Eklenen noktaları takip etmek için bir set oluşturuluyor.


    for wp in wp_kartezyen:
        try:
            sonraki_konum = wp_kartezyen[wp_kartezyen.index(wp) + 1]
        except IndexError:
            sonraki_konum = wp_kartezyen[0]

        for fence in fence_kartezyen:
            dogru = dogru_denklemi_olustur(wp[0], sonraki_konum[0], wp[1], sonraki_konum[1])
            cember = cember_denklemi(fence[0], fence[1], fence[2])
            kesisin_varmi = kesisim_kontrol(wp, sonraki_konum, fence)
            if nokta_cember_icinde_mi(wp, fence) == False and wp not in eklenen_noktalar:
                yeni_wp_kartezyen.append(wp)
                eklenen_noktalar.add(wp)  # Nokta eklenenler listesine ekleniyor.
            if kesisin_varmi == True:
                yeni_nokta1 = yeni_nokta_olusturma(wp, sonraki_konum, fence)
                yeni_nokta2 = yeni_nokta_olusturma2(wp, sonraki_konum, fence)
                yeni_nokta = yeni_nokta1
                for cember in fence_kartezyen:
                    if nokta_cember_icinde_mi(yeni_nokta1, cember) == True or nokta_alanın_içinde_mi(yeni_nokta1, ucus_alanı_kartezyen) == False:
                        yeni_nokta = yeni_nokta2
                if yeni_nokta not in eklenen_noktalar:
                    yeni_wp_kartezyen.append(yeni_nokta)
                    eklenen_noktalar.add(yeni_nokta)  # Yeni nokta eklenenler listesine ekleniyor.

    yeni_rota = []
    for nokta in yeni_wp_kartezyen:
        yeni_nokta = kartezyen_to_enlem_boylam(nokta, home_konumu)
        yeni_rota.append(yeni_nokta)
    WPnoktaları_dosyaya_yaz(yeni_rota, 'yeni_rota.waypoints')
    cizim_listesi = [(fence_kartezyen, 'kırmızı'), (yeni_wp_kartezyen, 'yeşil'), (ucus_alanı_kartezyen, 'mavi')]
    ciz(cizim_listesi)
except KeyboardInterrupt:
    print("Programdan çıkıldı")
