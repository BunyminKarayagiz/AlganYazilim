import matplotlib.pyplot as plt

from fonksiyonlar import *
import json
import subprocess
import ana_sunucu_islemleri


try:

    fence_konumları = fencenokta_okuma("hss.waypoints")

    target_locations = wp_nokta_okuma("waypoints.waypoints")

    wp_kartezyen, ucus_alanı_kartezyen = wp_konum_hesapla(target_locations, ucus_alanı)


    fence_kartezyen = fence_konum_hesapla(fence_konumları)
    silinecekler = []
    for wp in wp_kartezyen:
        for fence in fence_kartezyen:
            uzaklık = nokta_nokta(wp, fence)
            if uzaklık - x < fence[2]:
                print("Çemberin içinde olan nokta silindi", wp_kartezyen.index(wp) + 1)
                silinecekler.append(wp)
    for i in silinecekler:
        wp_kartezyen.remove(i)




    yeni_wp_kartezyen = []
    eklenen_noktalar = set()
    for wp in wp_kartezyen:
        try:
            sonraki_konum = wp_kartezyen[wp_kartezyen.index(wp) + 1]
        except IndexError:
            sonraki_konum = wp_kartezyen[0]
        for fence in fence_kartezyen:
            kesisin_varmi = kesisim_kontrol(wp, sonraki_konum, fence)
            if nokta_cember_icinde_mi(wp, fence) == False and wp not in yeni_wp_kartezyen:
                yeni_wp_kartezyen.append(wp)
            if kesisin_varmi == True:
                print(f"Kesişim var {wp_kartezyen.index(wp) + 1} ve {wp_kartezyen.index(sonraki_konum) + 1}")
                yeni_nokta1 = yeni_nokta_olusturma(wp, sonraki_konum, fence)
                yeni_nokta2 = yeni_nokta_olusturma2(wp, sonraki_konum, fence)

                if nokta_alanın_içinde_mi(yeni_nokta1, ucus_alanı_kartezyen) == True and nokta_cember_icinde_mi(
                        yeni_nokta1, fence) == False:
                    if yeni_nokta1 not in yeni_wp_kartezyen:
                        yeni_wp_kartezyen.append(yeni_nokta1)

                elif nokta_alanın_içinde_mi(yeni_nokta2, ucus_alanı_kartezyen) == True and nokta_cember_icinde_mi(
                        yeni_nokta2, fence) == False:
                    if yeni_nokta2 not in yeni_wp_kartezyen:
                        yeni_wp_kartezyen.append(yeni_nokta2)

                else:
                    for aci in range(0, 360, 45):

                        if aci == 0 or aci == 180 or aci == 90 or aci == 270:
                            continue
                        else:
                            yeni_nokta = yeni_nokta_olusturma_aci(wp, sonraki_konum, fence, aci)

                            if yeni_nokta not in yeni_wp_kartezyen and nokta_alanın_içinde_mi(yeni_nokta,
                                                                                              ucus_alanı_kartezyen) == True and nokta_cember_icinde_mi(
                                    yeni_nokta, fence_kartezyen) == False:
                                yeni_wp_kartezyen.append(yeni_nokta)
                            else:
                                continue



    # burada rota oluşturulur
    yeni_rota = []
    for nokta in yeni_wp_kartezyen:
        yeni_nokta = kartezyen_to_enlem_boylam(nokta, home_konumu)
        yeni_rota.append(yeni_nokta)
    WPnoktaları_dosyaya_yaz(yeni_rota, 'yeni_rota.waypoints')
    fence_dosya_kaydetme(fence_konumları, ucus_alanı, 'hss.waypoints')
    print("Rota oluşturuldu")
    print("olşturulan rota yeni_rota.waypoints dosyasına yazıldı.")
    cizim_listesi = [(fence_kartezyen, 'kırmızı'), (yeni_wp_kartezyen, 'yeşil'), (ucus_alanı_kartezyen, 'mavi')]
    ciz(cizim_listesi)
except:
    print("görev tamamlandı")
