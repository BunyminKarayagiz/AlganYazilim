from Modules import Server_Tcp,Server_Udp,ana_sunucu_islemleri,SimplifiedTelemetry
from Modules.Cprint import cp
import datetime,json,pickle,threading

class server_manager:
    def __init__(self,mavlink_ip,mavlink_port,takimNo):
        
        cp.ok("Server Manager Working....")
        
        self.kullanici_adi = "algan"
        self.sifre = "53SnwjQ2sQ"
        self.ana_sunucu = ana_sunucu_islemleri.sunucuApi("http://127.0.0.1:5000")
        self.mavlink_ip = mavlink_ip
        self.mavlink_port = mavlink_port
        self.takim_no = takimNo
        
        #* Servers
        self.Server_pwm = Server_Tcp.Server(PORT=9001,name="PWM")
        self.Server_yönelim = Server_Tcp.Server(PORT=9002,name="YÖNELİM")
        self.Server_mod = Server_Tcp.Server(PORT=9003,name="MOD")
        self.Server_kamikaze = Server_Tcp.Server(PORT=9004,name="KAMIKAZE")
        self.Server_UI_telem = Server_Tcp.Server(PORT=9005,name="UI_TELEM")
        self.Server_YKI_ONAY = Server_Tcp.Server(PORT=9006,name="YKI_ONAY")
        self.Server_ID=Server_Tcp.Server(PORT=9010,name="ID")
        self.Server_UIframe = Server_Udp.Server(port=11000,name="UI-Frame")
        self.Server_udp = Server_Udp.Server(port=5555,name="IHA-FRAME")
        
        #* Server States
        self.ana_sunucu_status = False
        self.Yönelim_sunucusu=False
        self.Mod_sunucusu=False
        self.kamikaze_sunucusu=False
        self.UI_telem_sunucusu = False
        self.YKI_ONAY_sunucusu = False
        self.MAV_PROXY_sunucusu=False
        self.görüntü_sunucusu=False
        self.UIframe_sunucusu=False
        self.PWM_sunucusu=False
        self.ID_sunucusu=False
        cp.ok("Server Manager initialized ✓✓✓")

    def senkron_local_saat(self):
        status_code, sunuc_saati = self.ana_sunucu.sunucu_saati_al()
        local_saat = datetime.datetime.today()
        sunuc_saati = json.loads(sunuc_saati)
        sunucu_saat, sunucu_dakika, sunucu_saniye, sunucu_milisaniye = sunuc_saati["saat"], sunuc_saati["dakika"],sunuc_saati["saniye"], sunuc_saati["milisaniye"]
        sunucu_saati = datetime.datetime(year=local_saat.year,
                                         month=local_saat.month,
                                         day=local_saat.day,
                                         hour=sunucu_saat,
                                         minute=sunucu_dakika,
                                         second=sunucu_saniye,
                                         microsecond=sunucu_milisaniye)
        self.fark = abs(local_saat - sunucu_saati)
        cp.info(f"Sunucu Saat Farki: {self.fark}")
        return self.fark

    def anasunucuya_baglan(self):
        connection_status = False
        while not connection_status:
            try:
                "Burada durum kodu işlemin başarı kodunu vermektedir örn:200"
                ana_sunucuya_giris_kodu, durum_kodu = self.ana_sunucu.sunucuya_giris(str(self.kullanici_adi),str(self.sifre))
                if int(durum_kodu) == 200:
                    cp.ok(f"\x1b[{31}m{'Ana Sunucuya Bağlanıldı: ' + durum_kodu}\x1b[0m")  # Ana sunucuya girerkenki durum kodu.
                    self.ana_sunucu_status = True
                    connection_status = self.ana_sunucu_status
                else:
                    raise Exception("DURUM KODU '200' DEGIL")
            except Exception as e:
                cp.err(f"ANA SUNUCU : BAGLANTI HATASI -> {e}")

    def Yönelim_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                connection_status = self.Server_yönelim.creat_server()
                cp.ok("YONELİM : SERVER OLUŞTURULDU")
            except (ConnectionError, Exception) as e:
                cp.warn(f"YÖNELİM SERVER: oluştururken hata : {e}")
                cp.warn("YÖNELİM SERVER: yeniden bağlanılıyor...")
                connection_status=self.Server_yönelim.reconnect()
                cp.ok("YONELİM : SERVER OLUŞTURULDU.")

        self.Yönelim_sunucusu=connection_status
        return connection_status

    def Mod_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_mod.creat_server()
                connection_status=True
                cp.ok("MOD : SERVER OLUŞTURULDU\n")
            except (ConnectionError, Exception) as e:
                cp.warn(f"MOD SERVER: oluştururken hata : {e}")
                cp.warn("MOD SERVER: yeniden bağlanılıyor...\n")
                connection_status=self.Server_pwm.reconnect()
                cp.info("MOD : SERVER OLUŞTURULDU\n")

        self.Mod_sunucusu_sunucusu = connection_status
        return connection_status

    def MAV_PROXY_sunucusu_oluştur(self):
        mavlink_obj = SimplifiedTelemetry.Telemetry(Mp_Ip=self.mavlink_ip,Mp_Port=self.mavlink_port,takimNo=self.takim_no) 
        connection_status = False
        while not connection_status:
            try:
                mavlink_obj.connect()
                connection_status = True
                cp.ok("MAVLINK : SERVER OLUŞTURULDU")
            except (ConnectionError, Exception) as e:
                cp.warn(f"MAVLINK SERVER: oluştururken hata :{e}")
                cp.warn("MAVLINK SERVER: yeniden bağlanılıyor...")
                connection_status=mavlink_obj.connect()
                cp.info("MAVLINK : SERVER OLUŞTURULDU")
        self.MAV_PROXY_sunucusu=connection_status
        return connection_status,mavlink_obj

    def kamikaze_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_kamikaze.creat_server()
                connection_status=True
                cp.ok("KAMIKAZE : SERVER OLUŞTURULDU\n")
            except (ConnectionError, Exception) as e:
                cp.warn(f"KAMIKAZE SERVER: oluştururken hata :{e}")
                cp.warn("KAMIKAZE SERVER: yeniden bağlanılıyor...\n")
                self.Server_kamikaze.reconnect()
                cp.info("KAMIKAZE : SERVER OLUŞTURULDU\n")
        self.kamikaze_sunucusu = connection_status
        return connection_status

    def UI_telem_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_UI_telem.creat_server()
                connection_status=True
                cp.ok("UI_TELEM : SERVER OLUSTURULDU\n")
            except (ConnectionError, Exception) as e:
                cp.warn(f"UI_TELEM : SERVER OLUSTURURKEN HATA : ", e , " \n")
                cp.warn("UI_TELEM : SERVER YENIDEN BAGLANIYOR...\n")
                self.Server_UI_telem.reconnect()
                cp.info("UI_TELEM : SERVER OLUSTURULDU\n")
        self.UI_telem_sunucusu = connection_status
        return connection_status  

    def YKI_ONAY_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_YKI_ONAY.creat_server()
                connection_status=True
                cp.ok("YKI_ONAY : SERVER OLUSTURULDU\n")
            except (ConnectionError, Exception) as e:
                cp.warn(f"YKI_ONAY : SERVER OLUSTURURKEN HATA :{e}")
                cp.warn("YKI_ONAY : SERVER YENIDEN BAGLANIYOR...\n")
                self.Server_YKI_ONAY.reconnect()
                cp.info("YKI_ONAY : SERVER OLUSTURULDU\n")
        self.YKI_ONAY_sunucusu = connection_status
        return connection_status

    def Görüntü_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_udp.create_server()
                connection_status=True
                cp.ok("UDP : SERVER OLUŞTURULDU")
            except (ConnectionError , Exception) as e:
                cp.warn(f"UDP SERVER: oluştururken hata :{e}")
            #    cp.warn("UDP SERVER'A 3 saniye içinden yeniden bağlanılıyor...\n")
            #   self.Server_udp.close_socket()
            #   self.Server_udp = Server_Udp.Server()
            #   self.Server_udp.create_server() #TODO DÜZENLEME GELEBİLİR
        self.görüntü_sunucusu = connection_status
        return connection_status

    def PWM_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_pwm.creat_server()
                connection_status=True
                cp.ok("PWM : SERVER OLUŞTURULDU..")
            except (ConnectionError, Exception) as e:
                cp.warn(f"PWM SERVER: oluştururken hata :{e}")
                cp.warn("PWM SERVER: yeniden bağlanılıyor...")
                self.Server_pwm.reconnect()
                cp.info("PWM : SERVER OLUŞTURULDU..")
        self.PWM_sunucusu=connection_status
        return connection_status

    def ArayuzFrame_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_UIframe.create_server()
                connection_status=True
                cp.ok("UI SERVER : SERVER OLUŞTURULDU")
            except (ConnectionError , Exception) as e:
                cp.warn(f"UI SERVER: oluştururken hata :{e}")
        self.UIframe_sunucusu = connection_status
        return connection_status

    def pwm_gonder(self,pwm_tuple):
        try:
            self.Server_pwm.send_data_to_client(pickle.dumps(pwm_tuple))
        except Exception as e:
            cp.err(f"PWM SUNUCU HATASI :{e}")
            cp.err("PWM SUNUCUSUNA TEKRAR BAGLANIYOR...")
            self.Server_pwm.reconnect()

    def ArayuzFrame_gonder(self,frame): #!Denenmedi...
        try:
            self.Server_UIframe.send_frame_to_client(frame)
        except Exception as e:
            cp.warn(f"PWM SUNUCU HATASI : {e}")
            cp.warn("PWM SUNUCUSUNA TEKRAR BAGLANIYOR...")
            self.Server_pwm.reconnect()

    def ID_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_ID.creat_server()
                connection_status=True
                cp.ok("ID : SERVER OLUŞTURULDU..")
            except (ConnectionError, Exception) as e:
                cp.warn(f"ID : SERVER oluştururken hata :{e}")
                cp.warn("ID : SERVER yeniden bağlanılıyor..")
                self.Server_ID.reconnect()
                cp.info("ID : SERVER OLUŞTURULDU..")
        self.ID_sunucusu = connection_status
        return connection_status

    def sunuculari_oluştur(self):
        self.anasunucuya_baglan()
        self.senkron_local_saat()

        cp.info("Sunucular bekleniyor...")
        t1 = threading.Thread(target=self.Görüntü_sunucusu_oluştur)
        t2 = threading.Thread(target=self.PWM_sunucusu_oluştur)
        t3 = threading.Thread(target=self.Yönelim_sunucusu_oluştur)
        t4 = threading.Thread(target=self.MAV_PROXY_sunucusu_oluştur) #Multiprocess ile uyumlu değil. "yonelim" içine alındı.
        t5 = threading.Thread(target=self.Mod_sunucusu_oluştur)
        t6 = threading.Thread(target=self.kamikaze_sunucusu_oluştur)
        t7 = threading.Thread(target=self.UI_telem_sunucusu_oluştur)
        t8 = threading.Thread(target=self.YKI_ONAY_sunucusu_oluştur)
        t9 = threading.Thread(target=self.ID_sunucusu_oluştur)

        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t5.start()
        t6.start()
        t7.start()
        t8.start()
        t9.start()

        return t1,t2,t3,t4,t5,t6,t7,t8,t9

if __name__ == "__main__":
    server_obj = server_manager(mavlink_ip="127.0.0.1",mavlink_port=5760,takimNo=1)
    tuple_obj = server_obj.sunuculari_oluştur()