from Modules.Arayuz import App
from Modules import Client_Tcp ,Server_Tcp
import threading,time
from Modules import ana_sunucu_islemleri
import json
from Modules import path
import argparse
from typing import Dict,Any
import rgbprint as Cprint
from random import randint
import math

#!CLASS OBJ
class Plane:
    def __init__(self, takim_numarasi: int, UI ,limit = 5):
        self.takim_numarasi = takim_numarasi
        self.data = []
        self.lock = threading.Lock()
        self.color = (randint(0,255),randint(0,255),randint(0,255))
        self.UI = UI
        self.limit = limit
        self.marker_list = []
        self.Prediction = []

        self.Start_looping()

    def append_data(self, new_data: Dict[str, Any]):
        with self.lock:
            if len(self.data) > self.limit:
                self.data.pop(0)
            Cprint.rgbprint(f"Plane {self.takim_numarasi} Present Data: {self.data}",color=self.color)
            if len(self.marker_list) >= self.limit:
                (self.marker_list.pop(0)).delete()
            self.marker_list.append(self.UI.set_plane(lat=new_data['iha_enlem'],lon=new_data['iha_boylam'],rotation=new_data['iha_yonelme'],plane_id=self.takim_numarasi))
            self.predict_next_position(x=new_data['iha_boylam'],y=new_data['iha_enlem'],speed=new_data['iha_hizi'],roll_degree=new_data['iha_yatis'])
            self.data.append(new_data)

#! ROUTE PREDICTION
    def predict_next_position(self,x, y, speed, roll_degree):
            self.Prediction.clear()
            direction_radians = math.radians(roll_degree)
    
        # Calculate displacement
            delta_x = speed * math.cos(direction_radians)
            delta_y = speed * math.sin(direction_radians)
    
        # Predicted next position
            next_x = x + delta_x
            next_y = y + delta_y
            self.Prediction.append(self.UI.set_plane(lat=next_x,lon=next_y,rotation=0,plane_id=f"{self.takim_numarasi}-Predict"))
            Cprint.rgbprint(f"Plane {self.takim_numarasi} processing data: {self.data}",color=self.color)
            time.sleep(1)

    def start_looping(self):
        pass


#!CLASS MAIN
class FlightTracker:
    def __init__(self,Yazılım_ip) -> None:
        
        self.UI=App()

        self.TK_INIT_TIME_SEC = 2
        self.TK_INTERVAL_TIME_SEC = 2

        self.kullanici_adi = "algan"
        self.sifre = "53SnwjQ2sQ"
        self.Algan_ID = "1"
        self.ana_sunucu = ana_sunucu_islemleri.sunucuApi("http://127.0.0.1:5000")
        self.ana_sunucu_status = False

        self.ID_Client=Client_Tcp.Client(Yazılım_ip,9010) #Yazılım bilgisayarından Sunucu_Cevabı alacak Client
        self.TCP_Iha_yonelim = Server_Tcp.Server(PORT=9011,name="IHA_yonelim") #Iha'ya yonelim verisini gönderecek Server
        
        self.iha:any
        
        self.planes = {}
        self.threads = []
        self.plane_dict = {}
        self.plane_show_limit = 3

#!SERVER-OPERATIONS
    def anasunucuya_baglan(self):
            connection_status = False
            while not connection_status:
                try:
                    "Burada durum kodu işlemin başarı kodunu vermektedir örn:200"
                    ana_sunucuya_giris_kodu, durum_kodu = self.ana_sunucu.sunucuya_giris(str(self.kullanici_adi),str(self.sifre))
                    print(durum_kodu)
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
                self.ID_Client.connect_to_server()
                connection=True
                self.Telem_client_status=connection
                print("TELEM SERVER: BAĞLANDI.")
            except (ConnectionError , Exception) as e:
                print("TELEM SERVER: baglanırken hata: ", e)

    def Yonelim_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.TCP_Iha_yonelim.creat_server()
                connection_status=True
                print("IHA_YONELIM : SERVER OLUŞTURULDU\n")
            except (ConnectionError, Exception) as e:
                print("IHA_YONELIM SERVER: oluştururken hata : ", e , " \n")
                print("IHA_YONELIM SERVER: yeniden bağlanılıyor...\n")
                self.TCP_Iha_yonelim.reconnect()
                print("IHA_YONELIM : SERVER OLUŞTURULDU\n")
        self.kamikaze_sunucusu = connection_status
        return connection_status

    def receive_telem(self):
        try:
            self.ID_Client.client_recv_message()
        except Exception as e:
            print("TELEM SERVER : Telemetri Receive Error ->",e)

    def process_data_stream(self, data_stream: str):
        parsed_data = json.loads(data_stream)["konumBilgileri"]

        for entry in parsed_data:
            takim_numarasi = entry["takim_numarasi"]
            if takim_numarasi not in self.planes:
                print("YENI UÇAK TESPIT EDILDI -> ",takim_numarasi," ",self.planes)
                self.add_plane(takim_numarasi)

            self.planes[takim_numarasi].append_data(entry)

    def add_plane(self, takim_numarasi: int):
        new_plane = Plane(takim_numarasi=takim_numarasi,UI=self.UI,limit=7)
        self.planes[takim_numarasi] = new_plane
        # thread = threading.Thread(target=new_plane.process_data)
        # thread.start()
        # self.threads.append(thread)

#! UI-OPERATIONS
    def add_plane_marker(self,lat,lon,rotation,plane_id):
        self.UI.set_plane(lat=lat,lon=lon,rotation=rotation,plane_id=plane_id,)  
        print(f"ID:{plane_id} -> [lat:{lat} , lon:{lon} , rotation:{rotation} ]")

    def start_ui(self):
        self.UI.start()

#! MAIN
    def main_op(self):

        # self.Yonelim_sunucusu_oluştur()
        # self.Telemetri_sunucusuna_baglan()
        # time.sleep(self.TK_INIT_TIME_SEC)
        # mainloop=False

        # if self.Telem_client_status:
        #     while not mainloop:
        #         telemetri_cevabı = self.ID_Client.client_recv_message()
        #         self.process_data_stream(telemetri_cevabı)
        #         time.sleep(self.TK_INTERVAL_TIME_SEC)

        # #? USER_CODE_END




        #!Testing
        self.anasunucuya_baglan()
        self.connect_mission()
        time.sleep(self.TK_INIT_TIME_SEC)
        mainloop=False

        #? USER_CODE_START
        while not mainloop:
            self.get_plane_data() #self.bizim_veri = get_plane_data
            durum_kodu,telemetri_cevabı = self.ana_sunucu.sunucuya_postala(self.bizim_veri)
            self.process_data_stream(telemetri_cevabı)
            time.sleep(self.TK_INTERVAL_TIME_SEC)

        # #? USER_CODE_END

#!Testing
    def add_plane_for_testing(self,start_lat,start_lon,limit,rotation,plane_id):
        time.sleep(4)
        while limit > 0:
            self.UI.set_marker(lat=start_lat,lon=start_lon,rotation=rotation,plane_id=rotation)
            limit -= 1
            start_lon +=0.010
            rotation += 15
            time.sleep(0.1)
            print("TEST-MARKERS ADDED..")

    def connect_mission(self,port=5762):
        parser = argparse.ArgumentParser()
        parser.add_argument('--connect', default=f'tcp:127.0.0.1:{port}')
        args = parser.parse_args()
        connection_string = args.connect
        self.iha=path.Plane(connection_string)

    def get_plane_data(self):
        self.bizim_veri = {
                    "takim_numarasi": 1,
                    "iha_enlem": self.iha.pos_lat,
                    "iha_boylam": self.iha.pos_lon,
                    "iha_irtifa": self.iha.pos_alt_rel,
                    "iha_dikilme":self.iha.att_pitch_deg,
                    "iha_yonelme": self.iha.att_heading_deg,
                    "iha_yatis": self.iha.att_roll_deg,
                    "iha_hizi": self.iha.airspeed,
                    "zaman_farki": 500}


if __name__ == "__main__":
    tracker=FlightTracker("10.0.0.236") #Yazılım bilgisayarı IP -> 10.0.0.236
    main_op=threading.Thread(target=tracker.main_op)
    main_op.start()
    tracker.start_ui()