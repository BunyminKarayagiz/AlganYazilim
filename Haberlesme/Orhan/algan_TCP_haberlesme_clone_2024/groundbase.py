
import datetime
import haberlesme2024_basic
import threading
import json,time
import numpy as np
import logging


class groundBase:

    takim_numarasi_index = []
    host = "0.0.0.0"
    port_TCP = 8888
    port_UDP = None

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
    qr_response = {"qrEnlem": 0.0,
                   "qrBoylam": 0.0}
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

    pwm_verileri = None
    server_socket_TCP = haberlesme2024_basic.server_TCP()
    lock = threading.Lock()

    @classmethod
    def telemetriTcp(cls):
        haberlesme_server_TCP_Obj = haberlesme2024_basic.server_TCP()
        state_giris = False

        try:
            state_giris = cls.server_socket_TCP.enter_server(cls.url, 'algan', '53SnwjQ2sQ')
        except ConnectionResetError:
            raise ConnectionResetError
        except Exception as err:
            print("There is an error in \"YerIstasyonu - telemetriTcp- sunucuya_giris()\" with the error: " + str(err))

        print(state_giris, "giriş yapıldı")

        while True:
            try:
                try:
                    mesaj = cls.server_socket_TCP.get_telemetry()
                    # print(mesaj)
                    mesaj = json.loads(mesaj)

                except Exception as err:
                    print("ConnectionResetError: ", err)

                    cls.server_socket_TCP.skt.close()
                    cls.server_socket_TCP = haberlesme2024_basic.server_TCP()
                    cls.server_socket_TCP.connected(cls.host, cls.port_TCP)

                    mesaj = cls.yanit_tel

                    print(
                        "There is an error in \"YerIstasyonu - telemetriTcp- telemetri_al()\" with the error: " + str(
                            err))

                try:
                    state_sunucu_saati, response_sunucu_saati = haberlesme_server_TCP_Obj.get_servertime(cls.url)
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


                cls.yanit_tel = yanit_tel

                if len(cls.yanit_tel) == 0:
                    print('IHA ile baglanti yok')
                    cls.server_socket_TCP = haberlesme2024_basic.server_TCP()
                    try:
                        cls.server_socket_TCP.connected(cls.host, cls.port_TCP)
                    except ConnectionResetError:
                        raise ConnectionResetError
                    except Exception as err:
                        print(
                            "There is an error in \"YerIstasyonu - telemetriTcp- baglan()\" with the error: " + str(
                                err))

                    print("Telemetri server yeniden oluşturuldu")
                    continue

            except ConnectionResetError or ValueError as err:
                print("ConnectionResetError: ", err)
                cls.server_socket_TCP.skt.close()
                cls.server_socket_TCP = haberlesme2024_basic.server_TCP()
                cls.server_socket_TCP.connected(cls.host, cls.port_TCP)

            except Exception as err:
                print("There is an error in \"YerIstasyonu - telemetriTcp() method\" with the error: " + str(
                    err))

    """def __call__(self):
        logging.basicConfig(level=logging.DEBUG)
        server_socket_TCP = haberlesme2024_basic.server_TCP()
        self.conn = server_socket_TCP.connected(self.host, self.port_TCP)
        t1 = threading.Thread(target=groundBase.telemetriTcp)
        t1.start()
        return self.conn"""

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


yer = groundBase()
yer.telemetriTcp()