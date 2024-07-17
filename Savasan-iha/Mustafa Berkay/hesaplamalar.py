import json 
from vincenty import vincenty
import math

class Hesaplamalar():
    def __init__(self):
        self.rakip_telemetri_verileri = []

    def get_yonelim_acisi_farklari(self,rakip,bizim):  # Rakip İHA'lar ile bizim İHA'mız arasındaki açı farkını hesaplıyor. ve +- 50 derece olan İHA'ların telemetri verilerini döndürüyor
        bizim_yonelim_acimiz = bizim["iha_yonelme"]
        for i in rakip["konumBilgileri"]:
            rakip_telemetri = {
                "takim_id": '',
                "enlem": '',
                "boylam": '',
                "irtifa": ''
                }
            fark = abs(i["iha_yonelme"] - bizim_yonelim_acimiz)
            if fark > 180:
                aradaki_fark = 360 - fark
            else:
                aradaki_fark = fark
            #print(self.rakip_telemetri_verileri)
            if aradaki_fark <= 50:
                rakip_telemetri["takim_id"] = i["takim_numarasi"]
                rakip_telemetri["enlem"] = i["iha_enlem"]
                rakip_telemetri["boylam"] = i["iha_boylam"]
                rakip_telemetri["irtifa"] = i["iha_irtifa"]
                self.rakip_telemetri_verileri.append(rakip_telemetri)

    def rakip_sec(self,rakip,bizim): # yönelim açısı +-50 olan en uzak rakibi seçiyor ve telemetri verilerini döndürüyor
        enlem_boylam = (bizim["iha_enlem"], bizim["iha_boylam"])
        self.get_yonelim_acisi_farklari(rakip=rakip,bizim=bizim)
        gecici_mesafe=0
        for i in self.rakip_telemetri_verileri:
            aradaki_mesafe = vincenty((enlem_boylam), (i["enlem"], i["boylam"]))
            if aradaki_mesafe > gecici_mesafe:
                gecici_mesafe=aradaki_mesafe
                secilen_rakip=i
        self.rakip_telemetri_verileri = []
        return secilen_rakip
    
