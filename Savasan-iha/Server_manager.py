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

        #* Servers # IHA:<9000> YONELIM_PC:<11000>
        self.Server_UDP = Server_Udp.Server(PORT=5555,name="IHA-VIDEO") #Görüntü aktarımı
        self.Server_PWM = Server_Tcp.Server(PORT=9001,name="KALMAN-PWM")
        self.Server_TRACK = Server_Tcp.Server(PORT=9002,name="TRACK")
        self.Server_MOD = Server_Tcp.Server(PORT=9003,name="MODE")
        self.Server_KAMIKAZE = Server_Tcp.Server(PORT=9004,name="KAMIKAZE")
        self.Server_CONFIRMATION = Server_Tcp.Server(PORT=9005,name="CONFIRMATION")

        self.Server_UI_VIDEO = Server_Udp.Server(PORT=11000,name="UI-VIDEO")
        self.Server_UI_Telem = Server_Tcp.Server(PORT=11001,name="UI_TELEM")
        self.Server_UI_Control = Server_Tcp.Server(PORT=11002,name="UI-CONTROL")

        #* Server State
        self.ANA_SUNUCU_DURUMU=False
        self.VIDEO_SERVER_STATUS=False
        self.KALMAN_PWM_SERVER_STATUS=False
        self.TRACK_SERVER_STATUS=False
        self.MODE_SERVER_STATUS=False
        self.KAMIKAZE_SERVER_STATUS=False
        self.CONFIRMATION_SERVER_STATUS=False

        self.MAVPROXY_SERVER_STATUS=False

        self.UI_TELEM_SERVER_STATUS=False
        self.UI_VIDEO_SERVER_STATUS=False
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
                    cp.ok(f"Ana Sunucuya Bağlanıldı:{durum_kodu}")  # Ana sunucuya girerkenki durum kodu.
                    connection_status = True
                    self.ana_sunucu_status = connection_status
                else:
                    raise Exception("DURUM KODU '200' DEGIL")
            except Exception as e:
                cp.err(f"ANA SUNUCU : BAGLANTI HATASI -> {e}")

    def CREATE_VIDEO_SERVER(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_UDP.create_server()
                connection_status=True
                cp.ok("VIDEO SERVER : OLUŞTURULDU")
            except (ConnectionError , Exception) as e:
                cp.warn(f"UDP SERVER: oluştururken hata :{e}")
            #    cp.warn("UDP SERVER'A 3 saniye içinden yeniden bağlanılıyor...\n")
            #   self.Server_udp.close_socket()
            #   self.Server_udp = Server_Udp.Server()
            #   self.Server_udp.create_server() #TODO DÜZENLEME GELEBİLİR
        self.VIDEO_SERVER_STATUS = connection_status
        return connection_status

    def CREATE_PWM_SERVER(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_PWM.creat_server()
                connection_status=True
                cp.ok("PWM SERVER : OLUŞTURULDU..")
            except (ConnectionError, Exception) as e:
                cp.warn(f"PWM SERVER: oluştururken hata :{e} \nPWM SERVER: yeniden bağlanılıyor... ")
                self.Server_PWM.reconnect()
                cp.info("PWM : SERVER OLUŞTURULDU...RETRY..")
        self.PWM_sunucusu=connection_status
        return connection_status

    def CREATE_TRACK_SERVER(self):
        connection_status=False
        while not connection_status:
            try:
                connection_status = self.Server_TRACK.creat_server()
                cp.ok("TRACK SERVER : OLUSTURULDU")
            except (ConnectionError, Exception) as e:
                cp.warn(f"TRACK SERVER : OLUSTURULAMADI : {e} \nTRACK SERVER : YENIDEN BAGLANIYOR...")
                connection_status=self.Server_TRACK.reconnect()
                cp.ok("TRACK SERVER: OLUSTURULDU")
        self.TRACK_SERVER_STATUS=connection_status
        return connection_status

    def CREATE_MOD_SERVER(self):
        connection_status=False
        while not connection_status:
            try:
                connection_status = self.Server_MOD.creat_server()
                cp.ok("TRACK SERVER: OLUSTURULDU")
            except (ConnectionError, Exception) as e:
                cp.warn(f"TRACK SERVER: OLUSTURULAMADI : {e}")
                cp.warn("TRACK SERVER: YENIDEM BAGLANIYOR...")
                connection_status=self.Server_MOD.reconnect()
                cp.ok("TRACK SERVER: OLUSTURULDU")
        self.MODE_SERVER_STATUS=connection_status
        return connection_status

    def CREATE_KAMIKAZE_SERVER(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_KAMIKAZE.creat_server()
                connection_status=True
                cp.ok("KAMIKAZE : SERVER OLUŞTURULDU\n")
            except (ConnectionError, Exception) as e:
                cp.warn(f"KAMIKAZE SERVER: oluştururken hata :{e}\nKAMIKAZE SERVER: yeniden bağlanılıyor...")
                self.Server_KAMIKAZE.reconnect()
                cp.info("KAMIKAZE : SERVER OLUŞTURULDU\n")
        self.KAMIKAZE_SERVER_STATUS = connection_status
        return connection_status

    def CREATE_CONFIRMATION_SERVER(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_CONFIRMATION.creat_server()
                connection_status=True
                cp.ok("KONTROL-ONAY : SERVER OLUSTURULDU\n")
            except (ConnectionError, Exception) as e:
                cp.warn(f"KONTROL-ONAY SERVER -> SERVER OLUSTURURKEN HATA :{e}\nKONTROL-ONAY SERVER :YENIDEN BAGLANIYOR...")
                # self.Server_CONFIRMATION.reconnect()
                # cp.info("KONTROL-ONAY SERVER : OLUSTURULDU\n")
        self.CONFIRMATION_SERVER_STATUS = connection_status
        return connection_status

    def CREATE_MAVPROXY_SERVER(self):
        mavlink_obj = SimplifiedTelemetry.Telemetry(Mp_Ip=self.mavlink_ip,Mp_Port=self.mavlink_port,takimNo=self.takim_no)
        connection_status = False
        while not connection_status:
            try:
                mavlink_obj.connect()
                connection_status = True
                cp.ok("MAVLINK SERVER : OLUSTURULDU")
            except (ConnectionError, Exception) as e:
                cp.warn(f"MAVLINK SERVER : OLUSTURURKEN HATA -> {e}\nMAVLINK SERVER : Yeniden baglanılıyor")
                connection_status=mavlink_obj.connect()
                cp.info("MAVLINK : SERVER OLUSTURULDU")
        self.MAVPROXY_SERVER_STATUS=connection_status
        return connection_status,mavlink_obj

    def CREATE_UI_VIDEO_SERVER(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_UI_VIDEO.create_server()
                connection_status=True
                cp.ok("UI SERVER : SERVER OLUŞTURULDU")
            except (ConnectionError , Exception) as e:
                cp.warn(f"UI SERVER : SERVER OLUSTURURKEN HATA -> {e}")
        self.UIframe_sunucusu = connection_status
        return connection_status

    def CREATE_UI_TELEM_SERVER(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_UI_Telem.creat_server()
                connection_status=True
                cp.ok("UI_TELEM : SERVER OLUSTURULDU\n")
            except (ConnectionError, Exception) as e:
                cp.warn(f"UI_TELEM : SERVER OLUSTURURKEN HATA -> {e}\nUI_TELEM : SERVER YENIDEN BAGLANIYOR..")
                # self.Server_UI_telem.reconnect()
                # cp.info("UI_TELEM : SERVER OLUSTURULDU")
        self.UI_telem_sunucusu = connection_status
        return connection_status  

    def SEND_PWM(self,pwm_data):
        try:
            self.Server_PWM.send_data_to_client(pickle.dumps(pwm_data))
        except Exception as e:
            cp.err(f"PWM SERVER SEND ERROR -> {e}")
            #self.KALMAN_PWM_SERVER_STATUS=False
            #self.Server_PWM.reconnect()

    def SEND_FRAME_TO_UI(self,frame): #!Denenmedi...
        try:
            self.Server_UI_Frame.send_frame_to_client(frame)
        except Exception as e:
            cp.warn(f"PWM SUNUCU HATASI : {e}")
            # cp.warn("PWM SUNUCUSUNA TEKRAR BAGLANIYOR.")
            # self.Server_UI_Frame.reconnect()

    def SV_MAIN(self):

        cp.info("Sunucular bekleniyor...")
        t0 = threading.Thread(target=self.anasunucuya_baglan)
        t1 = threading.Thread(target=self.CREATE_VIDEO_SERVER)
        t2 = threading.Thread(target=self.CREATE_PWM_SERVER)
        t3 = threading.Thread(target=self.CREATE_TRACK_SERVER)
        t4 = threading.Thread(target=self.CREATE_MOD_SERVER) #Multiprocess ile uyumlu değil. "yonelim" içine alındı.
        t5 = threading.Thread(target=self.CREATE_KAMIKAZE_SERVER)
        t6 = threading.Thread(target=self.CREATE_CONFIRMATION_SERVER)
        t7 = threading.Thread(target=self.CREATE_MAVPROXY_SERVER)
        t8 = threading.Thread(target=self.CREATE_UI_VIDEO_SERVER)
        t9= threading.Thread(target=self.CREATE_UI_TELEM_SERVER)

        t0.start()
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t5.start()
        t6.start()
        #t7.start()
        t8.start()
        t9.start()

        t0.join()
        return t0,t1,t2,t3,t4,t5,t6,t7,t8,t9

if __name__ == "__main__":
    server_obj = server_manager(mavlink_ip="127.0.0.1",mavlink_port=14550,takimNo=1)
    tuple_obj = server_obj.SV_MAIN()