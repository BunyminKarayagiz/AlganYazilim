from pymavlink import mavutil
import math

class yonelim:
    def __init__(self):
        self.konum = None
        self.hiz = None
        self.roll = None
        self.pitch = None
        self.yaw = None
        self.iha = None
        self.referans_konum = (37.7409072, 29.0911317)
        self.yonelim_start()

    def connect(self):
        self.iha= mavutil.mavlink_connection('tcp:127.0.0.1:5762')
        return self.iha
    
    def veri_alma(self):
        # ATTITUDE mesajını al
        msg = self.iha.recv_match(type='ATTITUDE', blocking=True)
        if msg is not None and msg.get_type() == 'ATTITUDE':
            roll = msg.roll
            pitch = msg.pitch
            yaw = msg.yaw
        else:
            roll = pitch = yaw = None  # Eğer mesaj alınamazsa None döndür

        # VFR_HUD mesajını al
        msg = self.iha.recv_match(type='VFR_HUD', blocking=True)
        if msg is not None and msg.get_type() == 'VFR_HUD':
            speed = msg.groundspeed
        else:
            speed = None  # Eğer mesaj alınamazsa None döndür

        # GLOBAL_POSITION_INT mesajını al
        msg = self.iha.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        if msg is not None and msg.get_type() == 'GLOBAL_POSITION_INT':
            x = msg.lat / 1e7  # Derece cinsinden enlem
            y = msg.lon / 1e7  # Derece cinsinden boylam
            z = msg.relative_alt / 1000  # Metre cinsinden yükseklik
        else:
            x = y = z = None  # Eğer mesaj alınamazsa None döndür

        roll = math.degrees(roll)
        pitch = math.degrees(pitch)
        yaw = math.degrees(yaw)

        acilar = (roll, pitch, yaw)
        konum = (x, y, z)
        hiz = speed

        return acilar, konum, hiz
    
    def yonelim_start(self):
        self.iha = self.connect()
        if self.iha is not None:
            while True:  # Sürekli veri çekmek için döngü
                acilar, self.konum, self.hiz = self.veri_alma()
                self.roll, self.pitch, self.yaw = acilar

                if self.konum and self.hiz is not None:
                    print(f"Açılar: {acilar}, Konum: {self.konum}, Hız: {self.hiz}")
                else:
                    print("Veri alınamadı.")
        else:
            print("Bağlantı hatası...")

yonelim()