from vincenty import vincenty
import math

# 7A7B85
rakip = {
    "konumBilgileri": [
        {
            "iha_boylam": 60.1420221,
            "iha_dikilme": 5,
            "iha_enlem": 32.186471,
            "iha_irtifa": 50,
            'iha_hiz': 3.85,
            "iha_yatis": 0,
            "iha_yonelme": 240,
            "takim_numarasi": 1,
            "zaman_farki": 93
        },
        {
            "iha_boylam": 50.1362715,
            "iha_dikilme": 5,
            "iha_enlem": 35.1827881,
            "iha_irtifa": 60,
            'iha_hiz': 5,
            "iha_yatis": 0,
            "iha_yonelme": 30,
            "takim_numarasi": 2,
            "zaman_farki": 74
        },
        {
            "iha_boylam": 20.1358852,
            "iha_dikilme": 5,
            "iha_enlem": 35.1939238,
            "iha_irtifa": 70,
            'iha_hiz': 3.85,
            "iha_yatis": 0,
            "iha_yonelme": 50,
            "takim_numarasi": 3,
            "zaman_farki": 43
        },
        {
            "iha_boylam": 30.1362715,
            "iha_dikilme": 5,
            "iha_enlem": -35.1827881,
            "iha_irtifa": 60,
            'iha_hiz': 8,
            "iha_yatis": 0,
            "iha_yonelme": 60,
            "takim_numarasi": 4,
            "zaman_farki": 74
        },
        {
            "iha_boylam": 29.0095263,
            "iha_dikilme": 5,
            "iha_enlem": 40.331272,
            "iha_irtifa": 60,
            'iha_hiz': 70,
            "iha_yatis": 0,
            "iha_yonelme": 0,
            "takim_numarasi": 5,
            "zaman_farki": 74
        }
    ],
    "sistemSaati": {
        "dakika": 53,
        "milisaniye": 500,
        "saat": 6,
        "saniye": 42
    }
}
bizim = {'takim_numarasi': 1, 'iha_enlem': 40.331272, 'iha_boylam': 29.0095263, 'iha_irtifa': 2.36, 'iha_dikilme': 0.08,
         'iha_yonelme': 10, 'iha_yatis': 0.07, 'iha_hiz': 3.85, 'iha_batarya': None, 'iha_otonom': 0,
         'iha_kilitlenme': 0, 'hedef_merkez_X': 0, 'hedef_merkez_Y': 0, 'hedef_genislik': 0, 'hedef_yukseklik': 0,
         'gps_saati': {'saat': 10, 'dakika': 31, 'saniye': 50, 'milisaniye': 56}, 'iha_mod': ' '}


class Hesaplamalar():
    def __init__(self):
        self.aradaki_mesafeler = []
        self.rakip_telemetri_verileri = []

    def get_yonelim_acisi_farklari(self,rakip,bizim):  # Rakip İHA'lar ile bizim İHA'mız arasındaki açı farkını hesaplıyor. ve +- 50 derece olan İHA'ların telemetri verilerini döndürüyor
        bizim_yonelim_acimiz = bizim["iha_yonelme"]
        for i in rakip["konumBilgileri"]:
            rakip_telemetri = {
                "takim_id": '',
                "enlem": '',
                "boylam": '',
                "irtifa": '',
                "hiz": ''}
            fark = abs(i["iha_yonelme"] - bizim_yonelim_acimiz)
            if fark > 180:
                aradaki_fark = 360 - fark
            else:
                aradaki_fark = fark
            if aradaki_fark <= 50:
                rakip_telemetri["takim_id"] = i["takim_numarasi"]
                rakip_telemetri["enlem"] = i["iha_enlem"]
                rakip_telemetri["boylam"] = i["iha_boylam"]
                rakip_telemetri["irtifa"] = i["iha_irtifa"]
                rakip_telemetri["hiz"] = i["iha_hiz"]
                self.rakip_telemetri_verileri.append(rakip_telemetri)
        return self.rakip_telemetri_verileri

    def rakip_sec(self,rakip,bizim): # yönelim açısı +-50 olan en uzak rakibi seçiyor ve telemetri verilerini döndürüyor
        enlem_boylam = (bizim["iha_enlem"], bizim["iha_boylam"])
        rakip_telemetrileri = self.get_yonelim_acisi_farklari(rakip,bizim)
        gecici_mesafe=0
        for i in rakip_telemetrileri:
            aradaki_mesafe = vincenty((enlem_boylam), (i["enlem"], i["boylam"]))
            if aradaki_mesafe > gecici_mesafe:
                gecici_mesafe=aradaki_mesafe
                secilen_rakip=i
        return secilen_rakip
hesap = Hesaplamalar()
print(hesap.rakip_sec(rakip,bizim))