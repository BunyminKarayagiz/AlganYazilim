import matplotlib.pyplot as plt

from fonksiyonlar import *
import json
import subprocess
import ana_sunucu_islemleri


try:

    connect_to_anasunucu()
    hss_koordinat = hss_coordinat()

    fence_konumları = []
    for i in hss_koordinat["hss_koordinat_bilgileri"]:
        enlem = float(i["hssEnlem"])
        boylam = float(i["hssBoylam"])
        yarıçap = float(i["hssYaricap"])
        fence_konumları.append((enlem, boylam, yarıçap))
    fence_dosya_kaydetme(fence_konumları, ucus_alanı, 'hss.waypoints')
    saptıran_noktalar = []
    guncel_wp = []
    for i in range(5):
        #fence_konumları = fencenokta_okuma("hss.waypoints")


        target_locations = wp_nokta_okuma("waypoints.waypoints")

        wp_kartezyen, ucus_alanı_kartezyen = wp_konum_hesapla(target_locations, ucus_alanı)


        fence_kartezyen = fence_konum_hesapla(fence_konumları)
        silinecekler = []
        for wp in wp_kartezyen:
            for fence in fence_kartezyen:
                uzaklık = nokta_nokta(wp, fence)
                if uzaklık - x < fence[2]:

                    silinecekler.append(wp)
        for i in silinecekler:
            try:
                wp_kartezyen.remove(i)
            except:
                continue


        yeni_wp_kartezyen = []

        for wp in wp_kartezyen:
            try:
                sonraki_konum = wp_kartezyen[wp_kartezyen.index(wp) + 1]
            except IndexError:
                sonraki_konum = wp_kartezyen[0]
            for fence in fence_kartezyen:
                kesisin_varmi = kesisim_kontrol(wp, sonraki_konum, fence)
                if nokta_cember_icinde_mi(wp, fence) == False and wp not in yeni_wp_kartezyen:
                    yeni_wp_kartezyen.append(wp)
                    saptıran_noktalar.append(wp)
                if kesisin_varmi == True:
                    print(f"Kesişim var {wp_kartezyen.index(wp) + 1} ve {wp_kartezyen.index(sonraki_konum) + 1}")
                    yeni_nokta1 = yeni_nokta_olusturma(wp, sonraki_konum, fence)
                    yeni_nokta2 = yeni_nokta_olusturma2(wp, sonraki_konum, fence)

                    if nokta_alanın_içinde_mi(yeni_nokta1, ucus_alanı_kartezyen) == True and nokta_cember_icinde_mi(
                            yeni_nokta1, fence) == False:
                        if yeni_nokta1 not in yeni_wp_kartezyen:
                            yeni_wp_kartezyen.append(yeni_nokta1)
                            saptıran_noktalar.append(yeni_nokta1)

                    elif nokta_alanın_içinde_mi(yeni_nokta2, ucus_alanı_kartezyen) == True and nokta_cember_icinde_mi(
                            yeni_nokta2, fence) == False:
                        if yeni_nokta2 not in yeni_wp_kartezyen:
                            yeni_wp_kartezyen.append(yeni_nokta2)
                            saptıran_noktalar.append(yeni_nokta2)

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
                                    saptıran_noktalar.append(yeni_nokta)
                                else:
                                    continue
        wp_kartezyen = []
        silincekler = []
        print("Saptıran noktalar", saptıran_noktalar)
        for wp in yeni_wp_kartezyen:
            nokta1=None
            nokta2=None
            try:
                sonraki_konum = yeni_wp_kartezyen[yeni_wp_kartezyen.index(wp) + 1]
            except IndexError:
                sonraki_konum = yeni_wp_kartezyen[0]
            try:
                onceki_konum = yeni_wp_kartezyen[yeni_wp_kartezyen.index(wp) - 1]
            except IndexError:
                onceki_konum = yeni_wp_kartezyen[-1]
            aci = calculate_turn_angle(onceki_konum, wp, sonraki_konum)
            once_dis = nokta_nokta(onceki_konum, wp)
            sonra_dis = nokta_nokta(wp, sonraki_konum)
            if once_dis < 20 or sonra_dis < 20:
                if wp not in saptıran_noktalar:
                    silincekler.append(wp)
            if aci < 60:
                print("Dönüş açısı 30 dereceden küçük")
                if wp not in saptıran_noktalar:
                    silincekler.append(wp)
                else:
                    nokta1=orta_nokta(onceki_konum, wp)
                    nokta2=orta_nokta(wp, sonraki_konum)
            if aci > 60 and aci < 120:
                print("Dönüş açısı 60 ile 120 derece arasında")
                nokta1 = orta_nokta(onceki_konum, wp)
                nokta2 = orta_nokta(wp, sonraki_konum)
                silinecekler.append(wp)
            if nokta1 != None and nokta2 != None:
                if nokta1 not in wp_kartezyen:
                    wp_kartezyen.append(nokta1)
                if nokta2 not in wp_kartezyen:
                    wp_kartezyen.append(nokta2)
            else:
                if wp not in wp_kartezyen and wp not in silinecekler:
                    wp_kartezyen.append(wp)
        for i in silinecekler:
            try:
                wp_kartezyen.remove(i)
            except:
                continue
        guncel_wp=wp_kartezyen

        yeni_rota = []

        for wp in wp_kartezyen:
            try:
                sonraki_konum = wp_kartezyen[wp_kartezyen.index(wp) + 1]
            except IndexError:
                sonraki_konum = wp_kartezyen[0]
            try:
                onceki_konum = wp_kartezyen[wp_kartezyen.index(wp) - 1]
            except IndexError:
                onceki_konum = wp_kartezyen[-1]
            once= nokta_nokta(onceki_konum, wp)
            sonra= nokta_nokta(wp, sonraki_konum)
            if once < 30 or sonra < 30:
                if wp or onceki_konum or sonraki_konum not in saptıran_noktalar:
                    silinecekler.append(wp)
        for i in silinecekler:
            try:
                wp_kartezyen.remove(i)
            except:
                continue


        for nokta in wp_kartezyen:
            yeni_nokta = kartezyen_to_enlem_boylam(nokta, home_konumu)
            yeni_rota.append(yeni_nokta)
        WPnoktaları_dosyaya_yaz(yeni_rota, 'waypoints.waypoints')
        fence_dosya_kaydetme(fence_konumları, ucus_alanı, 'hss.waypoints')
        print("Rota oluşturuldu")
        print("olşturulan rota waypoints.waypoints dosyasına yazıldı.")

    cizim_listesi = [(fence_kartezyen, 'kırmızı'), (wp_kartezyen, 'yeşil'), (ucus_alanı_kartezyen, 'mavi')]
    ciz(cizim_listesi)




except KeyboardInterrupt:
    print("Görev tamamlandı")
except:
    fence_dosya_kaydetme(fence_konumları, ucus_alanı, 'hss.waypoints')




