import fonksiyonlar
from fonksiyonlar import *

try:

    target_locations = wp_nokta_okuma("waypoint.waypoints")
    fence_konumları = fencenokta_okuma("Fencewpoints.waypoints")
    wp_kartezyen=wp_konum_hesapla(target_locations)
    fence_kartezyen=fence_konum_hesapla(fence_konumları)
    kesisim=[]
    yeni_wp_kartezyen=[]
    for wp in wp_kartezyen:
        try:
            sonraki_konum = wp_kartezyen[wp_kartezyen.index(wp) + 1]

        except:
            sonraki_konum = wp_kartezyen[0]

        finally:
            pass
        for fence in fence_kartezyen:
            dogru = dogru_denklemi_olustur(wp[0],sonraki_konum[0] ,wp[1] ,sonraki_konum[1] )
            cember = cember_denklemi(fence[0], fence[1], fence[2])
            kesisin_varmi=kesisim_kontrol(wp, sonraki_konum, fence)
            if nokta_cember_icinde_mi(wp,fence)==False:
                yeni_wp_kartezyen.append(wp)
            if kesisin_varmi==True:
                yeni_nokta1=yeni_nokta_olusturma(wp, sonraki_konum, fence)
                yeni_nokta2=yeni_nokta_olusturma2(wp,sonraki_konum, fence)
                yeni_nokta=yeni_nokta1
                for cember in fence_kartezyen:
                    if nokta_cember_icinde_mi(yeni_nokta1,cember)==True:
                        yeni_nokta=yeni_nokta2
                yeni_wp_kartezyen.append(yeni_nokta)





    print(yeni_wp_kartezyen)
    yeni_rota=[]
    for nokta in yeni_wp_kartezyen:
        yeni_nokta=kartezyen_to_enlem_boylam(nokta, home_konumu)
        yeni_rota.append(yeni_nokta)
    print(yeni_rota)
    WPnoktaları_dosyaya_yaz(yeni_rota,'yeni_rota.waypoints')
    ciz(fence_kartezyen,wp_kartezyen,yeni_wp_kartezyen)
except KeyboardInterrupt:
    print("Programdan çıkıldı")
