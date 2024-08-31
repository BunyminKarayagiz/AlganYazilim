from pymavlink import mavutil
import numpy as np
import vincenty
from colorama import Fore, init

referans_konum = (40.2285957, 28.9997649)
init(autoreset=True)

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
        print(Fore.RED + f'ROLL : {roll} PİTCH : {pitch} YAW : {yaw}')
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

def dönüşüm_matrisi(roll, pitch, yaw): #BU MATRİS HATASIZ ŞEKİLDE DÖNÜŞÜM MATRİSİNİ HESAPLIYOR
    R_roll = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]
    ])

    R_pitch = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])

    R_yaw = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1]
    ])

    R = R_yaw @ R_pitch @ R_roll

    return R

# Yerel koordinat sistemindeki vektör
def body_frame_guncelleme(vectors, roll_angle, pitch_angle, yaw_angle):
    R = dönüşüm_matrisi(roll_angle, pitch_angle, yaw_angle)
    vectors = np.array(vectors).T
    new_vectors = R @ vectors

    return new_vectors

# Dünya koordinat sistemindeki vektör
def body2world(vectors, roll, pitch, yaw):
    R = dönüşüm_matrisi(roll, pitch, yaw)
    vectors = np.array(vectors).T
    new_vectors = np.dot(R.T, vectors).T

    return new_vectors

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

def body_to_world(body_vector, yaw):
    """
    Body koordinat sistemindeki vektörü yaw açısını kullanarak world koordinat sistemine dönüştürür.

    Parametreler:
    body_vector (numpy.ndarray): Body koordinat sistemindeki vektör (3x1 sütun vektörü).
    yaw_degrees (float): Yaw açısı (derece cinsinden).

    Dönüş:
    numpy.ndarray: World koordinat sistemindeki vektör (3x1 sütun vektörü).
    """

    # Yaw dönüşüm matrisi oluştur
    R_yaw = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1]
    ])

    # Dönüşüm işlemi
    world_vector = R_yaw @ body_vector

    return world_vector

iha=connect()
while True:
    acilar, konum, hiz=veri_alma(iha)
    body_frame = [hiz, 0, 0]
    roll, pitch, yaw = acilar
    [x, y, z] = nokta_hesapla(konum)
    yeni_vektör = body_frame_guncelleme([20, 0, 0], roll, pitch, yaw)
    print("Yeni Vektör:", yeni_vektör)
    world_vektör=body_to_world(yeni_vektör, yaw)

    #print("WORLD FRAME:", world_vektör)
    #sağa doğru gidince x eksiliyor
    #aşağı doğru gidince x + oluyor
    #sola doğru gidince x yine -19
    #yukarı doğru gidince x yine pozitif ve maximum
    #bir şey deneyeceğim