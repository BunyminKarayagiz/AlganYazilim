from vincenty import vincenty
import math

rakip = {
    "konumBilgileri": [
        {
            "iha_boylam": 149.1420221,
            "iha_dikilme": 5,
            "iha_enlem": -35.186471,
            "iha_irtifa": 50,
            "iha_yatis": 0,
            "iha_yonelme": 240,
            "takim_numarasi": 1,
            "zaman_farki": 93
        },
        {
            "iha_boylam": 149.1362715,
            "iha_dikilme": 5,
            "iha_enlem": -35.1827881,
            "iha_irtifa": 60,
            "iha_yatis": 0,
            "iha_yonelme": 200,
            "takim_numarasi": 2,
            "zaman_farki": 74
        },
        {
            "iha_boylam": 149.1358852,
            "iha_dikilme": 5,
            "iha_enlem": -35.1939238,
            "iha_irtifa": 70,
            "iha_yatis": 0,
            "iha_yonelme": 250,
            "takim_numarasi": 3,
            "zaman_farki": 43
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
         'iha_yonelme': 180, 'iha_yatis': 0.07, 'iha_hiz': 3.85, 'iha_batarya': None, 'iha_otonom': 0,
         'iha_kilitlenme': 0, 'hedef_merkez_X': 0, 'hedef_merkez_Y': 0, 'hedef_genislik': 0, 'hedef_yukseklik': 0,
         'gps_saati': {'saat': 10, 'dakika': 31, 'saniye': 50, 'milisaniye': 56}, 'iha_mod': ' '}


class Hesaplamalar():
    def __init__(self):
        self.derece_farklari = []
        self.rakip_radyanlar = []
        self.rakip_boylamlar = []
        self.rakip_enlemler = []
        self.rakip_acilar = []
        self.rakip_indexleri = []
        self.rakip_mesafeler = []

    def radyan_hesapla(self, rakip, bizim):
        bizim_acimiz = math.radians(bizim["iha_yonelme"])
        radyanlar = self.rakip_radyanlari(rakip)
        for i in radyanlar:
            radyan_farklari = abs(bizim_acimiz - i)
            derece_fark = math.degrees(radyan_farklari)
            if derece_fark > 180:
                asli = 360 - derece_fark
                self.derece_farklari.append(asli)
            else:
                self.derece_farklari.append(derece_fark)
        return self.derece_farklari

    def rakip_radyanlari(self, rakip):
        rakip_acilar = self.yonelim_acısı(rakip)
        for i in rakip_acilar:
            self.rakip_radyanlar.append(math.radians(i))
        return self.rakip_radyanlar

    def get_enlem_boylam(self, konum_bilgileri):
        for i in konum_bilgileri["konumBilgileri"]:
            self.rakip_boylamlar.append(i["iha_boylam"])
            self.rakip_enlemler.append(i["iha_enlem"])
        return self.rakip_boylamlar, self.rakip_enlemler

    def yonelim_acısı(self, konum_bilgileri):
        for i in konum_bilgileri["konumBilgileri"]:
            self.rakip_acilar.append(i["iha_yonelme"])
        return self.rakip_acilar

    def rakip_sec(self, konum_bilgileri, bizim_veriler):
        rakip_yonelim_acileri = self.yonelim_acısı(konum_bilgileri)
        bizim_acimiz = bizim_veriler["iha_yonelme"]
        for i in rakip_yonelim_acileri:
            if (bizim_acimiz <= i + 60) and (
                    bizim_acimiz >= i - 60):  # 60 derecelik bir hata payı bırakıldı ama eksik çalışıyor. Sebebi örn rakip 360 biz 1 olabiliriz bu durumda aynı açıda olmamıza rağmen düzgün çalışmayacak
                self.rakip_indexleri.append(rakip_yonelim_acileri.index(i))
        return self.rakip_indexleri

    def mesafe_hesaplama(self, konum_bilgileri, bizim_veriler):
        enlem = bizim_veriler["iha_enlem"]
        boylam = bizim_veriler["iha_boylam"]
        boylamlar, enlemler = self.get_enlem_boylam(konum_bilgileri)

        for i in range(0, len(boylamlar)):
            self.rakip_mesafeler.append(vincenty((enlemler[i], boylamlar[i]), (enlem, boylam)))
        return self.rakip_mesafeler


hesap = Hesaplamalar()
print(hesap.radyan_hesapla(rakip, bizim))
