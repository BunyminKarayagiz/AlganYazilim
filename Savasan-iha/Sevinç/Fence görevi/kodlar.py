from fonksiyonlar import *
import json
import time
import ana_sunucu_islemleri
import subprocess
try:

    api = ana_sunucu_islemleri.sunucuApi("http://127.0.0.1:5000")
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
        return coordinat_text["hss_koordinat_bilgileri"]


    boolen = connect_to_anasunucu()
    hss_coordinat=hss_coordinat()
    fence_konumları=[]
    noktalar = [(nokta['hssEnlem'], nokta['hssBoylam'], nokta['hssYaricap']) for nokta in hss_coordinat]
    for nokta in noktalar:
        fence_konumları.append(nokta)

    #burada fonksiyonlardan waypointt ve fence parametreleri okunur
    target_locations = wp_nokta_okuma("waypoint.waypoints")
    #fence_konumları, ucus_alanı = fencenokta_okuma("Fencewpoints.waypoints")
    wp_kartezyen, ucus_alanı_kartezyen = wp_konum_hesapla(target_locations, ucus_alanı)
    fence_kartezyen = fence_konum_hesapla(fence_konumları)


    #burada çemberin içinde olan noktalar silinir.
    for wp in wp_kartezyen:
        for fence in fence_kartezyen:
            if nokta_cember_icinde_mi(wp,fence)==True:
                wp_kartezyen.remove(wp)

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
                yeni_nokta = yeni_nokta1
                for cember in fence_kartezyen:  # bu döngü ile eğer bu nokta başka bir çemberin içinde ise tam ters yöndeki nokta oluşturuluyor.
                    if nokta_cember_icinde_mi(yeni_nokta1, cember) == True or nokta_alanın_içinde_mi(yeni_nokta1,
                                                                                                     ucus_alanı_kartezyen) == False:
                        yeni_nokta = yeni_nokta2  # burad her bir eklenen nokta için alan sorgulaması yap0ıyor alanın dışına düşüyor ise nokta başka bir nokta oluşturuyor.
                if yeni_nokta not in eklenen_noktalar:
                    yeni_wp_kartezyen.append(yeni_nokta)
                    eklenen_noktalar.add(yeni_nokta)  # Yeni nokta eklenenler listesine ekleniyor.

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
        if aralarındaki_açı < 90:
            wp = genislet_ve_yakinlastir(önceki_konum, wp, sonraki_konum, 90 - aralarındaki_açı)





    #burada rota oluşturulur
    yeni_rota = []
    for nokta in yeni_wp_kartezyen:
        yeni_nokta = kartezyen_to_enlem_boylam(nokta, home_konumu)
        yeni_rota.append(yeni_nokta)
    WPnoktaları_dosyaya_yaz(yeni_rota, 'yeni_rota.waypoints')
    cizim_listesi = [(fence_kartezyen, 'kırmızı'), (yeni_wp_kartezyen, 'yeşil'), (ucus_alanı_kartezyen, 'mavi')]
    ciz(cizim_listesi)

    print("Rota oluşturuldu" )
except KeyboardInterrupt:
    print("Programdan çıkılıyor")