import matplotlib.pyplot as plt

from fonksiyonlar import *
import json
import subprocess
import ana_sunucu_islemleri

try:
    #print(f"\x1b[{31}m{'Ana Sunucuya Bağlanıldı: 200'}\x1b[0m")
    #print(f"\x1b[31mHSS Koordinatları Alındı: 200\x1b[0m")
    api=ana_sunucu_islemleri.sunucuApi("http://127.0.0.1:5000")
    def connect_to_anasunucu():
        "Burada durum kodu işlemin başarı kodunu vermektedir örn:200"
        ana_sunucuya_giris_durumu = False
        ana_sunucuya_giris_kodu, durum_kodu = api.sunucuya_giris(
            str("algan"),
            str("53SnwjQ2sQ"))
        if int(durum_kodu) == 200:
            print(f"\x1b[{31}m{'Ana Sunucuya Bağlanıldı: ' + durum_kodu}\x1b[0m")  # Ana sunucya girerkenki durum kodu.
            ana_sunucuya_giris_durumu = True
        return ana_sunucuya_giris_durumu
    def hss_coordinat():
        status_code, coordinat_text = api.get_hava_savunma_coord()
        coordinat_text = json.loads(coordinat_text)
        return coordinat_text
    boolen = connect_to_anasunucu()
    hss_koordinat = hss_coordinat()
    fence_konumları=[]
    for i in hss_koordinat["hss_koordinat_bilgileri"]:
        enlem= float(i["hssEnlem"])
        boylam= float(i["hssBoylam"])
        yarıçap= float(i["hssYaricap"])
        fence_konumları.append((enlem,boylam,yarıçap))
#burada fonksiyonlardan waypointt ve fence parametreleri okunur
    target_locations = wp_nokta_okuma("waypoint.waypoints")
    wp_kartezyen, ucus_alanı_kartezyen = wp_konum_hesapla(target_locations, ucus_alanı)
    fence_kartezyen = fence_konum_hesapla(fence_konumları)
    #burada çemberin içinde olan noktalar silinir.
    for wp in wp_kartezyen:
        for fence in fence_kartezyen:
            uzaklık=nokta_nokta( wp, fence)
            if uzaklık +x< fence[2]:
                wp_kartezyen.remove(wp)
                break
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
                yeni_nokta1 = yeni_nokta_olusturma(wp, sonraki_konum, fence)
                yeni_nokta2 = yeni_nokta_olusturma2(wp, sonraki_konum, fence)
                if nokta_alanın_içinde_mi(yeni_nokta1, ucus_alanı_kartezyen) == True and nokta_cember_icinde_mi(yeni_nokta1, fence) == False:
                    if yeni_nokta1 not in yeni_wp_kartezyen:
                        yeni_wp_kartezyen.append(yeni_nokta1)
                        cizim_listesi = [(fence_kartezyen, 'kırmızı'), (yeni_wp_kartezyen, 'yeşil'),
                                         (ucus_alanı_kartezyen, 'mavi'), ([yeni_nokta1], 'siyah')]
                        ciz(cizim_listesi)
                elif nokta_alanın_içinde_mi(yeni_nokta2, ucus_alanı_kartezyen) == True and nokta_cember_icinde_mi(yeni_nokta2, fence) == False:
                    if yeni_nokta2 not in yeni_wp_kartezyen:
                        yeni_wp_kartezyen.append(yeni_nokta2)
                        cizim_listesi = [(fence_kartezyen, 'kırmızı'), (yeni_wp_kartezyen, 'yeşil'),
                                         (ucus_alanı_kartezyen, 'mavi'), ([yeni_nokta2], 'siyah')]
                        ciz(cizim_listesi)
                else:
                        for aci in range(0,360,45):

                            if aci==0 or aci==180 or aci==90 or aci==270:
                                continue
                            else:
                                yeni_nokta=yeni_nokta_olusturma_aci(wp,sonraki_konum,fence,aci)
                                cizim_listesi = [(fence_kartezyen, 'kırmızı'), (yeni_wp_kartezyen, 'yeşil'),
                                                 (ucus_alanı_kartezyen, 'mavi'), ([yeni_nokta], 'siyah')]
                                ciz(cizim_listesi)
                                if yeni_nokta not in yeni_wp_kartezyen and nokta_alanın_içinde_mi(yeni_nokta, ucus_alanı_kartezyen) == True and nokta_cember_icinde_mi(yeni_nokta, fence_kartezyen) == False:
                                    yeni_wp_kartezyen.append(yeni_nokta)
                                else:
                                    continue



    for wp in yeni_wp_kartezyen:
        try:
            sonraki_konum= yeni_wp_kartezyen[yeni_wp_kartezyen.index(wp) + 1]
        except:
            sonraki_konum = yeni_wp_kartezyen[0]
        try:
            önceki_konum = yeni_wp_kartezyen[yeni_wp_kartezyen.index(wp) - 1]
        except:
            index= len(yeni_wp_kartezyen) - 1
            önceki_konum = yeni_wp_kartezyen[index]
        aralarındaki_açı = aci_hesapla(önceki_konum, wp, sonraki_konum)
        if aralarındaki_açı < 60:
            wp = genislet_ve_yakinlastir(önceki_konum, wp, sonraki_konum, 60 - aralarındaki_açı)

    #burada rota oluşturulur
    yeni_rota = []
    for nokta in yeni_wp_kartezyen:
        yeni_nokta = kartezyen_to_enlem_boylam(nokta, home_konumu)
        yeni_rota.append(yeni_nokta)
    WPnoktaları_dosyaya_yaz(yeni_rota, 'yeni_rota.waypoints')
    fence_dosya_kaydetme(fence_konumları, ucus_alanı, 'hss.waypoints')
    print("Rota oluşturuldu" )
    print("olşturulan rota yeni_rota.waypoints dosyasına yazıldı.")
    cizim_listesi = [(fence_kartezyen, 'kırmızı'), (yeni_wp_kartezyen, 'yeşil'), (ucus_alanı_kartezyen, 'mavi')]
    ciz(cizim_listesi)
except KeyboardInterrupt:
    print("Programdan çıkılıyor")