import ana_sunucu_islemleri
import json
import os
import shutil

def coordinat_text():
    api = ana_sunucu_islemleri.sunucuApi("http://10.0.0.236:5000")
    "Burada durum kodu işlemin başarı kodunu vermektedir örn:200"
    ana_sunucuya_giris_durumu = False
    ana_sunucuya_giris_kodu, durum_kodu = api.sunucuya_giris(
        str("algan"),
        str("53SnwjQ2sQ"))
    try:
        if int(durum_kodu) == 200:
            print(f"\x1b[{31}m{'Ana Sunucuya Bağlanıldı: ' + durum_kodu}\x1b[0m")  # Ana sunucya girerkenki durum kodu.
            ana_sunucuya_giris_durumu = True
    except ValueError:
        print(f"\x1b[{31}m{'Ana Sunucuya Bağlanılamadı: ' + durum_kodu}\x1b[0m")
    status_code, coordinat_text = api.get_hava_savunma_coord()
    coordinat_text = json.loads(coordinat_text)
    return coordinat_text

def fence_dosya_kaydetme(fence_konumları,ucus_alanı, dosya_adi):

    ucus_alanı_miktarı = len(ucus_alanı)
    fence_konumları_miktarı = len(fence_konumları)

    with open(dosya_adi, 'w') as dosya:
        dosya.truncate(0)
        dosya.write("QGC WPL 110\n")
        dosya.write("0\t1\t0\t16\t0\t0\t0\t0\t40.2320505\t29.0042872\t100.220000\t1\n")
        for i, konum in enumerate(ucus_alanı, start=1):
            dosya.write(
                f"{i}\t0\t0\t5001\t5.00000000\t0.00000000\t0.00000000\t0.00000000\t{konum[0]}\t{konum[1]}\t100.000000\t1\n")
        for j, konum in enumerate(fence_konumları, start=ucus_alanı_miktarı + 1):
            dosya.write(
                f"{j}\t0\t0\t5004\t{float(konum[2]):.8f}\t0.00000000\t0.00000000\t0.00000000\t{konum[0]}\t{konum[1]}\t100.000000\t1\n")
ucus_alanı=[(36.942314,35.563323),(36.942673,35.553363),(36.937683,35.553324),(36.937864,35.562873)]
#bu kısımda hss koordinatlarını alıp dosyaya kaydediyoruz.
hss_koordinat = coordinat_text()

fence_konumları = []
for i in hss_koordinat["hss_koordinat_bilgileri"]:
    enlem = float(i["hssEnlem"])
    boylam = float(i["hssBoylam"])
    yarıçap = float(i["hssYaricap"])
    fence_konumları.append((enlem, boylam, yarıçap))
fence_dosya_kaydetme(fence_konumları, ucus_alanı, 'hss.waypoints')