import argparse
import ast
import datetime

from vincenty import vincenty

import haberlesme
import detection
import hesaplamalar
import cv2
import threading
import random, json, requests, time
import pyvirtualcam
import GUIRun
import numpy as np
import logging

import path
import resources_rc
import tot4nihai


class YerIstasyonu:
    takim_numarasi_index = []
    host = None
    port_UDP = None
    port_TCP = None
    url = "http://0.0.0.0"  # url is for Main Server
    airspeed = 0
    irtifa = None
    mod = 'kilitlenme'
    iha_mod = 0
    giris_basarili = False
    frame = np.zeros((640, 480, 3), dtype=np.uint8)
    connected = False
    iha = None
    rakip_timer = time.time()
    sunucu_saati = {"gun": 14,
                    "saat": 11,
                    "dakika": 29,
                    "saniye": 4,
                    "milisaniye": 653}
    qr_response = {"qrEnlem": 40.2319867,
                   "qrBoylam": 29.0033913}
    qr_baslangic_zamani = None
    qr_baslangic_zamani_flag = False
    qr_bitis_zamani = None
    qr_bitis_zamani_flag = False
    qr_data_acquired = None
    qr_gorev_basladi = True
    yanit_tel = {"takim_numarasi": 0, "iha_enlem": 1.0, "iha_boylam": 1.0, "iha_irtifa": 1.0, "iha_dikilme": 1.0,
                 "iha_yonelme": 1.0, "iha_yatis": 1.0, "iha_hiz": 1.0, "iha_batarya": 1, "iha_otonom": 1,
                 "iha_kilitlenme": 1, "hedef_merkez_X": 1, "hedef_merkez_Y": 1, "hedef_genislik": 1,
                 "hedef_yukseklik": 1,
                 "gps_saati": {"saat": 1, "dakika": 1, "saniye": 1, "milisaniye": 1}, "mod": "AUTO"}
    """{'takim_numarasi': 4,
     'iha_enlem': 0.0,
     'iha_boylam': 0.0,
     'iha_irtifa': -0.808,
     'iha_dikilme': -22.35449539868347,
     'iha_yonelme': 46.64746337061367,
     'iha_yatis': -1.4423654114208542,
     'iha_hiz': 0.0,
     'iha_batarya': 100,
     'iha_otonom': 0,
     'iha_kilitlenme': 0,
     'hedef_merkez_X': 383,
     'hedef_merkez_Y': 299,
     'hedef_genislik': 26,
     'hedef_yukseklik': 37,
     'gps_saati': {'saat': 0, 'dakika': 0, 'saniye': 0, 'milisaniye': 0}, 'mod': 'kilitlenme'}"""
    pwm_verileri = None
    server_socket_TCP = None
    lock = threading.Lock()

    @classmethod
    def connect(cls, host, port_UDP, port_TCP):
        try:
            logging.basicConfig(level=logging.DEBUG)

            cls.host = host
            cls.port_UDP = port_UDP
            cls.port_TCP = port_TCP

            cls.server_socket_TCP = haberlesme.server_TCP()
            cls.server_socket_UDP = haberlesme.server_UDP()
            # cls.url = "http://10.10.10.2:5000"
            # cls.url = "http://" + GUIRun.GUIRun.ui.lineEditAnaSunucuBaglantiUrl.text()
            cls.url = GUIRun.GUIRun.ui.lineEditAnaSunucuBaglantiUrl.text()
            print("asdada",cls.url)  # arayüzdeki sunucu urlsi bizim cls.urlmiz


            GUIRun.GUIRun.ui.labelBaglanti.setText("Dinleniyor!")
            GUIRun.GUIRun.ui.labelBaglanti.setStyleSheet("background-color: rgb(180,180,0);")
            GUIRun.GUIRun.ui.pushButtonIHABaglan.setEnabled(False)

            cls.server_socket_UDP.baglan(cls.host, cls.port_UDP)
            conn = cls.server_socket_TCP.baglan(cls.host, cls.port_TCP)

            """parser = argparse.ArgumentParser()
            #parser.add_argument('--connect', default=f'udp:{GUIRun.GUIRun.ui.lineEditIHABaglantiUrl.text()}:14550') #Yer İstasyonu IP
            parser.add_argument('--connect', default='udp:169.254.102.128:14550') #Yer İstasyonu IP
            args = parser.parse_args()
    
            connection_string = args.connect
    
            # -- Create the object
            cls.iha = path.Plane(connection_string)"""

            GUIRun.GUIRun.ui.labelBaglanti.setText("Baglanti Kuruldu!")  # GUI'ye IHA ile bağlantı kuruldu yazdırılıyor.
            GUIRun.GUIRun.ui.labelBaglanti.setStyleSheet("background-color: rgb(0,180,0);")

            t1 = threading.Thread(target=YerIstasyonu.telemetriTcp)
            t2 = threading.Thread(target=YerIstasyonu.videoServer)

            t1.start()
            t2.start()
            GUIRun.GUIRun.ui.showVideo()
            return conn

        except Exception as err:
            print("There is an error in \"YerIstasyonu - connect\" with the error: " + str(err))
            return -1

    @classmethod
    def videoServer(cls):
        # cls.url = "http://127.0.0.1:5000"
        # cls.url = "http://10.0.0.15:64559"
        video_recorder = cv2.VideoWriter('video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (640, 480))
        widhtScreen, heightScreen = 640, 480
        cls.pwm_verileri = {'pwmx': 1500, 'pwmy': 1500, 'hiz': 0, 'rakip': 0, 'center': 0, 'x': 0, 'y': 0, 'width': 0,
                            'height': 0}
        qr_gitti = False
        cls.rakip = 0
        kamikaze_sure = []
        kamikaze_first = True
        kilitlenme_first = True
        referenceTime = 0
        # totalTime = 0
        bestLockingTime = 0
        referenceTimeForLocking = 0
        x = 0
        y = 0
        width = 0
        height = 0
        lockedOrNot = 0
        text_color = (100, 10, 150)

        try:
            with pyvirtualcam.Camera(width=widhtScreen, height=heightScreen, fps=30) as cam:
                print(f'Using virtual camera: {cam.device}')

                while True:
                    try:
                        frame = cls.server_socket_UDP.video_al()
                    except ConnectionResetError:
                        raise ConnectionResetError
                    except Exception as err:
                        print("There is an error in \"YerIstasyonu - videoServer - video_al()\" with the error: " + str(
                            err))

                    #cls.mod = cls.yanit_tel['mod']
                    cls.mod = "kilitlenme"

                    if cls.yanit_tel["iha_otonom"] == 1:
                        iha_otonom = True
                    else:
                        iha_otonom = False

                    # print(cam.fps)s
                    # print(type(frame))
                    frame = cv2.resize(frame, (widhtScreen, heightScreen))
                    if cls.mod == 'kilitlenme':
                        kamikaze_sure = []

                        if kilitlenme_first:
                            kilitlenme_first = False
                            kamikaze_first = True
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        results = tot4nihai.Detector.detectorObj.score_frame(frame)
                        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        cls.rakip, center, x, y, width, height, frame, lockedOrNot = tot4nihai.Detector.detectorObj.plot_boxes(
                            results, frame)
                        # cls.rakip, center, x, y, width, height, frame = detection.imageprocessing(frame)

                        if lockedOrNot == 0:
                            referenceTime = time.time()
                            referenceTimeForLocking = time.time()
                            kilitlenmeBaslangicZamani = cls.yanit_tel["gps_saati"]

                        localTotalTime = time.time() - referenceTime
                        localTotalTimeForLocking = time.time() - referenceTimeForLocking

                        try:
                            if localTotalTimeForLocking >= 4.00:
                                kilitlenmeBitisZamani = cls.yanit_tel["gps_saati"]
                                GUIRun.GUIRun.ui.lineEditEnSonGerceklestirilenIHAMod.setText("Kilitlenme")
                                GUIRun.GUIRun.ui.lineEditEnSonGerceklestirilenIHAMod.setStyleSheet(
                                    "background-color: green")
                                GUIRun.GUIRun.ui.lineEditKilitlenmeBaslangicZamani.setText(
                                    str(kilitlenmeBaslangicZamani["saat"]) + ":" + str(
                                        kilitlenmeBaslangicZamani["dakika"]) + ":" + str(
                                        kilitlenmeBaslangicZamani["saniye"]) + ":" + str(
                                        kilitlenmeBaslangicZamani["milisaniye"]))
                                GUIRun.GUIRun.ui.lineEditKilitlenmeBitisZamani.setText(
                                    str(kilitlenmeBitisZamani["saat"]) + ":" + str(
                                        kilitlenmeBitisZamani["dakika"]) + ":" + str(
                                        kilitlenmeBitisZamani["saniye"]) + ":" + str(
                                        kilitlenmeBitisZamani["milisaniye"]))
                                kilitlenme_data = {
                                    "kilitlenmeBaslangicZamani": {"saat": kilitlenmeBaslangicZamani["saat"],
                                                                  "dakika": kilitlenmeBaslangicZamani["dakika"],
                                                                  "saniye": kilitlenmeBaslangicZamani["saniye"],
                                                                  "milisaniye": kilitlenmeBaslangicZamani[
                                                                      "milisaniye"]},
                                    "kilitlenmeBitisZamani": {"saat": kilitlenmeBitisZamani["saat"],
                                                              "dakika": kilitlenmeBitisZamani["dakika"],
                                                              "saniye": kilitlenmeBitisZamani["saniye"],
                                                              "milisaniye": kilitlenmeBitisZamani["milisaniye"]},
                                    "otonom_kilitlenme": 1}

                                durum_kilitlenme = False

                                try:
                                    durum_kilitlenme = cls.server_socket_TCP.kilitlenme_postala(cls.url,
                                                                                                kilitlenme_data)
                                except ConnectionResetError:
                                    raise ConnectionResetError
                                except Exception as err:
                                    print(
                                        "There is an error in \"YerIstasyonu - videoServer - kilitlenme_postala()\" with the error: " + str(
                                            err))

                                print("Kilitlenme Paketi Gönderiliyor")
                                # print(cls.durum(durum_kilitlenme))
                                # totalQrLockingTime = (bitisDateTime - baslangicDateTime).total_seconds()
                                GUIRun.GUIRun.ui.lineEditKilitlenmeSuresi.setText(("4s"))
                                referenceTimeForLocking = time.time()

                        except Exception as err:
                            print(
                                "There is an error in \"YerIstasyonu - videoServer - Kilitlenme Gönderirken veya arayüze yazarkan sorun oluştu!\" with the error: " + str(
                                    err))

                        if localTotalTime > bestLockingTime:
                            bestLockingTime = localTotalTime

                        cv2.putText(frame, str(lockedOrNot), (70, 400), cv2.FONT_HERSHEY_DUPLEX, 1, text_color, 1)
                        cv2.putText(frame, "Kilitlenme Suresi: " + "{:.5f}".format(localTotalTime), (10, 450),
                                    cv2.FONT_HERSHEY_DUPLEX, 0.5, text_color, 1)
                        cv2.putText(frame, "En Iyi Kilitlenme Suresi: " + "{:.5f}".format(bestLockingTime), (10, 470),
                                    cv2.FONT_HERSHEY_DUPLEX, 0.5, text_color, 1)
                        cls.pwm_verileri["rakip"] = cls.rakip
                        cls.pwm_verileri["center"] = center
                        cls.pwm_verileri["x"] = x
                        cls.pwm_verileri["y"] = y
                        cls.pwm_verileri["width"] = width
                        cls.pwm_verileri["height"] = height
                        # print(cls.pwm_verileri)

                    elif cls.mod != "kilitlenme" and cls.mod != "kamikaze":
                        disx1, disx2, disy1, disy2 = int(frame.shape[1] * 0.25), int(frame.shape[1] * 0.75), int(
                            frame.shape[0] * 0.10), int(frame.shape[0] * 0.90)
                        cv2.rectangle(frame, (disx1, disy1), (disx2, disy2), (0, 0, 255), 1)

                    elif cls.mod == 'kamikaze':
                        iha_otonom = True
                        # kamikaze mod
                        try:
                            qr_enlem = cls.qr_response["qrEnlem"]
                            qr_boylam = cls.qr_response["qrBoylam"]
                            ###qr_mesafe = vincenty([cls.yanit_tel["iha_enlem"], cls.yanit_tel["iha_boylam"]], [cls.qr_response["qrEnlem"], cls.qr_response["qrBoylam"]],0)

                            qr_mesafe = hesaplamalar.mesafe_hesapla(
                                [cls.yanit_tel["iha_enlem"], cls.yanit_tel["iha_boylam"]], [qr_enlem, qr_boylam])
                            # print(qr_gidiyor, kalkista, qr_mesafe, cls.iha.pos_alt_rel)
                            # data_controller = False
                            qr_bilgisi, frame = tot4nihai.Detector.detectorObj.qr_detection(frame)
                            print("QR MESAFE:", qr_mesafe)

                            if qr_bilgisi != None:
                                print("lan")
                                cls.qr_data_acquired = str(qr_bilgisi)
                                GUIRun.GUIRun.ui.lineEditQrData.setText(cls.qr_data_acquired)

                            """if qr_mesafe > 0.125:  # QR'I TEKRAR BAŞLATMAK İÇİN GEREKEN MESAFE"""
                            print("125 metre")
                            cls.qr_gorev_basladi = True
                            cls.qr_baslangic_zamani_flag = False
                            cls.qr_bitis_zamani_flag = False

                            if qr_mesafe < 0.1 and cls.qr_baslangic_zamani_flag == False and cls.qr_gorev_basladi == True:  # DALIŞ YAPMAK İÇİN GEREKEN MESAFE
                                # BASLANGIC REFERENCE
                                print("başlangıç referans")
                                cls.qr_baslangic_zamani = cls.yanit_tel["gps_saati"]
                                cls.qr_baslangic_zamani_flag = True
                                GUIRun.GUIRun.ui.lineEditQrBaslangicZamani.setText(
                                    str(cls.qr_baslangic_zamani["saat"]) + ":" + str(
                                        cls.qr_baslangic_zamani["dakika"]) + ":" + str(
                                        cls.qr_baslangic_zamani["saniye"]) + ":" + str(
                                        cls.qr_baslangic_zamani["milisaniye"]))

                            if cls.yanit_tel[
                                "iha_irtifa"] < 50 and cls.qr_bitis_zamani_flag == False and cls.qr_gorev_basladi == True:
                                # BITIS ZAMANI REFERENCE
                                cls.qr_bitis_zamani = cls.yanit_tel["gps_saati"]
                                cls.qr_bitis_zamani_flag = True
                                cls.qr_gorev_basladi = False

                            if cls.qr_data_acquired == None and cls.qr_baslangic_zamani_flag == True and cls.qr_bitis_zamani_flag == True and cls.qr_gorev_basladi == False:
                                GUIRun.GUIRun.ui.lineEditQrData.setText("BASARISIZ")
                                cls.qr_baslangic_zamani_flag = False
                                cls.qr_bitis_zamani_flag = False

                            elif cls.qr_data_acquired != None and cls.qr_baslangic_zamani_flag == True and cls.qr_bitis_zamani_flag == True and cls.qr_gorev_basladi == False:
                                cls.qr_baslangic_zamani_flag = False
                                cls.qr_bitis_zamani_flag = False

                                GUIRun.GUIRun.ui.lineEditEnSonGerceklestirilenIHAMod.setText("Kamikaze")
                                GUIRun.GUIRun.ui.lineEditEnSonGerceklestirilenIHAMod.setStyleSheet(
                                    "background-color: red")
                                GUIRun.GUIRun.ui.lineEditQrBaslangicZamani.setText(
                                    str(cls.qr_baslangic_zamani["saat"]) + ":" + str(
                                        cls.qr_baslangic_zamani["dakika"]) + ":" + str(
                                        cls.qr_baslangic_zamani["saniye"]) + ":" + str(
                                        cls.qr_baslangic_zamani["milisaniye"]))
                                GUIRun.GUIRun.ui.lineEditQrBitisZamani.setText(
                                    str(cls.qr_bitis_zamani["saat"]) + ":" + str(
                                        cls.qr_bitis_zamani["dakika"]) + ":" + str(
                                        cls.qr_bitis_zamani["saniye"]) + ":" + str(
                                        cls.qr_bitis_zamani["milisaniye"]))
                                GUIRun.GUIRun.ui.lineEditQrData.setText(cls.qr_data_acquired)
                                kamikaze_data = {
                                    "kamikazeBaslangicZamani": {"saat": cls.qr_baslangic_zamani["saat"],
                                                                "dakika": cls.qr_baslangic_zamani["dakika"],
                                                                "saniye": cls.qr_baslangic_zamani["saniye"],
                                                                "milisaniye": cls.qr_baslangic_zamani[
                                                                    "milisaniye"]},
                                    "kamikazeBitisZamani": {"saat": cls.qr_bitis_zamani["saat"],
                                                            "dakika": cls.qr_bitis_zamani["dakika"],
                                                            "saniye": cls.qr_bitis_zamani["saniye"],
                                                            "milisaniye": cls.qr_bitis_zamani["milisaniye"]},
                                    "qrMetni": cls.qr_data_acquired}

                                durum_kamikaze = 400

                                try:
                                    durum_kamikaze = cls.server_socket_TCP.kamikaze_gonder(cls.url, kamikaze_data)
                                except ConnectionResetError:
                                    raise ConnectionResetError
                                except Exception as err:
                                    print(
                                        "There is an error in \"YerIstasyonu - videoServer - kamikaze_gonder()\" with the error: " + str(
                                            err))

                                if str(durum_kamikaze)[0] == '2':
                                    print("Kamikaze verisi gönderildi!")
                                    GUIRun.GUIRun.ui.lineEditEnSonGerceklestirilenIHAMod.setText("Kamikaze Başarılı")
                                    GUIRun.GUIRun.ui.lineEditEnSonGerceklestirilenIHAMod.setStyleSheet(
                                        "background-color: green")
                                else:
                                    print("Kamikaze gönderiminde hata!")
                                    GUIRun.GUIRun.ui.lineEditEnSonGerceklestirilenIHAMod.setText("ANA SUNUCU HATA")
                                    GUIRun.GUIRun.ui.lineEditEnSonGerceklestirilenIHAMod.setStyleSheet(
                                        "background-color: red")
                                print(cls.durum(durum_kamikaze))

                        except Exception as err:
                            print(
                                "There is an error in \"YerIstasyonu - videoServer() - Kamikaze\" with the error: " + str(
                                    err))

                    cv2.putText(frame, f"Gorev Modu: {cls.mod}", (10, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, text_color, 1)
                    if iha_otonom:
                        cv2.putText(frame, "IHA Mod: Otonom", (10, 40), cv2.FONT_HERSHEY_DUPLEX, 0.5, text_color, 1)
                    else:
                        cv2.putText(frame, "IHA Mod: Manuel", (10, 40), cv2.FONT_HERSHEY_DUPLEX, 0.5, text_color, 1)
                    if YerIstasyonu.yanit_tel['gps_saati'] is not None:
                        """cv2.putText(frame,
                                    f"GPS Saati: {YerIstasyonu.yanit_tel['gps_saati']['saat']}:{YerIstasyonu.yanit_tel['gps_saati']['dakika']}:{YerIstasyonu.yanit_tel['gps_saati']['saniye']}:{YerIstasyonu.yanit_tel['gps_saati']['milisaniye']}",
                                    (400, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, text_color, 1)"""
                        cv2.putText(frame,
                                    f"Sunucu Saati: {cls.sunucu_saati['saat']}:{cls.sunucu_saati['dakika']}:{cls.sunucu_saati['saniye']}:{cls.sunucu_saati['milisaniye']}",
                                    (400, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, text_color, 1)

                    video_recorder.write(frame)

                    if cls.rakip and cls.airspeed is not None:
                        pwmX, pwmY = hesaplamalar.yonver(x, y, widhtScreen, heightScreen, cls.irtifa)
                        """takip_hiz = hesaplamalar.hizayarla(cls.yanit_tel["iha_hiz"],cls.pwm_verileri["hiz"],width,height)"""
                        # OLU ALAN
                        if x == 320 and y == 240:
                            cls.pwm_verileri["pwmx"] = 1500
                            cls.pwm_verileri["pwmy"] = 1500
                            cls.pwm_verileri["hiz"] = 1500
                        else:
                            cls.pwm_verileri["pwmx"] = pwmX
                            cls.pwm_verileri["pwmy"] = pwmY
                            """cls.pwm_verileri["hiz"] = takip_hiz
                            print(takip_hiz)"""

                    try:
                        # print("gönderiyor",cls.pwm_verileri)
                        cls.server_socket_UDP.mesaj_gonder(cls.pwm_verileri)
                    except Exception as err:
                        print(
                            "There is an error in \"YerIstasyonu - videoServer - mesaj_gonder()\" with the error: " + str(
                                err))

                    cls.frame = frame
                    pyvirtualcam_frame = cv2.cvtColor(cls.frame, cv2.COLOR_RGB2BGR)
                    cam.send(pyvirtualcam_frame)
                    cv2.imshow("framegndrdm", cls.frame)

                    key = cv2.waitKey(1)

                    if key == ord('q'):
                        video_recorder.release()
                        cv2.destroyAllWindows()
                        cls.server_socket_UDP.s.close()
                        break

        except ConnectionResetError as e:
            print(e)
            cls.server_socket_UDP.s.close()
            cls.connected = False
            cls.server_socket_UDP = haberlesme.server_UDP()
            while not cls.connected:
                try:
                    cls.server_socket_UDP.baglan(cls.host, cls.port_UDP)
                    cls.server_socket_UDP.s.settimeout(0.001)
                    cls.connected = True
                except Exception as e:
                    print(e)
                    time.sleep(1)
                    pass
        except Exception as e:
            print(e)

    @classmethod
    def telemetriTcp(cls):
        haberlesme_server_TCP_Obj = haberlesme.server_TCP()
        # st_tst, _ = haberlesme_server_TCP_Obj.sunucuya_postala(cls.url, 'test')

        state_giris = False

        try:
            state_giris = cls.server_socket_TCP.sunucuya_giris(cls.url, 'algan', '53SnwjQ2sQ')
        except ConnectionResetError:
            raise ConnectionResetError
        except Exception as err:
            print("There is an error in \"YerIstasyonu - telemetriTcp- sunucuya_giris()\" with the error: " + str(err))

        print(state_giris, "giriş yapıldı")

        if state_giris[0] == 200:
            giris_basarili = True
            GUIRun.GUIRun.ui.labelAnaSunucuBaglanti.setText(
                "Baglanti Kuruldu!")  # GUI'ye IHA ile bağlantı kuruldu yazdırılıyor.
            GUIRun.GUIRun.ui.labelAnaSunucuBaglanti.setStyleSheet("background-color: rgb(0, 180, 0);")
        else:
            GUIRun.GUIRun.ui.labelAnaSunucuBaglanti.setText(
                "K.adi veya Şifre yanlış!")  # GUI'ye IHA ile bağlantı kuruldu yazdırılıyor.
            GUIRun.GUIRun.ui.labelAnaSunucuBaglanti.setStyleSheet("background-color: rgb(180, 0, 0);")

        qr_response = False

        try:
            cls.qr_state, qr_response = cls.server_socket_TCP.qr_koordinat_al(cls.url)
        except ConnectionResetError:
            raise ConnectionResetError
        except Exception as err:
            print("There is an error in \"YerIstasyonu - telemetriTcp- qr_koordinat_al()\" with the error: " + str(err))

        # print(response, state)

        cls.qr_response = json.loads(qr_response)
        print(cls.qr_response, cls.qr_state)
        qr = [41.01, 29.10]
        cls.rakip_timer = time.time()
        index = 0
        sayac = cls.yanit_tel["gps_saati"]["saniye"]

        while True:
            try:
                try:
                    mesaj = cls.server_socket_TCP.telemetri_al()
                    # print(mesaj)
                    mesaj = json.loads(mesaj)
                    # mesaj = json.loads(mesaj.split("}")[0] + "}}")
                except Exception as err:
                    print("ConnectionResetError: ", err)

                    GUIRun.GUIRun.ui.labelBaglanti.setText("Yeniden Bağlanmaya Çalışılıyor!")
                    GUIRun.GUIRun.ui.labelBaglanti.setStyleSheet("background-color: rgb(180, 180, 0)")
                    cls.server_socket_TCP.s.close()
                    cls.server_socket_TCP = haberlesme.server_TCP()
                    cls.server_socket_TCP.baglan(cls.host, cls.port_TCP)
                    GUIRun.GUIRun.ui.labelBaglanti.setText("Baglanti Tekrar Kuruldu!")
                    GUIRun.GUIRun.ui.labelBaglanti.setStyleSheet("background-color: rgb(0,180,0);")

                    mesaj = cls.yanit_tel

                    print(
                        "There is an error in \"YerIstasyonu - telemetriTcp- telemetri_al()\" with the error: " + str(
                            err))

                try:
                    state_sunucu_saati, response_sunucu_saati = haberlesme_server_TCP_Obj.sunucu_saati_al(cls.url)
                    sunucu_saati = json.loads(response_sunucu_saati)
                    cls.sunucu_saati = sunucu_saati
                except ConnectionResetError:
                    raise ConnectionResetError
                except Exception as err:
                    print(
                        "There is an error in \"YerIstasyonu - telemetriTcp- sunucu_saati_al()\" with the error: " + str(
                            err))

                # print(mesaj)

                json.dumps(mesaj)

                yanit_tel = mesaj  # json.loads(cls.server_socket_TCP.telemetri_al())

                # GPS Saati Datetime formatına çevrilip saat farkı hatası düzeltiliyor.
                datetimeObj = datetime.datetime(year=2023, month=1, day=5, hour=yanit_tel['gps_saati']['saat'],
                                                minute=yanit_tel['gps_saati']['dakika'],
                                                second=yanit_tel['gps_saati']['saniye'],
                                                microsecond=yanit_tel['gps_saati']['milisaniye'])

                timedeltaObj = datetime.timedelta(
                    hours=0)  # Yer istasyonundaki GPS'de zaman farkı yaratman için kullanılır.
                GPSSaatiDateTime = datetimeObj + timedeltaObj

                yanit_tel['gps_saati']['saat'] = GPSSaatiDateTime.hour
                yanit_tel['gps_saati']['dakika'] = GPSSaatiDateTime.minute
                yanit_tel['gps_saati']['saniye'] = GPSSaatiDateTime.second
                yanit_tel['gps_saati'][
                    'milisaniye'] = GPSSaatiDateTime.microsecond  # Gelecekte inceleyenler için; Datetime formatında milisaniye formatı olmadığı için datetime.microsecond attribute'ı kullanılmıştır. Kodun işleyişine şuanlık bir etkisi yok. Düzenleme yaparken dikkatli olun.

                """yanit_tel['gps_saati']['saat'] = sunucu_saati['saat']
                yanit_tel['gps_saati']['dakika'] = sunucu_saati['dakika']
                yanit_tel['gps_saati']['saniye'] = sunucu_saati['saniye']
                yanit_tel['gps_saati']['milisaniye'] = sunucu_saati['milisaniye']"""

                # Orjinal GPS Saati- {'takim_numarasi': 1, 'iha_enlem': -35.3555779, 'iha_boylam': 149.1643982, 'iha_irtifa': 50.6, 'iha_dikilme': -1.8, 'iha_yonelme': 331.22, 'iha_yatis': 38.4, 'iha_hiz': 21.91, 'iha_batarya': 51, 'iha_otonom': 0, 'iha_kilitlenme': 0, 'hedef_merkez_X': 0, 'hedef_merkez_Y': 0, 'hedef_genislik': 0, 'hedef_yukseklik': 0, 'gps_saati': {'saat': 16, 'dakika': 29, 'saniye': 17, 'milisaniye': 656}, 'mod': 'HaberlesmeTest'}

                # print(yanit_tel)

                """with cls.lock:
                    cls.yanit_tel = yanit_tel"""

                cls.yanit_tel = yanit_tel

                # print("Sayac: ", sayac, 'cls.yanit_tel["gps_saati"]["saniye"]', cls.yanit_tel["gps_saati"]["saniye"])

                # print(mesaj)
                # time.sleep(0.05)   Threadler senkron çalışsın diye eklemiştik bir işe yaramadı ŞİMDİLİK

                try:
                    GUIRun.GUIRun.ui.telemetriDataThread()
                except Exception as err:
                    print(f"There is an exception in Yer Istasyonu for calling telemetriDataThread())with: {err}")

                # GUIRun.GUIRun.ui.labelBaglanti.setText("Baglanti Kuruldu2!")
                # GUIRun.GUIRun.ui.labelBaglanti.setStyleSheet("background-color: rgb(0,180,0);")
                if len(cls.yanit_tel) == 0:
                    print('IHA ile baglanti yok')
                    cls.server_socket_TCP = haberlesme.server_TCP()

                    try:
                        cls.server_socket_TCP.baglan(cls.host, cls.port_TCP)
                    except ConnectionResetError:
                        raise ConnectionResetError
                    except Exception as err:
                        print(
                            "There is an error in \"YerIstasyonu - telemetriTcp- baglan()\" with the error: " + str(
                                err))

                    print("Telemetri server yeniden oluşturuldu")
                    continue
                if 'otonom_kilitlenme' in cls.yanit_tel:
                    cls.yanit_tel = ast.literal_eval(str(cls.yanit_tel))
                    # durum_kilitlenme = cls.server_socket_TCP.kilitlenme_postala(cls.url, cls.yanit_tel)

                    try:
                        GUIRun.GUIRun.ui.printKilitlenmeData()
                    except ConnectionResetError:
                        raise ConnectionResetError
                    except Exception as err:
                        print(
                            "There is an error in \"YerIstasyonu - telemetriTcp- printKilitlenmeData()\" with the error: " + str(
                                err))

                    print("Kilitlenme Paketi Gönderiliyor")
                    # print(cls.durum(durum_kilitlenme))
                else:
                    cls.yanit_tel = ast.literal_eval(str(cls.yanit_tel))
                    # mod = cls.yanit_tel['mod']
                    airspeed = cls.yanit_tel["iha_hiz"]
                    irtifa = cls.yanit_tel["iha_irtifa"]
                    iha_mod = cls.yanit_tel["iha_otonom"]
                    gps_saati = cls.yanit_tel["gps_saati"]
                    # del cls.yanit_tel['mod']

                    if cls.yanit_tel["gps_saati"][
                        "saniye"] != sayac:  # GÖKALPE SORULACAK KISIM (cls.rakip verisi bir dict olarak değil, int 1 olarak geliyor.)
                        state = False
                        cls.rakip = False

                        try:
                            state, cls.rakip = haberlesme_server_TCP_Obj.sunucuya_postala(cls.url, cls.yanit_tel)
                        except ConnectionResetError:
                            raise ConnectionResetError
                        except Exception as err:
                            print(
                                "There is an error in \"YerIstasyonu - telemetriTcp- sunucuya_postala()\" with the error: " + str(
                                    err))

                        print("Telemetri Paketi Gönderiliyor")
                        # print(YerIstasyonu.durum(state))
                        cls.rakip = ast.literal_eval(str(cls.rakip))
                        print(cls.rakip)
                        sayac = cls.yanit_tel["gps_saati"]["saniye"]
                        # print(type(cls.rakip))

                        if time.time() - cls.rakip_timer >= 10:

                            rakip_konum = [[i['iha_enlem'], i['iha_boylam'], i['iha_irtifa']] for i in
                                           cls.rakip["konumBilgileri"]]
                            en_uzak = hesaplamalar.en_uzak([cls.yanit_tel["iha_enlem"], cls.yanit_tel["iha_boylam"]],
                                                           rakip_konum)
                            if en_uzak != None:
                                index = rakip_konum.index(en_uzak)

                                if len(cls.takim_numarasi_index) < 2:
                                    cls.takim_numarasi_index.append(index)

                                rakip_timer = time.time()
                                en_uzak_rakip = [cls.rakip["konumBilgileri"][cls.takim_numarasi_index[0]]["iha_enlem"],
                                                 cls.rakip["konumBilgileri"][cls.takim_numarasi_index[0]]["iha_boylam"],
                                                 cls.rakip["konumBilgileri"][cls.takim_numarasi_index[0]]["iha_irtifa"],
                                                 cls.qr_response]
                                print("en_uzak_rakip[2]", en_uzak_rakip[2])

                                if cls.yanit_tel["mod"] != "kilitlenme":
                                    cls.takim_numarasi_index.clear()
                                try:
                                    cls.server_socket_TCP.telemetri_gonder(en_uzak_rakip)
                                except ConnectionResetError:
                                    raise ConnectionResetError
                                except Exception as err:
                                    print(
                                        "There is an error in \"YerIstasyonu - telemetriTcp- telemetri_gonder()\" with the error: " + str(
                                            err))

            except ConnectionResetError or ValueError as err:
                print("ConnectionResetError: ", err)
                GUIRun.GUIRun.ui.labelBaglanti.setText("Yeniden Bağlanmaya Çalışılıyor!")
                GUIRun.GUIRun.ui.labelBaglanti.setStyleSheet("background-color: rgb(180, 180, 0)")
                cls.server_socket_TCP.s.close()
                cls.server_socket_TCP = haberlesme.server_TCP()
                cls.server_socket_TCP.baglan(cls.host, cls.port_TCP)
                GUIRun.GUIRun.ui.labelBaglanti.setText("Baglanti Tekrar Kuruldu!")
                GUIRun.GUIRun.ui.labelBaglanti.setStyleSheet("background-color: rgb(0,180,0);")
            except Exception as err:
                print("There is an error in \"YerIstasyonu - telemetriTcp() method\" with the error: " + str(
                    err))

    @classmethod
    def durum(cls, kod):
        if kod == 200:
            return "İstek başarılı"
        elif kod == 204:
            return "Gonderilen paketin Formati Yanlis"
        elif kod == 400:
            return "Istek hatali veya gecersiz."
        elif kod == 401:
            return "Kimliksiz erisim denemesi. Oturum acmaniz gerekmektedir."
        elif kod == 403:
            return "Yetkisiz erisim denemesi."
        elif kod == 404:
            return "Gecersiz URL."
        elif kod == 500:
            return "Sunucu ici hata."


"""{"takim_numarasi": 4,
 "iha_enlem": 0.0,
 "iha_boylam": 0.0,
 "iha_irtifa": -0.808,
 "iha_dikilme": -22.35449539868347,
 "iha_yonelme": 46.64746337061367,
 "iha_yatis": -1.4423654114208542,
 "iha_hiz": 0.0,
 "iha_batarya": 100,
 "iha_otonom": 0,
 "iha_kilitlenme": 0,
 "hedef_merkez_X": 383,
 "hedef_merkez_Y": 299,
 "hedef_genislik": 26,
 "hedef_yukseklik": 37,
 "gps_saati": {"saat": 0, "dakika": 0, "saniye": 0, "milisaniye": 0}, "mod": "kilitlenme"}
"""
