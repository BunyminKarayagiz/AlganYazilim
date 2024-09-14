
from fonksiyonlar import *



connect_to_anasunucu()
hss_koordinat = hss_coordinat()
fence_konumları = []
print(hss_koordinat)

#for i in hss_koordinat["hss_koordinat_bilgileri"]:
#    enlem = float(i["hssEnlem"])
#    boylam = float(i["hssBoylam"])
#    yarıçap = float(i["hssYaricap"])
#    fence_konumları.append((enlem, boylam, yarıçap))
#fence_dosya_kaydetme(fence_konumları, ucus_alanı, 'hss.waypoints')
#target_locations = wp_nokta_okuma("waypoints.waypoints")
#
#wp_kartezyen, ucus_alanı_kartezyen = wp_konum_hesapla(target_locations, ucus_alanı)
#
#
#fence_kartezyen = fence_konum_hesapla(fence_konumları)
#