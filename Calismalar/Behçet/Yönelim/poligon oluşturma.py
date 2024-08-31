import numpy as np
import vincenty
from pymavlink import mavutil
import time

np.set_printoptions(suppress=True)
#poligonun tepe noktasını bulmak için
referans_konum = (37.7409072, 29.0911317)
def connect():
    iha= mavutil.mavlink_connection('tcp:127.0.0.1:5762')
    return iha

def veri_alma(iha):
    # ATTITUDE mesajını al
    msg = iha.recv_match(type='ATTITUDE', blocking=True)
    if msg is not None and msg.get_type() == 'ATTITUDE':
        roll = msg.roll
        pitch = msg.pitch
        yaw = msg.yaw
    else:
        roll = pitch = yaw = None  # Eğer mesaj alınamazsa None döndür

    # VFR_HUD mesajını al
    msg = iha.recv_match(type='VFR_HUD', blocking=True)
    if msg is not None and msg.get_type() == 'VFR_HUD':
        speed = msg.groundspeed
    else:
        speed = None  # Eğer mesaj alınamazsa None döndür

    # GLOBAL_POSITION_INT mesajını al
    msg = iha.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    if msg is not None and msg.get_type() == 'GLOBAL_POSITION_INT':
        x = msg.lat / 1e7  # Derece cinsinden enlem
        y = msg.lon / 1e7  # Derece cinsinden boylam
        z = msg.relative_alt / 1000  # Metre cinsinden yükseklik
    else:
        x = y = z = None  # Eğer mesaj alınamazsa None döndür

    acilar = (roll, pitch, yaw)
    konum = (x, y, z)
    hiz = speed

    return acilar, konum, hiz

np.set_printoptions(suppress=True, precision=6)

def nokta_hesapla(konum):
    i=konum

    y_ussu = (i[0], referans_konum[1])
    x_ussu = (referans_konum[0], i[1])

    y_mesafe = vincenty.vincenty(y_ussu, referans_konum)
    x_mesafe = vincenty.vincenty(x_ussu, referans_konum)
    # x i negatif yapmak için  boylamının home boylamından küçük olması gerekir

    if i[1] < referans_konum[1]:
        x_mesafe = x_mesafe * -1000
    else:
        x_mesafe = x_mesafe * 1000
    # y i negatif yapmak için enlemi home enleminin altında olması gerekir

    if i[0] < referans_konum[0]:
        y_mesafe = y_mesafe * -1000
    else:
        y_mesafe = y_mesafe * 1000
    nokta = (x_mesafe, y_mesafe, i[2])

    return nokta

def dönüş_yaricapi(v, roll):
    g = 9.81
    return (v ** 2) / (g * np.tan(roll))

def yaw_değişimi(v, r, roll, dt):
    return v *np.tan(roll)/ r * dt

def dairesel_hareket(konum, roll, v, yaw):
    negative=False

    if roll<0:
        negative=True

    roll=np.deg2rad(roll)
    x, y, z = konum

    r = dönüş_yaricapi(v, roll)
    yaw_degisim = yaw_değişimi(v, r, roll, 1)

    yaw += yaw_degisim

    if negative:
        yaw = -yaw

    x +=  v*np.sin(yaw)
    y +=  v*np.cos(yaw)
    z +=  v*np.tan(roll)
    
    return x, y, z

"""x,y,z=dairesel_hareket((0,0,0),30,20)
print(F"X:{x:.4f} Y:{y:.4f} Z:{z:.4f}")
"""

iha = connect()
tahminler = []
konumlar= []
tahminler.append((0,0,0))
yaw_değerleri = []
onceki_zaman = time.time()

while True:

    acilar, konum, hiz = veri_alma(iha)
    nokta=nokta_hesapla(konum)
    konumlar.append(nokta)
    x,y,z=dairesel_hareket(nokta,acilar[0],hiz,acilar[2])
    tahminler.append((x,y,z))
    yaw_değerleri.append(np.rad2deg(acilar[2]))
    print(f"Nokta:X:{nokta[0]:.4f} Y:{nokta[1]:.4f}  Z:{nokta[2]:.4f}       X:{x:.4f} Y:{y:.4f} Z:{z:.4f}")
    if time.time()-onceki_zaman>60:
        break
print(f"Tahminler: {tahminler}\n Konumlar: {konumlar} Yaw Değerleri: {yaw_değerleri}\n")
sözlük= {}

"""
for i in range(len(max(tahminler,konumlar))):
    yaw_değerleri[i]=np.deg2rad(yaw_değerleri[i])
    sözlük[i]={f"{yaw_değerleri[i]}":(konumlar[i]-tahminler[i])}
print(sözlük)
    """