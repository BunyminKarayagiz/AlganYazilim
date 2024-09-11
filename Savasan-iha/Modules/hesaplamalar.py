"""from vincenty import vincenty
import math

class Hesaplamalar():
    def init(self):
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
                "hiz": '',
                "dikilme":'',
                "yonelme":'',
                "yatis":'',
                }
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
                rakip_telemetri["dikilme"]=i["iha_dikilme"]
                rakip_telemetri["yonelme"]=i["iha_yonelme"]
                rakip_telemetri["yatis"]=i["iha_yatis"]
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
        self.rakip_telemetri_verileri = []
        self.aradaki_mesafeler= []
        return secilen_rakip"""