import time

from pymavlink import mavutil  # gerekli olan kütüphane yüklenir
class MAVProxy:
    def __init__(self):
        self.telemetri = None
        self.mod = None
        self.custom_mode = None
        self.batarya = 0.0
        self.master = 0.0
        self.msg = None
        self.port = None
        self.enlem = 0.0
        self.boylam = 0.0
        self.yukseklik = 0.0
        self.yer_hizi = 0.0
        self.hava_hizi = 0.0
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.mode = None

        self.mode_mapping = {
            0: "MANUAL",
            1: "CIRCLE",
            2: "STABILIZE",
            3: "TRAINING",
            4: "ACRO",
            5: "FBWA",
            6: "FBWB",
            7: "CRUISE",
            8: "AUTOTUNE",
            10: "AUTO",
            11: "RTL",
            12: "LOITER",
            13: "TAKEOFF",
            14: "AVOID_ADSB",
            15: "GUIDED",
            16: "INITIALISING",
            17: "QSTABILIZE",
            18: "QHOVER",
            19: "QLOITER",
            20: "QLAND",
            21: "QRTL",
            22: "QAUTOTUNE",
            23: "QACRO",
            24: "THERMAL"
        }
"""burada öncelikle bağlanacağımız mision plannerdan ctrl-f yaparak açtığımız pencereden mavlink kısmına giriyoruz. oradan tcp host 14550 yi seçip altından da baudrate i seçiyoruz.
uzaktaki bilgisayara bağlanmak istediğimiz için write access kutucuğunu işaretleyip bağlan kısmına tıklıyoruz."""
    def connect(self, port='tcp:10.80.1.31:14550'):
        self.master = mavutil.mavlink_connection(port)


    def veri_kaydetme(self):
        while True:

            self.msg = self.master.recv_match(blocking=True)  # Burada mesajı tanımlıyoruz bu mesajlar bize farklı
            if self.msg.get_type() == 'GPS_RAW_INT':
                self.enlem = self.msg.lat / 10000000
                self.boylam = self.msg.lon / 10000000
            elif self.msg.get_type() == 'GLOBAL_POSITION_INT':
                self.yukseklik = self.msg.relative_alt / 1000
            elif self.msg.get_type() == 'VFR_HUD':
                self.yer_hizi = self.msg.groundspeed
                self.hava_hizi = self.msg.airspeed
            elif self.msg.get_type() == 'SYS_STATUS':
                self.batarya = self.msg.battery_remaining
            elif self.msg.get_type() == 'ATTITUDE':
                self.roll = self.msg.roll
                self.pitch = self.msg.pitch
                self.yaw = self.msg.yaw
            elif self.msg.get_type() == 'HEARTBEAT':
                self.custom_mode = self.msg.custom_mode
                self.mod = self.mode_mapping.get(self.custom_mode, str(self.custom_mode))
            self.telemetri = {
                "Emlen:": float(self.enlem),
                "Boylam": float(self.boylam),
                "Yükseklik": float(self.yukseklik),
                "Yer_Hızı": float(self.yer_hizi),
                "hava hızı": float(self.hava_hizi),
                "roll": float(self.roll),
                "pitch": float(self.pitch),
                "yaw": float(self.yaw),
                "mode": str(self.mod)
            }
            print(self.telemetri)

try:
    maVProxy = MAVProxy()
    maVProxy.connect()
    maVProxy.veri_kaydetme()
except KeyboardInterrupt:
    pass
finally:
    print("görev tamamlandı")
