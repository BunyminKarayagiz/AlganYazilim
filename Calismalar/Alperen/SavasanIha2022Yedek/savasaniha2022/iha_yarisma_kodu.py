from multiprocessing.pool import ThreadPool

from vincenty import vincenty
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

#host = ipConfig.wlan_ip()
host = "169.254.16.34"
port = 8888
port2 = 1234
cap_video = cv2.VideoCapture(0)
widhtScreen = 640
heightScreen = 480

zamanlistesi = []
zamanlistesi2 = []

# haberlesme video udp baglanma
iha_haber2 = haberlesme.client_UDP()
udp2 = iha_haber2.baglan(host, port2)

# haberlesme veri tcp baglanma
iha_tele = haberlesme.client_TCP()
iha_tele.baglan(host, port)
print("baglandi")

parser = argparse.ArgumentParser()
parser.add_argument('--connect', default='/dev/ttyACM0')
args = parser.parse_args()
connection_string = args.connect

"""parser = argparse.ArgumentParser()
parser.add_argument('--connect', default='tcp:127.0.0.1:5762')
args = parser.parse_args()
connection_string = args.connect"""

# -- Tuygun Bağlantı
iha = path.Plane(connection_string)


def mavlinkrouter():
    os.system('mavproxy.py --master=/dev/ttyACM0,57600 --out=udpbcast:169.254.102.128:14550')  # Yer Istasyonu IP


circlesayac = []
loiter = 0
# ilk_enlem = iha.pos_lat
# ilk_boylam = iha.pos_lon


datasayac = time.time()
g = time.time()
sure = time.time()
iha_tele.s.settimeout(0.001)
x_right, x_left, y_up, y_down = 0, 0, 0, 0
mod = "AUTO"

def send_video():
    global x_right, x_left, y_up, y_down, iha_haber2
    # frame = np.zeros((640, 480, 3), dtype=np.uint8)

    while True:
        try:
            ret, frame = cap_video.read()
            frame = cv2.flip(frame, 1)
            # print("Return: ", ret)
            # x_right, x_left, y_up, y_down = frame.shape[1] * 0.25, frame.shape[1] * 0.75, frame.shape[0] * 0.10,frame.shape[0] * 0.90
            if ret:
                iha_haber2.video_gonder(frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    cap_video.release()
                    cv2.destroyeAllWindows()

        except ConnectionResetError as e:
            print("ihada video koptu1:" + str(e))
            iha_haber2.s.close()
            connected = False
            iha_haber2 = haberlesme.client_UDP()
            while not connected:
                try:
                    iha_haber2.baglan(host, port)
                    iha_haber2.s.settimeout(0.001)
                    connected = True
                except Exception as e:
                    print("ihada video koptu2:" + str(e))
                    time.sleep(1)
                    pass
        except Exception as e:
            print("ihada video koptu3:" + str(e))


def recv_udp():
    try:
        data = iha_haber2.mesaj_al()
        pwm_verileri = ast.literal_eval(data)
        return pwm_verileri
    except Exception as e:
        pass


def recv_tcp():
    try:
        data = iha_tele.telemetri_al()
        return json.loads(data)
    except Exception as e:
        pass


def recv_yonel_tcp():
    try:
        data = iha_tele.telemetri_al()
        return json.loads(data)
    except Exception as e:
        pass


pool = ThreadPool(processes=3)
rakip = None
pool.apply_async(send_video)
# pool.apply_async(mavlinkrouter)
first = 0
qr_gidiyor = False
kalkista = False
global speed
speed = 1500
counter_FBWA = time.time()
time_difference_FBWA = 0
hiz_pwm = 1100

def hiz_ayarla(input_value):
    if input_value < 614:
        return 1900
    elif input_value > 122880:
        return 1100
    else:
        return int(1750 - ((input_value - 614) / 120000) * 600)

while True:
    try:
        # gelen_kilit_onay = 0
        pwm_verileri = pool.apply(recv_udp)
        gelen_rakip_verisi = pool.apply(recv_yonel_tcp)
        # gelen_kilit_onay = pool.apply(recv_kilit_onay_tcp)
        # print(gelen_kilit_onay)

        if gelen_rakip_verisi != None:
            rakip = gelen_rakip_verisi
            # print("none ise:",rakip)
        if pwm_verileri != None:
            pwm_verileri = ast.literal_eval(pwm_verileri)
            # print("none değil:",rakip)

        mesaj = iha.mesajlar()
        mesaj['iha_otonom'] = 0

        if time.time() - sure > 0.1:
            sure = time.time()

            # AUTO
            if iha.ch6 > 1600 and iha.ch8 > 1600:  # ch6: High, ch8: High
                mod = 'AUTO'
                mesaj['iha_otonom'] = 1
                if iha.get_ap_mode() != "AUTO":
                    iha.set_ap_mode("AUTO")

            # RTL
            if (iha.ch6 > 1400 and iha.ch6 < 1600) and iha.ch8 > 1600:  # ch6: Mid, ch8: High
                mod = 'RTL'
                mesaj['iha_otonom'] = 1
                if iha.get_ap_mode() != "RTL":
                    iha.set_ap_mode("RTL")

            # FBWA
            if iha.ch6 < 1400 and iha.ch8 > 1600:  # ch6: Low, ch8: High
                mod = "FBWA"
                mesaj['iha_otonom'] = 0
                if iha.get_ap_mode() != "FBWA":
                    iha.set_ap_mode("FBWA")

            # KİLİTLENME
            if iha.ch6 > 1600 and (iha.ch8 > 1400 and iha.ch8 < 1600):  # ch6: High, ch8: Mid
                mod = "kilitlenme"
                mesaj['iha_otonom'] = 1
                time_difference_value_FBWA = 0.5

                """if iha.pos_alt_rel <= 30: #YARIŞMADA AÇILACAK
                    if iha.get_ap_mode() != 'RTL':
                        iha.set_ap_mode('RTL')"""
                if True:
                    # Rakip algılama yok yönelim başlat
                    if not pwm_verileri['rakip']:
                        # Yönelim Başlıyor
                        mesaj['iha_otonom'] = 1
                        zamanlistesi = []
                        bekle = time.time()
                        zamanlistesi2.append(bekle)
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

                    # Ekranda Rakip görüldü Takip başladı
                    if pwm_verileri != None and pwm_verileri['rakip']:
                        reference_instant_time_FBWA = time.time()
                        time_difference_FBWA = reference_instant_time_FBWA - counter_FBWA
                        print(time_difference_FBWA)

                        if pwm_verileri["pwmx"] == 1500 and pwm_verileri["pwmy"] == 1500 and pwm_verileri["rakip"] == 0:
                            counter_FBWA = time.time()

                        x, y, width, height = pwm_verileri['center'][0], pwm_verileri['center'][1], pwm_verileri[
                            'width'], \
                                              pwm_verileri['height']
                        mesaj['hedef_merkez_X'] = x
                        mesaj['hedef_merkez_Y'] = y
                        mesaj['hedef_genislik'] = width
                        mesaj['hedef_yukseklik'] = height
                        mesaj['iha_otonom'] = 1

                        # KILITLENME SONRASI LOITER
                        if loiter == 1:
                            circlebitis = time.time()
                            circlesayac.append(circlebitis)
                            if circlesayac[-1] - circlesayac[0] >= 10:
                                loiter = 0
                                circlesayac = []
                        else:
                            circlesayac = []
                        print(pwm_verileri)

                        if iha.get_ap_mode() != "FBWA" and loiter == 0 and time_difference_FBWA > time_difference_value_FBWA:
                            iha.set_ap_mode("FBWA")
                        pwmX = pwm_verileri['pwmx']
                        pwmY = pwm_verileri['pwmy']
                        iha.set_rc_channel(1, pwmX)
                        iha.set_rc_channel(2, pwmY)
                        rakip_alan = width * height
                        hiz_pwm = hiz_ayarla(int(rakip_alan))
                        print("RAKİP ALAN : ", rakip_alan)
                        print("HIZ PWM : ", hiz_pwm)
                        iha.set_rc_channel(3, hiz_pwm)

                        if x_right < x and x + width < x_left and y_up < y and y + height < y_down:
                            zamanlistesi.append(iha.gps_time)

                            if (zamanlistesi[-1] - zamanlistesi[0]).total_seconds() >= 4:
                                print("KILITLENME")
                                baslangic = zamanlistesi[0]
                                bitis = zamanlistesi[-1]
                                kilitlenme = {"kilitlenmeBaslangicZamani": {"saat": baslangic.hour,
                                                                            "dakika": baslangic.minute - 4,
                                                                            "saniye": baslangic.second,
                                                                            "milisaniye": baslangic.microsecond // 1000},
                                              "kilitlenmeBitisZamani": {"saat": bitis.hour,
                                                                        "dakika": bitis.minute - 4,
                                                                        "saniye": bitis.second,
                                                                        "milisaniye": bitis.microsecond // 1000},
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
                        first = 0
                    else:
                        counter_FBWA = time.time()

            # KAMİKAZE
            if iha.ch6 > 1600 and iha.ch8 < 1400:  # ch6: High, ch8: Low
                mod = "kamikaze"
                mesaj['iha_otonom'] = 1
                try:
                    qr_enlem, qr_boylam = rakip[3]['qrEnlem'], rakip[3]['qrBoylam']
                    # qr_enlem, qr_boylam = -35.3557012, 149.1524076
                    qr_mesafe = vincenty([iha.pos_lat, iha.pos_lon], [qr_enlem, qr_boylam], 100)
                    print("QR MESAFE", qr_mesafe)

                    if not qr_gidiyor and not kalkista and qr_mesafe > 0.2:  # and iha.pos_alt_rel > 100:
                        print('qr_gidiyor')

                        if iha.get_ap_mode() != "GUIDED":
                            iha.set_ap_mode("GUIDED")
                        qr_git = LocationGlobalRelative(qr_enlem, qr_boylam, 100)
                        iha.set_rc_channel(3, 1500)
                        iha.goto(qr_git)
                        qr_gidiyor = True

                    if qr_mesafe < 0.0640 and qr_gidiyor:  # 150 metre
                        if iha.get_ap_mode() != "FBWA":
                            iha.set_ap_mode("FBWA")

                        iha.set_rc_channel(1, 1500)  # Channel 1 is for Roll Input,
                        iha.set_rc_channel(2, 1100)  # Channel 2 is for Pitch Input,
                        iha.set_rc_channel(3, 1100)  # Channel 3 is for Throttle Input,

                    """if iha.pos_alt_rel < 30: #YARIŞMADA AÇILACAK
                        iha.set_rc_channel(1, 1500)
                        iha.set_rc_channel(2, 1900)
                        iha.set_rc_channel(3, 1600)
                        # 169.254.148.157
                        qr_gidiyor = False
                        kalkista = True"""

                    if kalkista and iha.pos_alt_rel < 100:
                        print("kalkiyor")
                        iha.set_rc_channel(1, 1500)
                        iha.set_rc_channel(2, 1900)
                        iha.set_rc_channel(3, 1600)

                    if kalkista and iha.pos_alt_rel > 30:
                        print("kalkis bitti AUTO")
                        if iha.get_ap_mode() != "AUTO":
                            iha.set_ap_mode("AUTO")
                        kalkista = False

                except Exception as e:
                    print("kamikazede problem var:" + str(e))

            mesaj['mod'] = mod
            iha_tele.telemetri_gonder(mesaj)
            #print(mesaj)


    except ConnectionResetError as e:
        print("ihada veri koptu1:" + str(e))
        iha_tele.s.close()
        connected = False
        iha_tele = haberlesme.client_TCP()
        while not connected:
            try:
                iha_tele.baglan(host, port)
                iha_tele.s.settimeout(0.001)
                connected = True
            except Exception as e:
                print("ihada veri koptu2:" + str(e))
                time.sleep(1)
                pass
    except Exception as e:
        print("ihada veri koptu3:" + str(e))
