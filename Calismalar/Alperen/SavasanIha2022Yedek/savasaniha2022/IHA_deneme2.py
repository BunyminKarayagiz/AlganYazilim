from multiprocessing.pool import ThreadPool
import path
import time
import argparse
import cv2
import hesaplamalar, haberlesme
import json
from dronekit import LocationGlobalRelative
import datetime
import ast
import os

host = "10.80.1.105"
port = 8888
port2 = 1234

cap_video = cv2.VideoCapture(0)
widhtScreen = 800
heightScreen = 600

zamanlistesi = []
zamanlistesi2 = []

# haberlesme baglanma

iha_haber2 = haberlesme.client_UDP()
udp2 = iha_haber2.baglan(host, port2)

iha_tele = haberlesme.client_TCP()
iha_tele.baglan(host, port)
print("baglandi")

parser = argparse.ArgumentParser()
parser.add_argument('--connect', default='/dev/ttyACM0')
args = parser.parse_args()

connection_string = args.connect

# -- Create the object
iha = path.Plane(connection_string)

def mavlinkrouter():
    os.system('mavproxy.py --master=/dev/ttyACM0,57600 --out=udpbcast:192.168.0.175:14550')
  

circlesayac = []
loiter = 0
#ilk_enlem = iha.pos_lat
#ilk_boylam = iha.pos_lon

datasayac = time.time()
g = time.time()
sure = time.time()
iha_tele.s.settimeout(0.001)
x_right,x_left,y_up,y_down=0,0,0,0
def send_video():
    global x_right,x_left,y_up,y_down
    while True:
        ret, frame = cap_video.read()
        frame = cv2.flip(frame, 1)
        x_right, x_left, y_up, y_down = frame.shape[1] * 0.25, frame.shape[1] * 0.75, frame.shape[0] * 0.10,frame.shape[0] * 0.90
        if ret:
            iha_haber2.video_gonder(frame)
#RECONNECT UDP YAZILACAK

def recv_udp():
    try:
        data = iha_haber2.mesaj_al()
        pwm_verileri=ast.literal_eval(data)
        return pwm_verileri
    except Exception as e:
        pass

def recv_tcp():
    try:
        data = iha_tele.telemetri_al()
        return json.loads(data)
    except Exception as e:
        pass

pool = ThreadPool(processes=4)
rakip=None
pool.apply_async(send_video)
#pool.apply_async(mavlinkrouter)
first=0
qr_gidiyor=False
kalkista=False

while True:
    time.sleep(1)
    try:
        pwm_verileri = pool.apply(recv_udp)
        gelen_rakip_verisi = pool.apply(recv_tcp)
        if gelen_rakip_verisi != None:
            rakip = gelen_rakip_verisi
        if pwm_verileri != None:
            pwm_verileri = ast.literal_eval(pwm_verileri)
        mesaj = iha.mesajlar()
        print(mesaj)
        if time.time() - sure > 0.1:
            sure = time.time()
            if iha.servo6 < 1400 and iha.servo7 > 1600:
                mod="kamikaze"
            else:
                mod="kilitlenme"
                qr_gidiyor=False
                kalkista=False

            if mod == "kamikaze":
                mesaj['IHA_otonom']=1
                if iha.get_ap_mode() != "RTL" and iha.get_ap_mode() != "GUIDED" and iha.get_ap_mode() != "AUTO":
                    iha.set_ap_mode("RTL")
                # kamikaze mod
                try:
                    qr_enlem, qr_boylam = rakip[3][0], rakip[3][1]
                    qr_mesafe = hesaplamalar.mesafe_hesapla([iha.pos_lat, iha.pos_lon], [qr_enlem, qr_boylam])
                    print(qr_gidiyor,kalkista,qr_mesafe,iha.pos_alt_rel)
                    if not qr_gidiyor and not kalkista and qr_mesafe > 0.3 and iha.pos_alt_rel > 100:
                        print('qr_gidiyor')
                        if iha.get_ap_mode() != "GUIDED":
                            iha.set_ap_mode("GUIDED")
                        qr_git = LocationGlobalRelative(qr_enlem, qr_boylam, 100)
                        iha.goto(qr_git)
                        qr_gidiyor = True
                    if qr_mesafe < 0.15 and qr_gidiyor:
                        if iha.get_ap_mode() != "FBWA":
                            iha.set_ap_mode("FBWA")
                        iha.set_rc_channel(1, 1500)
                        iha.set_rc_channel(2, 1100)
                        iha.set_rc_channel(3, 1600)
                    if iha.pos_alt_rel < 50:
                        iha.set_rc_channel(1, 1500)
                        iha.set_rc_channel(2, 1900)
                        iha.set_rc_channel(3, 1600)
                        qr_gidiyor = False
                        kalkista = True
                    if kalkista and iha.pos_alt_rel < 100:
                        print("kalkiyor")
                        iha.set_rc_channel(1, 1500)
                        iha.set_rc_channel(2, 1900)
                        iha.set_rc_channel(3, 1600)
                    if kalkista and iha.pos_alt_rel > 100:
                        print("kalkis bitti rtl")
                        if iha.get_ap_mode() != "RTL":
                            iha.set_ap_mode("RTL")
                        kalkista = False

                except Exception as e:
                    print(e)
            else:
                if pwm_verileri != None and pwm_verileri['rakip']:
                    x, y, width, height = pwm_verileri['center'][0], pwm_verileri['center'][1], pwm_verileri['width'], pwm_verileri['height']
                    mesaj['Hedef_merkez_X']=x
                    mesaj['Hedef_merkez_Y']=y
                    mesaj['Hedef_genislik']=width
                    mesaj['Hedef_yukseklik']=height

                    #FBWA'da kod calisiyor kilitlenme
                    if iha.servo6 > 1700 and iha.servo7 > 1600:
                        mesaj['IHA_otonom'] = 1
                        # KILITLENME SONRASI LOITER
                        if loiter == 1:
                            circlebitis = time.time()
                            circlesayac.append(circlebitis)
                            if circlesayac[-1] - circlesayac[0] >= 10:
                                loiter = 0
                                circlesayac = []
                        else:
                            circlesayac = []
                        if iha.get_ap_mode() != "FBWA" and loiter == 0:
                            iha.set_ap_mode("FBWA")
                        pwmX = pwm_verileri['pwmx']
                        pwmY = pwm_verileri['pwmy']
                        iha.set_rc_channel(1, pwmX)
                        iha.set_rc_channel(2, pwmY)
                        #iha.set_rc_channel(3,1600)

                    # Manuel pilot
                    elif iha.servo6 > 1700 and iha.servo7 < 1600 and iha.servo7 > 1400:
                        mesaj['IHA_otonom'] = 0
                        if iha.get_ap_mode() != "STABILIZE":
                            iha.set_ap_mode("STABILIZE")
                        loiter=0
                        circlesayac = []

                    elif iha.servo6 > 1600 and iha.servo7 < 1400:
                        mesaj['IHA_otonom'] = 1
                        if iha.get_ap_mode() != "RTL":
                            iha.set_ap_mode("RTL")
                        loiter=0
                        circlesayac = []

                    if x_right < x and x + width < x_left and y_up < y and y + height < y_down:
                        zamanlistesi.append(iha.gps_time)
                        if (zamanlistesi[-1] - zamanlistesi[0]).total_seconds() >= 4:
                            print("KILITLENME")
                            baslangic = zamanlistesi[0]
                            bitis = zamanlistesi[-1]
                            kilitlenme = {"kilitlenmeBaslangicZamani": {"saat": baslangic.hour,
                                                                        "dakika": baslangic.minute-4,
                                                                        "saniye": baslangic.second,
                                                                        "milisaniye": baslangic.microsecond//1000},
                                          "kilitlenmeBitisZamani": {"saat": bitis.hour,
                                                                        "dakika": bitis.minute-4,
                                                                        "saniye": bitis.second,
                                                                        "milisaniye": bitis.microsecond//1000},
                                          "otonom_kilitlenme": 1}

                            iha_tele.telemetri_gonder(kilitlenme)
                            loiter = 1
                            zamanlistesi = []
                            print(kilitlenme)
                            iha.set_ap_mode("LOITER")
                            circlebaslangic = time.time()
                            circlesayac.append(circlebaslangic)

                    else:
                        zamanlistesi = []
                    zamanlistesi2 = []
                    first=0
                #Rakip yok
                else:
                    if first==0:
                        iha.set_rc_channel(1, 1500)
                        iha.set_rc_channel(2, 1500)
                        first=1
                    #kamikazemod
                    if iha.servo6 < 1400 and iha.servo7 > 1600:
                        try:
                            qr_enlem, qr_boylam = rakip[3][0], rakip[3][1]
                            qr_mesafe=hesaplamalar.mesafe_hesapla([iha.pos_lat,iha.pos_lon],[qr_enlem,qr_boylam])
                            print(qr_mesafe)
                            if not qr_gidiyor and not kalkista and qr_mesafe > 0.3 and iha.pos_alt_rel>100:
                                print('qr_gidiyor')
                                if iha.get_ap_mode() != "GUIDED":
                                    iha.set_ap_mode("GUIDED")
                                qr_git = LocationGlobalRelative(qr_enlem, qr_boylam, 100)
                                iha.goto(qr_git)
                                qr_gidiyor=True
                            if qr_mesafe < 0.15 and qr_gidiyor:
                                if iha.get_ap_mode() != "FBWA":
                                    iha.set_ap_mode("FBWA")
                                iha.set_rc_channel(1,1500)
                                iha.set_rc_channel(2,1100)
                                iha.set_rc_channel(3,1600)
                            if iha.pos_alt_rel < 50:
                                iha.set_rc_channel(1, 1500)
                                iha.set_rc_channel(2, 1900)
                                iha.set_rc_channel(3, 1600)
                                qr_gidiyor=False
                                kalkista=True
                            if kalkista and iha.pos_alt_rel < 100:
                                print("kalkiyor")
                                iha.set_rc_channel(1, 1500)
                                iha.set_rc_channel(2, 1900)
                                iha.set_rc_channel(3, 1600)
                            if kalkista and iha.pos_alt_rel > 100:
                                print("kalkis bitti rtl")
                                if iha.get_ap_mode() != "RTL":
                                    iha.set_ap_mode("RTL")
                                kalkista=False

                        except Exception as e:
                            print(e)
                    #Yonelim calisiyor
                    if iha.servo6 > 1700 and iha.servo7 > 1600:
                        mesaj['IHA_otonom'] = 1
                        zamanlistesi = []
                        bekle = time.time()
                        zamanlistesi2.append(bekle)
                        if zamanlistesi2[-1] - zamanlistesi2[0] >= 4:
                            print("5 saniye oldu")
                            if iha.get_ap_mode() != 'GUIDED' or iha.get_ap_mode() != 'LOITER':
                                iha.set_ap_mode('LOITER')
                            try:
                                lat, lon, alt = rakip[0], rakip[1], rakip[2]
                                git = LocationGlobalRelative(lat, lon, int(alt))
                                if iha.get_ap_mode() != 'GUIDED':
                                    iha.set_ap_mode('GUIDED')
                                    zamanlistesi2 = []
                                iha.goto(git)
                                zamanlistesi2 = []
                            except Exception as e:
                                print(e)
                                zamanlistesi2 = []
                    #Manuel pilot
                    elif iha.servo6 > 1700 and iha.servo7 < 1600 and iha.servo7 > 1400:
                        mesaj['IHA_otonom'] = 0
                        if iha.get_ap_mode() != 'STABILIZE':
                            iha.set_ap_mode('STABILIZE')
                        zamanlistesi = []
                        loiter = 0
                        circlesayac = []

                    elif iha.servo6 > 1600 and iha.servo7 < 1400:
                        mesaj['IHA_otonom'] = 1
                        if iha.get_ap_mode() != 'RTL' and iha.get_ap_mode() != 'AUTO':
                            iha.set_ap_mode('RTL')
                        zamanlistesi = []
                        loiter = 0
                        circlesayac = []
            mesaj['mod']=mod
            iha_tele.telemetri_gonder(mesaj)
            
    except ConnectionResetError as e:
        print(e)
        iha_tele.s.close()
        connected=False
        iha_tele = haberlesme.client_TCP()
        while not connected:
            try:
                iha_tele.baglan(host, port)
                iha_tele.s.settimeout(0.001)
                connected=True
            except Exception as e:
                print(e)
                time.sleep(1)
                pass
    except Exception as e:
        print(e)









