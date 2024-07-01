import datetime
import json
import time

import ana_sunucu_islemleri

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


def get_sunucusaat():
    status_code, sunuc_saati = api.sunucu_saati_al()
    sunuc_saati = json.loads(sunuc_saati)
    return sunuc_saati["saat"], sunuc_saati["dakika"], sunuc_saati["saniye"], sunuc_saati["milisaniye"]

def senkron_local_saat(local, sunucu):
    pass



boolen = connect_to_anasunucu()

while boolen:
    bugun = datetime.datetime.today()
    sunucu_saat, sunucu_dakika, sunucu_saniye, sunucu_milisaniye = get_sunucusaat()
    sunucu_saati = datetime.datetime(year= bugun.year, month= bugun.month, day=bugun.day ,hour= sunucu_saat,minute= sunucu_dakika,second= sunucu_saniye,microsecond= sunucu_milisaniye)

    print(bugun)
    print(sunucu_saati)
    fark = abs(bugun - sunucu_saati)
    print( "fark ",fark)
    bugun = bugun + fark
    print("yeni_bugun", bugun)




    time.sleep(1)
