from Modules.Arayuz import App
from Modules import Client_Tcp
import threading,time
from Modules import ana_sunucu_islemleri
import json

class flight_tracker:
    def __init__(self,Yazılım_ip) -> None:
        
        self.UI=App()

        self.TK_INIT_TIME_SEC = 2
        self.TK_INTERVAL_TIME_SEC = 5

        self.kullanici_adi = "algan"
        self.sifre = "53SnwjQ2sQ"
        self.ana_sunucu = ana_sunucu_islemleri.sunucuApi("http://127.0.0.1:5000")
        self.ana_sunucu_status = False

        self.TCP_telemetri=Client_Tcp.Client(Yazılım_ip,9010)
        self.Telem_client_status = False
        
        self.bizim_telemetri = {"takim_numarasi": 1, "iha_enlem": 0,"iha_boylam":0,"iha_irtifa": 0,"iha_dikilme":0,
                                "iha_yonelme":0,"iha_yatis":0,"iha_hiz":0,"iha_batarya":0,"iha_otonom": 1,
                               "iha_kilitlenme": 1,"hedef_merkez_X": 300,"hedef_merkez_Y": 230,"hedef_genislik": 30,
                               "hedef_yukseklik": 43,"gps_saati": {"saat": time.gmtime().tm_hour,
                                                                   "dakika": time.gmtime().tm_min,
                                                                   "saniye": time.gmtime().tm_sec,
                                                                   "milisaniye": int((time.time() % 1) * 1000)
                                                                   }
                                }

#!SERVER-OPERATIONS
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

    def Telemetri_sunucusuna_baglan(self):
        connection=False
        while not connection:
            try:
                self.TCP_telemetri.connect_to_server()
                connection=True
                self.Telem_client_status=connection
                print("TELEM SERVER: BAĞLANDI.")
            except (ConnectionError , Exception) as e:
                print("TELEM SERVER: baglanırken hata: ", e)

    def receive_telem(self):
        try:
            self.TCP_telemetri.client_recv_message()
        except Exception as e:
            print("TELEM SERVER : Telemetri Receive Error ->",e)

#! ROUTE PREDICTION
    def UNCOMPLETE_plane_predict(self):
        print("Function empty! :'UNCOMPLETE_plane_predict'")

#! UI-OPERATIONS
    def add_plane(self,lat,lon,rotation,plane_id):
        self.UI.set_marker(lat=lat,lon=lon,rotation=rotation,plane_id=plane_id)
        print(f"ID:{plane_id} -> [lat:{lat} , lon:{lon} , rotation:{rotation} ]")
    
    #!Testing
    def add_plane_for_testing(self,start_lat,start_lon,limit,rotation,plane_id):
        time.sleep(4)
        while limit > 0:
            self.UI.set_marker(lat=start_lat,lon=start_lon,rotation=rotation,plane_id=plane_id)
            limit -= 1
            start_lon +=0.005
            rotation += 15
            time.sleep(0.1)
            print("TEST-MARKERS ADDED(Antalya)")

    def update_planes(self):
        pass

    def start_ui(self):
        self.UI.start()

#! MAIN
    def main_op(self):
        self.anasunucuya_baglan()
        time.sleep(self.TK_INIT_TIME_SEC)
        mainloop=False

        #? USER_CODE_START

        stat,ret = self.ana_sunucu.sunucuya_postala(self.bizim_telemetri)
        ret = json.loads(ret)

        rakip_2 =ret['konumBilgileri'][1] #? Rakip Telem
        self.add_plane(lat=rakip_2['iha_enlem'],lon=rakip_2['iha_boylam'],rotation=rakip_2['iha_yonelme'],plane_id=rakip_2['takim_numarasi'])

        while not mainloop:
            time.sleep(self.TK_INTERVAL_TIME_SEC)
            self.add_plane_for_testing(start_lat=37,start_lon=30.7,limit=5,rotation=20,plane_id=99)

        #? USER_CODE_END

            mainloop=True


if __name__ == "__main__":
    tracker=flight_tracker("10.0.0.236") #Yazılım bilgisayarı IP -> 10.0.0.236
    main_op=threading.Thread(target=tracker.main_op)
    main_op.start()
    tracker.start_ui()