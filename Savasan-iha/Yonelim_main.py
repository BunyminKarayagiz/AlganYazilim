from Modules.yonelim_arayuz import App
from Modules import Client_Tcp ,Server_Tcp,Trajectory_estimation
from Modules.Cprint import cp
from Modules import Trajectory_estimation #simple_estimation,advanced_estimation,high_resolution_estimation
import threading,time
from Modules import ana_sunucu_islemleri
import json
from Modules import path_drone as path
import argparse
from typing import Dict,Any
from random import randint
import math
from vincenty import vincenty
#!CLASS OBJ
class Plane:
    def __init__(self, takim_numarasi: int, UI ,data_limit=5,marker_limit = 5,shadow=3):

        self.takim_numarasi = takim_numarasi
        self.data_limit= data_limit
        self.data = []
        self.r , self.g , self.b = (randint(50,255),randint(50,255),randint(50,255))
        self.color = (self.r,self.g,self.b)
        self.UI = UI

        self.marker_limit = marker_limit
        self.marker_list = []

        self.path_limit = marker_limit + shadow
        self.path_list = []
        
        self.polygon_est = None
        self.polygon_est_path = []

        self.path_obj= None
        self.first_two_coord=False
        self.first_lat=0
        self.first_lon=0

        #Tahminleme için kullanılan parametreler
        self.Prediction = []
        self.tahmin=((0,0),(0,0),(0,0),(0,0),(0,0))

    def append_data(self, new_data: Dict[str, Any]):
        if len(self.data) > self.data_limit:
                self.data.pop(0)
        if len(self.marker_list) > self.marker_limit:
                #self.path_obj.remove_position(self.marker_list[0])
                (self.marker_list.pop(0)).delete()
        if len(self.path_list) > self.path_limit: 
                self.path_obj.remove_position(*self.path_list[0])
                self.path_list.pop(0)
        
        self.marker_list.append(self.UI.set_plane(lat=new_data['iha_enlem'],lon=new_data['iha_boylam'],
                                                      rotation=new_data['iha_yonelme'],color_palette=self.color,
                                                      plane_id=self.takim_numarasi))
        
        if self.path_obj == None:
                if self.first_two_coord == True:
                    self.path_obj = self.UI.init_plane_path([(self.first_lat,self.first_lon),(new_data['iha_enlem'],new_data['iha_boylam'])],color_palette=(self.r-50,self.g-50,self.b-50))
                    self.path_list.append((new_data['iha_enlem'],new_data['iha_boylam']))
                else:
                    self.first_lat = new_data['iha_enlem']
                    self.first_lon = new_data['iha_boylam']
                    self.first_two_coord = True
                    self.path_list.append((self.first_lat,self.first_lon))
        else:
                self.path_obj.add_position(new_data['iha_enlem'],new_data['iha_boylam'])
                self.path_list.append((new_data['iha_enlem'],new_data['iha_boylam']))

        a,b,c,d=self.predict_next_position(lat=new_data['iha_enlem'],lon=new_data['iha_boylam'],height=new_data['iha_irtifa'],
                                                          speed=new_data['iha_hizi'],roll_degree=new_data['iha_yatis'],
                                                          pitch_degree=new_data["iha_dikilme"],rotation_yaw=new_data['iha_yonelme'])
        
        self.data.append(new_data)
        return a,b,c,d

    def predict_next_position(self,lat, lon, height, speed, roll_degree,pitch_degree,rotation_yaw):
        if self.Prediction:
            (self.Prediction.pop(0)).delete()
            (self.Prediction.pop(0)).delete()
            (self.Prediction.pop(0)).delete()
            (self.Prediction.pop(0)).delete()

        try:
            a,b,c,d =Trajectory_estimation.final_estimation(lat=lat,lon=lon,height=height,speed=speed,roll_degree=roll_degree,pitch_degree=pitch_degree,rotation_yaw=rotation_yaw)
            self.Prediction.append(self.UI.set_plane(lat=a[0],lon=a[1],rotation=rotation_yaw,color_palette=self.color,plane_id=f"HQ-a"))
            self.Prediction.append(self.UI.set_plane(lat=b[0],lon=b[1],rotation=rotation_yaw,color_palette=self.color,plane_id=f"HQ-b"))
            self.Prediction.append(self.UI.set_plane(lat=c[0],lon=c[1],rotation=rotation_yaw,color_palette=self.color,plane_id=f"HQ-c"))
            self.Prediction.append(self.UI.set_plane(lat=d[0],lon=d[1],rotation=rotation_yaw,color_palette=self.color,plane_id=f"HQ-d"))
        except Exception as e:
            cp.err(f"HQ-Calculation Error ->{e}")

        return a,b,c,d

#!CLASS MAIN
class FlightTracker:
    def __init__(self,Yazılım_ip) -> None:
        
        self.UI=App()

        self.TK_INIT_TIME_SEC = 2
        self.TK_INTERVAL_TIME_SEC = 1

        self.kullanici_adi = "algan"
        self.sifre = "53SnwjQ2sQ"

        self.Algan_ID = "1"
        self.ana_sunucu = ana_sunucu_islemleri.sunucuApi("http://127.0.0.1:5000")
        self.ana_sunucu_status = False

        self.ID_Client=Client_Tcp.Client(Yazılım_ip,9010) #Yazılım bilgisayarından Sunucu_Cevabı alacak Client
        self.TCP_UI_TELEM = Server_Tcp.Server(PORT=9011,name="TELEM-DATA") #Iha'ya yonelim verisini gönderecek Server
        
        self.iha:any
        
        self.planes = {}
        self.threads = []
        self.plane_dict = {}
        self.plane_show_limit = 3
        self.secilen_rakip=""
        self.yonelim_deg_value=50

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
                self.TCP_UI_TELEM.creat_server()
                connection_status=True
                print("IHA_YONELIM : SERVER OLUŞTURULDU\n")
            except (ConnectionError, Exception) as e:
                print("IHA_YONELIM SERVER: oluştururken hata : ", e , " \n")
                print("IHA_YONELIM SERVER: yeniden bağlanılıyor...\n")
                self.TCP_UI_TELEM.reconnect()
                print("IHA_YONELIM : SERVER OLUŞTURULDU\n")
        self.kamikaze_sunucusu = connection_status
        return connection_status

    def receive_telem(self):
        try:
            self.ID_Client.client_recv_message()
        except Exception as e:
            print("TELEM SERVER : Telemetri Receive Error ->",e)

    def send_coord_to_uav(self,coord_data):
        try:
            self.TCP_UI_TELEM.send_data_to_client(coord_data)        
        except Exception as e:
            print("IHA Yonelim : Veri Gönderilirken HATA -> ",e)

    def fark_hesapla(self,ac1, ac2):
        fark = abs(ac1 - ac2)
        if fark > 180:
            fark = 360 - fark
        return fark

    def process_data_stream(self, data_stream: str):
        max_uzaklik=0
        try:
            parsed_data = json.loads(data_stream)["konumBilgileri"]
            for entry in parsed_data:
                takim_numarasi = entry["takim_numarasi"]
                if takim_numarasi not in self.planes:
                    self.add_plane(takim_numarasi)
                    print("YENI UÇAK TESPIT EDILDI -> ",takim_numarasi," ",self.planes)
                a,b,c,d = self.planes[takim_numarasi].append_data(entry)
            if self.secilen_rakip == "":      
                for i in parsed_data:
                    if i["takim_numarasi"] == int(self.Algan_ID):
                        continue
                    
                    fark = abs(i["iha_yonelme"] - parsed_data[int(self.Algan_ID)-1]["iha_yonelme"])
                    if fark > 180:
                        aradaki_fark = 360 - fark
                    else:
                        aradaki_fark = fark

                    if aradaki_fark <= self.yonelim_deg_value:
                        benEnlem_rad = math.radians(parsed_data[int(self.Algan_ID)-1]["iha_enlem"])
                        rakipEnlem_rad = math.radians(i["iha_enlem"])
                        deltaBoylam = math.radians(i["iha_boylam"] - parsed_data[int(self.Algan_ID)-1]["iha_boylam"])
                    
                        # Azimut hesaplama.
                        y = math.sin(deltaBoylam) * math.cos(rakipEnlem_rad)
                        x = math.cos(benEnlem_rad) * math.sin(rakipEnlem_rad) - math.sin(benEnlem_rad) * math.cos(rakipEnlem_rad) * math.cos(deltaBoylam)
                        azimut = math.degrees(math.atan2(y, x))
                        azimut = (azimut + 360) % 360
                        
                        # Azimut ve yön farkı kontrolü
                        yon_farki = self.fark_hesapla(parsed_data[int(self.Algan_ID)-1]["iha_yonelme"], azimut)
                        # Geliştirilmiş kontrol ve çıktı
                        if yon_farki <= 50:  # Burada önümüzdeki rakipler arasındaki en uzaktaki rakibi seçiyoruz. Ve bu bizim yöneleceğimiz rakip olmuş oluyor
                            rakip_konum=(i["iha_enlem"],i["iha_boylam"])
                            uzaklık = vincenty((rakip_konum),(parsed_data[int(self.Algan_ID)-1]["iha_enlem"],parsed_data[int(self.Algan_ID)-1]["iha_boylam"]))
                            if max_uzaklik < uzaklık:
                                max_uzaklik=uzaklık
                                self.secilen_rakip=i # rakibin seçimi burada yapılıyor. for dışında secilen_rakip değişkeni kullanılabilir.
                        else:
                            # Bu kısmı, yön farkı kontrolünden önce sağlayan test kodunu kaldırdık
                            print("RAKİP BULUNAMADI:")
                            self.yonelim_deg_value += 5
                

            print( "SEÇİLEN RAKİP: ", self.secilen_rakip)
        except Exception as e:
            cp.fatal(e)

    def add_plane(self, takim_numarasi: int):
        new_plane = Plane(takim_numarasi=takim_numarasi,UI=self.UI,data_limit=5,marker_limit=5,shadow=5)
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
    def main_op(self,mode):
        print("Current Working Mode : ",mode)

        if mode == "IHA":

            self.Yonelim_sunucusu_oluştur()
            self.Telemetri_sunucusuna_baglan()
            time.sleep(self.TK_INIT_TIME_SEC)
            mainloop=False

            if self.Telem_client_status:
                while not mainloop:
                    telemetri_cevabı = self.ID_Client.client_recv_message()
                    coord_data=self.process_data_stream(telemetri_cevabı)
                    self.send_coord_to_uav(coord_data=coord_data)
                    #time.sleep(self.TK_INTERVAL_TIME_SEC) #!Gerektirse açılabilir..

        if mode == "Monitor":
        #!Testing
            self.anasunucuya_baglan()
            self.connect_mission(port=5762)
            time.sleep(self.TK_INIT_TIME_SEC)
            mainloop=False

            #? USER_CODE_START
            while not mainloop:
                self.get_plane_data() #self.bizim_veri = get_plane_data
                durum_kodu,telemetri_cevabı = self.ana_sunucu.sunucuya_postala(self.bizim_veri)
                self.process_data_stream(telemetri_cevabı)
                time.sleep(self.TK_INTERVAL_TIME_SEC)

        if mode == "UI_TEST":
            time.sleep(2)
            self.add_plane_for_testing(start_lat=52.5164,start_lon=13.3734,limit=20,rotation=10,plane_id="TEST")


#!Testing
    def add_plane_for_testing(self,start_lat,start_lon,limit,rotation,plane_id):
        time.sleep(2)
        r,g,b = (randint(50,255),randint(50,255),randint(50,255))
        path_obj = None
        first_two_coord=False
        curve_multiplier=1
        
        while limit > 0:
            self.UI.set_plane(lat=start_lat,lon=start_lon,rotation=rotation,plane_id=plane_id,color_palette=(r,g,b))
            if path_obj == None:
                if first_two_coord == True:
                    path_obj = self.UI.init_plane_path([(first_lat,first_lon),(start_lat,start_lon)],color_palette=(r-50,g-50,b-50))
                else:
                    first_lat = start_lat
                    first_lon = start_lon
                    first_two_coord = True
            else:
                path_obj.add_position(start_lat,start_lon)
            limit -= 1

            
            lat_increase = 0.005*curve_multiplier
            start_lat += lat_increase

            lon_increase = lat_increase*curve_multiplier
            start_lon += lon_increase

            curve_multiplier +=0.8

            rotation += 10
            #time.sleep(0.1)
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

    Mode = "Monitor" #Monitor / IHA / UI_TEST

    tracker=FlightTracker("10.80.1.73") #Yazılım bilgisayarı IP -> 10.0.0.236
    main_op=threading.Thread(target=tracker.main_op,args=(Mode,))
    main_op.start()
    tracker.start_ui()