from Modules.Arayuz import App
from Modules import Client_Tcp
import threading,time
from Modules import ana_sunucu_islemleri
import json

class flight_tracker:
    def __init__(self) -> None:
        self.UI=App()

        self.kullanici_adi = "algan"
        self.sifre = "53SnwjQ2sQ"
        self.ana_sunucu = ana_sunucu_islemleri.sunucuApi("http://127.0.0.1:5000")
        self.ana_sunucu_status = False

        self.bizim_telemetri = {"takim_numarasi": 1, "iha_enlem": 0,"iha_boylam":0,"iha_irtifa": 0,"iha_dikilme":0,
                                "iha_yonelme":0,"iha_yatis":0,"iha_hiz":0,"iha_batarya":0,"iha_otonom": 1,
                               "iha_kilitlenme": 1,"hedef_merkez_X": 300,"hedef_merkez_Y": 230,"hedef_genislik": 30,
                               "hedef_yukseklik": 43,"gps_saati": {"saat": time.gmtime().tm_hour,
                                                                   "dakika": time.gmtime().tm_min,
                                                                   "saniye": time.gmtime().tm_sec,
                                                                   "milisaniye": int((time.time() % 1) * 1000)
                                                                   }
                                }

    def anasunucuya_baglan(self):
            connection_status = False
            while not connection_status:
                try:
                    "Burada durum kodu işlemin başarı kodunu vermektedir örn:200"
                    ana_sunucuya_giris_kodu, durum_kodu = self.ana_sunucu.sunucuya_giris(str(self.kullanici_adi),str(self.sifre))
                    if int(durum_kodu) == 200:
                        print(f"\x1b[{31}m{'Ana Sunucuya Bağlanıldı: ' + durum_kodu}\x1b[0m")  # Ana sunucuya girerkenki durum kodu.
                        self.ana_sunucu_status = True
                        connection_status = self.ana_sunucu_status
                    else:
                        raise Exception("DURUM KODU '200' DEGIL")
                except Exception as e:
                    print("ANA SUNUCU : BAGLANTI HATASI -> ",e)

    def add_plane(self,lat,lon):
        time.sleep(4)
        self.UI.set_marker(lat,lon)

    def start_ui(self):
        self.UI.start()

    def main_op(self):
        self.anasunucuya_baglan()
        TK_INIT_TIME = 2
        time.sleep(TK_INIT_TIME)
        mainloop=False
        stat,ret = self.ana_sunucu.sunucuya_postala(self.bizim_telemetri)
        print(ret["takim"])
        # while not mainloop:
        #     self.add_plane_for_testing(start_lat=37,start_lon=30.7,limit=5,rotation=45)

    #!Testing
    def add_plane_for_testing(self,start_lat,start_lon,limit,rotation):
        time.sleep(4)
        while limit > 0:
            self.UI.set_marker(start_lat,start_lon,rotation)
            limit -= 1
            start_lon +=0.005
            rotation += 15
            time.sleep(0.05)

if __name__ == "__main__":
    tracker=flight_tracker()
    main_op=threading.Thread(target=tracker.main_op)
    main_op.start()
    tracker.start_ui()