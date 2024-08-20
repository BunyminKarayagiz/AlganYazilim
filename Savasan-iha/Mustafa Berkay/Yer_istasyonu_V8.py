# import numpy as np
# from pyzbar import pyzbar

import av
from Modules import Server_Udp
from Modules import Server_Tcp
# from path import Plane
from Modules import ana_sunucu_islemleri
import threading
import cv2
import pyvirtualcam
import YOLOv8_deploy
import json
import time, datetime
#from Modules import mavproxy2
from Modules import hesaplamalar
from Modules.qr_detection import QR_Detection
import multiprocessing as mp
import numpy as np
import os
from Modules.custom_decorators import perf_counter,debug,memoize
from logging_setup import setup_logging, start_log_listener
from termcolor import cprint
import pickle
from Modules import SimplifiedTelemetry
import numba
import tkinter as tk


#!      SORUNLAR
#!SUNUCU-SAATİ + FARK :                Eksik
#?Yonelim-PWM Değişimi :               Eksik(Çözüldü.)
#?Ana_sunucuya veri gönderimi :        Kusurlu(Çözüldü)
#?Telemetri verilerinin alınması :     Kusurlu(Kısmen çözüldü)
#!Yonelim modunda rakip seçimi:        Eksik
#!Aşırı yönelim(pwm):                   Eksik
#!Hava savunma sistemi:                Eksik
#!Pwm veri doğruluğu:                  Test edilecek
#?Telemetri gönderim sıklığı:           Kusurlu(Çözüldü)
#!Logger                                Kusurlu/Eksik
#!Qr için timeout                       Eksik(İptal edildi.)
#!Kalman ile rota tahmin                Eksik
#?Kalman array için gecikmesi           Kusurlu(Çözüldü)

#! KOD ÇALIŞTIRMA SIRASI: sunucuapi -> Yer_istasyonu_v6 -> Iha_test(PUTTY) -> Iha_haberlesme(PUTTY)
class Yerİstasyonu():

    def __init__(self,mavlink_ip,event_map,SHUTDOWN_KEY,queue_size=1,frame_debug_mode="IHA"): #TODO

        self.kullanici_adi = "algan"
        self.sifre = "53SnwjQ2sQ"
        self.ana_sunucu = ana_sunucu_islemleri.sunucuApi("http://127.0.0.1:5000")
        
        self.yolo_model = YOLOv8_deploy.Detection("C:\\Users\\bunya\\Desktop\\Algan son\\AlganYazilim\\Savasan-iha\\Mustafa Berkay\\Models\\V5_best.pt")
   
        self.Server_pwm = Server_Tcp.Server(PORT=9001,name="PWM")
        self.Server_yönelim = Server_Tcp.Server(PORT=9002,name="YÖNELİM")
        self.Server_mod = Server_Tcp.Server(PORT=9003,name="MOD")
        self.Server_kamikaze = Server_Tcp.Server(PORT=9004,name="KAMIKAZE")
        self.Server_UI_telem = Server_Tcp.Server(PORT=9005,name="UI_TELEM")
        self.Server_YKI_ONAY = Server_Tcp.Server(PORT=9006,name="YKI_ONAY")
        self.Server_ID=Server_Tcp.Server(PORT=9010,name="ID")
        
        self.Server_UIframe = Server_Udp.Server(port=11000,name="UI-Frame")
        self.Server_udp = Server_Udp.Server(port=5555,name="IHA-FRAME")

        self.SHUTDOWN_KEY = SHUTDOWN_KEY

        #Sunucu durumları için kullanılacak değişkenler
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

        self.frame_debug_mode = frame_debug_mode

        #MultiProcess-Mod Objeleri
        self.capture_queue = mp.Queue(maxsize=queue_size)
        self.display_queue = mp.Queue(maxsize=queue_size)
        self.event_map = event_map
        
        #YÖNELİM yapılacak uçağın seçilmesi için kullanılacak obje
        self.yönelim_obj=hesaplamalar.Hesaplamalar()

        #M.PLANNER bilgisayarından telemetri verisi çekmek için kullanılacak obje
        #! MULTIPROCESS ILE ÇAKIŞMA VAR.
        #? yonelim icine tasındı.Yerine mavlink_ip getirildi.      
        #self.mavlink_obj = SimplifiedTelemetry.Telemetry(mavlink_ip) 
        self.mavlink_ip = mavlink_ip

        self.fark = 0
        self.is_qrAvailable = False
        self.is_qr_transmitted = "False"
        self.Yki_onayi_verildi = False
        
        self.qr_coordinat = ""
        self.qr = QR_Detection()

        #GÖREV_MODU SEÇİMİ
        self.event_map = event_map
        self.secilen_görev_modu="kilitlenme"
        self.önceki_mod = ""
        self.sunucu_saati:str = ""

        # Telemetri paketi için PWM'den veriler alınmalı
        self.x_center=0
        self.y_center=0
        self.width=0
        self.height=0
        self.rakip=0

    #! SUNUCU FONKSİYONLARI
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
        print("Sunucu Saat Farki: ", self.fark)
        return self.fark

    def anasunucuya_baglan(self):
        connection_status = False
        while not connection_status:
            try:
                "Burada durum kodu işlemin başarı kodunu vermektedir örn:200"
                ana_sunucuya_giris_kodu, durum_kodu = self.ana_sunucu.sunucuya_giris(str(self.kullanici_adi),str(self.sifre))
                if int(durum_kodu) == 200:
                    print(f"\x1b[{31}m{'Ana Sunucuya Bağlanıldı: ' + durum_kodu}\x1b[0m")  # Ana sunucuya girerkenki durum kodu.
                    self.ana_sunucu_status = True
                    connection_status = self.ana_sunucu_status
                else:
                    raise Exception("DURUM KODU '200' DEGIL")
            except Exception as e:
                print("ANA SUNUCU : BAGLANTI HATASI -> ",e)

    def Yönelim_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_yönelim.creat_server()
                connection_status=True
                print("YONELİM : SERVER OLUŞTURULDU")
            except (ConnectionError, Exception) as e:
                print("YÖNELİM SERVER: oluştururken hata : ", e , " \n")
                print("YÖNELİM SERVER: yeniden bağlanılıyor...\n")
                connection_status=self.Server_yönelim.reconnect()
                print("YONELİM : SERVER OLUŞTURULDU.")

        self.Yönelim_sunucusu=connection_status
        return connection_status

    def Mod_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_mod.creat_server()
                connection_status=True
                print("MOD : SERVER OLUŞTURULDU\n")
            except (ConnectionError, Exception) as e:
                print("MOD SERVER: oluştururken hata : ", e , " \n")
                print("MOD SERVER: yeniden bağlanılıyor...\n")
                connection_status=self.Server_pwm.reconnect()
                print("MOD : SERVER OLUŞTURULDU\n")

        self.Mod_sunucusu_sunucusu = connection_status
        return connection_status

    def MAV_PROXY_sunucusu_oluştur(self):
        mavlink_obj = SimplifiedTelemetry.Telemetry(self.mavlink_ip) 
        connection_status = False
        while not connection_status:
            try:
                mavlink_obj.connect()
                connection_status = True
                print("MAVLINK : SERVER OLUŞTURULDU\n")
            except (ConnectionError, Exception) as e:
                print("MAVLINK SERVER: oluştururken hata : ", e , " \n")
                print("MAVLINK SERVER: yeniden bağlanılıyor...\n")
                connection_status=mavlink_obj.connect()
        self.MAV_PROXY_sunucusu=connection_status
        return connection_status,mavlink_obj

    def kamikaze_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_kamikaze.creat_server()
                connection_status=True
                print("KAMIKAZE : SERVER OLUŞTURULDU\n")
            except (ConnectionError, Exception) as e:
                print("KAMIKAZE SERVER: oluştururken hata : ", e , " \n")
                print("KAMIKAZE SERVER: yeniden bağlanılıyor...\n")
                self.Server_kamikaze.reconnect()
                print("KAMIKAZE : SERVER OLUŞTURULDU\n")
        self.kamikaze_sunucusu = connection_status
        return connection_status

    def UI_telem_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_UI_telem.creat_server()
                connection_status=True
                print("UI_TELEM : SERVER OLUSTURULDU\n")
            except (ConnectionError, Exception) as e:
                print("UI_TELEM : SERVER OLUSTURURKEN HATA : ", e , " \n")
                print("UI_TELEM : SERVER YENIDEN BAGLANIYOR...\n")
                self.Server_UI_telem.reconnect()
                print("UI_TELEM : SERVER OLUSTURULDU\n")
        self.UI_telem_sunucusu = connection_status
        return connection_status  

    def YKI_ONAY_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_YKI_ONAY.creat_server()
                connection_status=True
                print("YKI_ONAY : SERVER OLUSTURULDU\n")
            except (ConnectionError, Exception) as e:
                print("YKI_ONAY : SERVER OLUSTURURKEN HATA : ", e , " \n")
                print("YKI_ONAY : SERVER YENIDEN BAGLANIYOR...\n")
                self.Server_YKI_ONAY.reconnect()
                print("YKI_ONAY : SERVER OLUSTURULDU\n")
        self.YKI_ONAY_sunucusu = connection_status
        return connection_status

    def Görüntü_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_udp.create_server()
                connection_status=True
                print("UDP : SERVER OLUŞTURULDU")
            except (ConnectionError , Exception) as e:
                print("UDP SERVER: oluştururken hata : ", e)
            #    print("UDP SERVER'A 3 saniye içinden yeniden bağlanılıyor...\n")
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
                print("PWM : SERVER OLUŞTURULDU\n")
            except (ConnectionError, Exception) as e:
                print("PWM SERVER: oluştururken hata : ", e , " \n")
                print("PWM SERVER: yeniden bağlanılıyor...\n")
                self.Server_pwm.reconnect()
                print("PWM : SERVER OLUŞTURULDU\n")
        self.PWM_sunucusu=connection_status
        return connection_status

    def ArayuzFrame_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_UIframe.create_server()
                connection_status=True
                print("UI SERVER : SERVER OLUŞTURULDU")
            except (ConnectionError , Exception) as e:
                print("UI SERVER: oluştururken hata : ", e)
        self.UIframe_sunucusu = connection_status
        return connection_status

    def pwm_gonder(self,pwm_tuple):
        try:
            self.Server_pwm.send_data_to_client(pickle.dumps(pwm_tuple))
        except Exception as e:
            print("PWM SUNUCU HATASI : ",e)
            print("PWM SUNUCUSUNA TEKRAR BAGLANIYOR...")
            self.Server_pwm.reconnect()

    def ArayuzFrame_gonder(self,frame): #!Denenmedi...
        try:
            self.Server_UIframe.send_frame_to_client(frame)
        except Exception as e:
            print("PWM SUNUCU HATASI : ",e)
            print("PWM SUNUCUSUNA TEKRAR BAGLANIYOR...")
            self.Server_pwm.reconnect()

    def ID_sunucusu_oluştur(self):
        connection_status=False
        while not connection_status:
            try:
                self.Server_ID.creat_server()
                connection_status=True
                print("ID : SERVER OLUŞTURULDU\n")
            except (ConnectionError, Exception) as e:
                print("ID : SERVER oluştururken hata : ", e , " \n")
                print("ID : SERVER yeniden bağlanılıyor...\n")
                self.Server_ID.reconnect()
                print("ID : SERVER OLUŞTURULDU\n")
        self.ID_sunucusu = connection_status
        return connection_status

    #! KONTROL FONKSİYONU
    def trigger_event(self, event_number, message):
        try:
            if event_number in self.event_map:
                    queue, event = self.event_map[event_number]
                    queue.put(message)
                    event.set()
            else:
                raise ValueError(f"Event_map do not contain {event_number}")
        except Exception as e:
            print("TRIGGER ERROR -> ",e)

    #!FRAME ISLEYEN FONKSIYONLAR
    def qr_oku(self, frame):
        qr_result = self.qr.file_operations(frame=frame)
        return qr_result ,frame

    def capture_frames(self):
        process_name = mp.current_process().name
        cprint(f"Starting Capture-process: {process_name}","green")

        self.Görüntü_sunucusu_oluştur()
        if self.frame_debug_mode == "IHA":
            codec_1 = av.CodecContext.create('h264', 'r')
            frame_id = 0
            while True:
                try:
                    data = self.Server_udp.recv_frame_from_client()
                    packet = av.Packet(data)
                    frames = codec_1.decode(packet)
                    for frame in frames:
                        try:
                            img = frame.to_image()
                            frame = np.array(img)
                            #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            if not self.capture_queue.full():
                                self.capture_queue.put((frame,frame_id))
                                frame_id += 1
                                #print("FRAME :SAVED IN CAPTURE_QUEUE ...")
                            else:
                                #print("FRAME : CAPTURE_QUEUE FULL...")
                                pass
                        except Exception as e:
                            print("FRAME : CAPTURE_QUEUE ERROR -> ",e)
                except Exception as e:
                    print("FRAME : RECEIVE ERROR ->",e)

        elif self.frame_debug_mode == "LOCAL":
            frame_id = 0
            while True:
                try:
                    frame = self.Server_udp.recv_frame_from_client()
                    try:
                        if not self.capture_queue.full():
                            self.capture_queue.put((frame,frame_id))
                            frame_id += 1
                            #print("FRAME :SAVED IN CAPTURE_QUEUE ...")
                        else:
                            #print("FRAME : CAPTURE_QUEUE FULL...")
                            pass
                    except Exception as e:
                        print("FRAME : CAPTURE_QUEUE ERROR -> ",e)
                except Exception as e:
                    print("FRAME : RECEIVE ERROR ->",e)

    def process_frames(self, num):
        process_name = mp.current_process().name
        cprint(f"Starting Frame_Processing process: {process_name}","green")
        event_queue, event_trigger = self.event_map[num]

        # yonelim_queue,yonelim_trigger = self.event_map[4]
        pwm_data_queue,pwm_trigger = self.event_map[5]
        ana_sunucu_queue,sunucu_event = self.event_map[6]
        lock_once_event,qr_once_event = self.event_map[7]
        lock_outer_event,qr_outer_event = self.event_map[8]

        lockedOrNot = 0
        locked_prev = 0
        event_message = ""
        is_locked = 0
        sent_once = 0

        while True:
            if event_trigger.is_set():
                time.sleep(0.01)
                event_message = event_queue.get()
                cprint(f"{process_name} received event: {event_message}","red")
                event_trigger.clear()

            if not self.capture_queue.empty():
                (frame,frame_id) = self.capture_queue.get()
                #print(f"{process_name} -> ",frame_id)

                if event_message == "kilitlenme":
                    pwm_tuple, processed_frame, lockedOrNot = self.yolo_model.model_predict(frame=frame,frame_id=frame_id)
                    # Burada pwm_tuple dan çekilen veriler telemetri paketinin içinde kullanılacak şekilde düzenlenmeli
                    self.rakip= pwm_tuple[3]
                    self.x_center =pwm_tuple[4]
                    self.y_center = pwm_tuple[5]
                    self.width =  pwm_tuple[6]
                    self.height = pwm_tuple[7]

                    #* 4 SANIYE-KILITLENME
                    if lockedOrNot == 1 and locked_prev == 0:
                            lock_start_time=time.perf_counter()
                            start_now =datetime.datetime.now()
                            cv2.putText(img=processed_frame,text="HEDEF GORULDU",org=(50,400),fontFace=1,fontScale=2,color=(0,255,0),thickness=2)
                            locked_prev=1

                    #Hedef Görüldü. Yönelim modu devre dışı.
                            self.trigger_event(4,"STOP")
                            pwm_data_queue.put(pwm_tuple)
                            #pwm_trigger.set()


                    if lockedOrNot == 0 and locked_prev== 1:
                            cv2.putText(img=processed_frame,text="HEDEF KAYBOLDU",org=(50,400),fontFace=1,fontScale=2,color=(0,255,0),thickness=2)
                            locked_prev= 0
                            is_locked= 0
                            sent_once = 0

                    #Hedef kayboldu. Yönelim Moduna geri dön. Pwm modunu kapat
                            self.trigger_event(4,"yonelim")
                            #pwm_trigger.clear()

                    if lockedOrNot == 1 and locked_prev== 1:
                            lock_elapsed_time= time.perf_counter() - lock_start_time
                            cv2.putText(img=processed_frame,text=str(round(lock_elapsed_time,3)),org=(50,370),fontFace=1,fontScale=1.5,color=(0,255,0),thickness=2)

                            """if is_locked == 0:
                                cv2.putText(img=processed_frame,text="KILITLENIYOR",org=(50,400),fontFace=1,fontScale=1.8,color=(0,255,0),thickness=2)"""
                                  

                            if lock_elapsed_time >= 4.0:
                                cv2.putText(img=processed_frame,text="KILITLENDI",org=(50,400),fontFace=1,fontScale=1.8,color=(0,255,0),thickness=2)
                                kilitlenme_bilgisi=True
                                is_locked=1
                                self.trigger_event(4,"yonelim")
                                #pwm_trigger.clear()
                                
                    if pwm_tuple[0] != 1500 or pwm_tuple[1] != 1500: #pwm_tuple -> [0]=pwmx , [1]=pwmy
                        self.trigger_event(5,pwm_tuple)
                    # #Kilitlenme gerçekleşti. Yönelim moduna geri dön.
                        
                    if is_locked == 1 and sent_once == 0:
                            end_now = datetime.datetime.now()
                            kilitlenme_bilgisi = {
                                "kilitlenmeBaslangicZamani": {
                                    "saat": start_now.hour,
                                    "dakika": start_now.minute,
                                    "saniye": start_now.second,
                                    "milisaniye": start_now.microsecond #TODO düzeltilecek
                                },
                                "kilitlenmeBitisZamani": {
                                    "saat": end_now.hour,
                                    "dakika": end_now.minute,
                                    "saniye": end_now.second,
                                    "milisaniye": end_now.microsecond #TODO düzeltilecek
                                },
                                "otonom_kilitlenme": 0
                            }
                            print(kilitlenme_bilgisi)
                            kilitlenme_bilgisi = json.dumps(kilitlenme_bilgisi)
                            print("KİLİTLENME BAŞARILI\nKİLİTLENME BAŞARILI\nKİLİTLENME BAŞARILI\nKİLİTLENME BAŞARILI\n")
                            lock_once_event.set()
                            #if lock_once_event.is_set() and (not lock_outer_event.is_set()):
                            if lock_once_event.is_set():
                                self.trigger_event(6,(kilitlenme_bilgisi,"kilitlenme"))
                                lock_once_event.clear()

                    if not self.display_queue.full():
                        self.display_queue.put(processed_frame)

                elif event_message == "kamikaze":
                    qr_text,processed_frame = self.qr_oku(frame)
                    
                    # if qr_text != None :
                    #     qr_once_event.set()
                    # elif qr_text == None:
                    #     qr_once_event.clear()
                        
                    #if qr_once_event.is_set() and (not qr_outer_event.is_set()):
                    # if qr_once_event.is_set():
                    #     self.trigger_event(6,(qr_text,"qr"))
                    if qr_text != None :
                        self.trigger_event(6,(qr_text,"qr"))


                    if not self.display_queue.full():
                        self.display_queue.put(processed_frame)
                elif event_message == "AUTO" or event_message == "FBWA" or event_message == "RTL":
                    if not self.display_queue.full():
                        self.display_queue.put(frame)

                else:
                    print("Process_frame :INVALID MODE...")
                    time.sleep(0.5)

    def display_frames(self):
        process_name = mp.current_process().name
        cprint(f"Starting Display process: {process_name}","green")
        event_message=""
        display_process_queue,display_process_event = self.event_map[10]
        arayuz_frame_queue , arayuz_telem_queue=self.event_map[9]
        
        fourrcc = cv2.VideoWriter_fourcc(*'MP4V')
        videoKayit = cv2.VideoWriter('video.mp4', fourrcc, 30.0, (640, 480))
        
        is_stream_available = False
        frame_count:float= 0.0
        fps:float = 0.0
        with pyvirtualcam.Camera(width=640,height=480,fps=30) as cam:
            while True:
                if not self.display_queue.empty():
                    if not is_stream_available:
                        fps_start_time = time.perf_counter()
                        is_stream_available = True

                    frame = self.display_queue.get() #TODO EMPTY Queue blocking test?
                    now = datetime.datetime.now()
                    virtual_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    current_time = now.strftime("%H:%M:%S") + f".{now.microsecond//1000:03d}"
                    cv2.putText(frame,"SUNUCU : "+current_time , (420, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 128, 0), 2)
                    cv2.putText(frame, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 128, 0), 2)
                    videoKayit.write(frame)    
                    if not arayuz_frame_queue.full():
                        arayuz_frame_queue.put(frame)
                    cam.send(frame= virtual_frame)
                    cv2.imshow('Camera', frame)
                    fps = frame_count / (time.perf_counter() - fps_start_time)
                    frame_count += 1.0
                else:
                    pass

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                if display_process_event.is_set():
                    time.sleep(0.01)
                    event_message = display_process_queue.get()
                    cprint(f"{process_name} received event: {event_message}","red")
                    display_process_event.clear()

                if event_message=="stop_capture":
                    videoKayit.release()


        videoKayit.release()
        cv2.destroyAllWindows()

    def kalman_predict(self,kalman_buffer,buffer_size=5):
    
        #! Kalman burada uygulanacak

        return kalman_buffer[0]

    #! KİLİTLENME MODUNDA ÇALIŞACAK FONKSİYONLAR
    def yonelim_gonder(self,hedef): #TODO Yeniden bağlanma durumları kontrol edilecek...
        try:
            self.Server_yönelim.send_data_to_client(json.dumps(hedef).encode())
        except Exception as e:
            print("YONELİM : VERİ GÖNDERİLİRKEN HATA --> ",e)
            print("YONELİM YENİDEN BAĞLANIYOR...")
            self.Server_yönelim.reconnect()

    def rakip_sec(self,bizim_telemetri,rakip_telemetri): #? Ekleme yapılabilir...
            try:
                secilen_rakip= self.yönelim_obj.rakip_sec(rakip_telemetri,bizim_telemetri) 
                secilen_rakip = 0
                return secilen_rakip
            except Exception as e:
                print("YONELİM: TELEMETRİ ALINIRKEN HATA --> ",e)

    #! KAMİKAZE MODUNDA ÇALIŞACAK FONKSİYONLAR
    def get_qrCoord(self,timeout=1): #TODO Timeout özelliği eklenecek...
        if self.is_qrAvailable == True:
            try:
                _, self.qr_coordinat = self.ana_sunucu.qr_koordinat_al()
                print("QRKONUM :",self.qr_coordinat)
                self.is_qrAvailable = True
                return self.qr_coordinat
            except Exception as e :
                print("KAMIKAZE : SUNUCUDAN QR-KONUM ALINIRKEN HATA -> ",e)
                #TODO EKLEME YAPILACAK

    def kamikaze_time_recv(self):
        print("Waiting for kamikaze_time_packet")
        time.sleep(1)
        while True:
            try:
                self.kamikaze_packet=self.Server_kamikaze.recv_tcp_message()
                print(self.kamikaze_packet)
                print("Kamikaze_start received...")
            except Exception as e:
                print("Kamikaze_start ERROR :",e)

    #! ANA FONKSİYONLAR
    def sunuculari_oluştur(self):
        self.anasunucuya_baglan()
        self.senkron_local_saat()

        print("Sunucular bekleniyor...")
        t1 = threading.Thread(target=self.Görüntü_sunucusu_oluştur) # YKI_PROCESS  içinde kullanıldı.
        t2 = threading.Thread(target=self.PWM_sunucusu_oluştur) # YKI_PROCESS  içinde kullanıldı.
        t3 = threading.Thread(target=self.Yönelim_sunucusu_oluştur)
        t4 = threading.Thread(target=self.MAV_PROXY_sunucusu_oluştur) #Multiprocess ile uyumlu değil. "yonelim" içine alındı.
        t5 = threading.Thread(target=self.Mod_sunucusu_oluştur)
        t6 = threading.Thread(target=self.kamikaze_sunucusu_oluştur)
        t7 = threading.Thread(target=self.UI_telem_sunucusu_oluştur) # UI_TELEM içine taşındı.
        t8 = threading.Thread(target=self.YKI_ONAY_sunucusu_oluştur)
        t9 = threading.Thread(target=self.ID_sunucusu_oluştur)

        #t1.start()
        #t2.start()
        t3.start()
        #t4.start()
        t5.start()
        t6.start()
        #t7.start()
        t8.start()
        t9.start()

        t5.join()
        return t1,t2,t3,t4,t5,t6,t7,t8,t9

    def yki_onay_ver(self):
        if self.YKI_ONAY_sunucusu:
            if self.Yki_onayi_verildi == False:
                self.Server_YKI_ONAY.send_data_to_client("ALGAN".encode())
                self.Yki_onayi_verildi = True
                cprint(f"ONAY VERILDI ---> {self.Yki_onayi_verildi}","red","on_white", attrs=["bold"])
            else:
                self.Server_YKI_ONAY.send_data_to_client("RED".encode())
                self.Yki_onayi_verildi = False
                cprint(f"ONAY REDDEDILDI ---> {self.Yki_onayi_verildi}","red","on_white", attrs=["bold"])
        else:
            cprint(f"YKI ONAY : SUNUCU KAPALI / MEVCUT ONAY DURUMU --> {self.Yki_onayi_verildi}","red","on_white", attrs=["bold"])
            return False

    def yonelim(self,num=4):
        ret,mavlink_obj=self.MAV_PROXY_sunucusu_oluştur()
        
        event_queue,event_trigger = self.event_map[num]
        event_message = ""
        timer_start = time.perf_counter()

        while True:
            if event_trigger.is_set():
                time.sleep(0.01)
                event_message = event_queue.get()
                print("Yonelim received event : ",event_message)
                event_trigger.clear()
            try:
                bizim_telemetri,ui_telemetri=mavlink_obj.telemetry_packet()
                # bizim_telemetri = {"takim_numarasi": 1, "iha_enlem": 0,"iha_boylam":0,"iha_irtifa": 0,"iha_dikilme":0,
                #                    "iha_yonelme":0,"iha_yatis":0,"iha_hiz":0,"iha_batarya":0,"iha_otonom": 1,
                #                    "iha_kilitlenme": 1,"hedef_merkez_X": 300,"hedef_merkez_Y": 230,"hedef_genislik": 30,
                #                    "hedef_yukseklik": 43,"gps_saati": {"saat": time.gmtime().tm_hour,
                #                                                        "dakika": time.gmtime().tm_min,
                #                                                        "saniye": time.gmtime().tm_sec,
                #                                                        "milisaniye": int((time.time() % 1) * 1000)
                #                                                        }
                #                     }
                #arayüze gidecek telemetri eklenecek.

                if bizim_telemetri is not None:
                    if time.perf_counter() - timer_start > 1 :
                        rakip_telemetri=self.ana_sunucu.sunucuya_postala(bizim_telemetri) #TODO Telemetri 1hz olmalı...
                        try:
                            if not self.ID_sunucusu:
                                self.Server_ID.send_data_to_client(rakip_telemetri)
                        except Exception as e:
                            print("ID : DATA SENDING ERROR -> ",e)
                        timer_start=time.perf_counter()

            except Exception as e:
                print("TELEMETRI : VERI HATASI -> ",e)

                if event_message == "yonelim":
                    if not bizim_telemetri == None:
                        self.yonelim_gonder( (self.rakip_sec(bizim_telemetri,rakip_telemetri),"yonelim") ) #? Rakip-Kontrol ayrı yapılabilir.

                elif event_message == "qr":
                    #if not self.is_qrAvailable and self.is_qr_transmitted == "False" :
                        self.yonelim_gonder(self.get_qrCoord())
                        self.is_qr_transmitted=self.Server_yönelim.recv_tcp_message()
                        print("Is QR transmitted : ",self.is_qr_transmitted)
                    #else:
                        print("Qr already available",self.qr_coordinat)

            time.sleep(0.01) #? GEÇİCİ

    def UI_TELEM(self): #Denenmedi
        _ , arayuz_telem_queue = self.event_map[9]
        t7 = threading.Thread(target=self.UI_telem_sunucusu_oluştur)
        t7.start()
        while True:
            if self.UI_telem_sunucusu:
                if not arayuz_telem_queue.empty():
                    telemetri=arayuz_telem_queue.get()
                    #Verileri bölme işi arayüz kodunda yapılacak.
                    if not telemetri == None:
                        self.Server_UI_telem.send_data_to_client(telemetri)

    def UI_FRAME(self):
        self.ArayuzFrame_sunucusu_oluştur()
        (arayuz_frame_queue,arayuz_telem_queue) =self.event_map[9]
        if not arayuz_frame_queue.empty():
            try:
                frame = self.arayuz_frame_queue.get()
                resized_frame = cv2.resize(frame, (480,320), interpolation=cv2.INTER_AREA)
                _, encoded_frame = cv2.imencode('.jpg', resized_frame) #TODO Bu komuta ihtiyaç olmayabilir.
                self.ArayuzFrame_gonder(encoded_frame)
            except Exception as e:
                print("UI_FRAME :",e)

    def PWM(self):
        self.PWM_sunucusu_oluştur()
        pwm_data_queue, pwm_trigger = self.event_map[5] 

        stored_packets = [0,0,0,0,0,0,0,0]
        packet_counter = 0
        while True:
            if not pwm_data_queue.empty():
                pwm_tuple= pwm_data_queue.get()
                stored_packets[packet_counter]=pwm_tuple
                packet_counter +=1

                if packet_counter == 5:
                    packet_counter = 0
                    print("Packet Ready:\n",stored_packets,"\n")
                    self.pwm_gonder(pwm_tuple=self.kalman_predict(kalman_buffer=stored_packets,buffer_size=5))
                    stored_packets = [0,0,0,0,0,0,0,0]

    def ana_sunucu_manager(self,num=6):
        event_queue,event_trigger = self.event_map[num]
        lock_once_event,qr_once_event = event_map[7]
        lock_outer_event,qr_outer_event = event_map[8]
        gorev_bilgisi = None

        qr_sent_once = False
        lock_sent_once = False
        

        qr_timer = time.perf_counter()
        lock_timer = time.perf_counter()
        
        th1= threading.Thread(target=self.kamikaze_time_recv)
        th1.daemon = True
        th1.start()

        while True:
            if event_trigger.is_set():
                time.sleep(0.01)
                gorev_bilgisi,Type = event_queue.get()
                print(Type)
                if Type == "qr":
                    cprint(f"QR:{gorev_bilgisi}","blue")
                    if not qr_sent_once:
                        self.ana_sunucu.sunucuya_postala(gorev_bilgisi)
                        qr_sent_once = True
                if Type == "kilitlenme":
                    cprint(f"LOCK:{gorev_bilgisi}","blue")
                    if not lock_sent_once:
                        self.ana_sunucu.sunucuya_postala(gorev_bilgisi)
                        lock_sent_once = True
                event_trigger.clear()
                
            if time.perf_counter()-qr_timer > 3:
                qr_sent_once = False
                qr_timer = time.perf_counter()

            if time.perf_counter()-lock_timer > 3:
                lock_sent_once = False
                lock_timer = time.perf_counter()

    def process_flow_manager(self):
        self.sunuculari_oluştur()

        th1 = threading.Thread(target=self.yonelim)
        th2 = threading.Thread(target=self.ana_sunucu_manager)
        th3 = threading.Thread(target=self.UI_TELEM)
        th4 = threading.Thread(target=self.PWM)
        th5 = threading.Thread(target=self.UI_FRAME)

        th1.daemon = True
        th2.daemon = True
        th3.daemon = True
        th4.daemon = True
        th5.daemon = True

        th1.start()
        th2.start()
        th3.start()
        th4.start()
        th5.start()

        p1 = mp.Process(target=self.capture_frames)
        p2 = mp.Process(target=self.process_frames, args=(1,))
        p3 = mp.Process(target=self.process_frames, args=(2,))
        p4 = mp.Process(target=self.process_frames, args=(3,))
        p5 = mp.Process(target=self.display_frames)

        p1.start()
        p2.start()
        p3.start()
        #p4.start()
        p5.start()

        return th1,th2,th3,th4,th5 , p1,p2,p3,p4,p5

    def terminate_all(self,p1,p2,p3,p4,p5):
            p1.terminate()
            cprint("Capture process terminated...","red","on_white", attrs=["bold"])
            p2.terminate()
            cprint("Frame-1 process terminated..","red","on_white", attrs=["bold"])
            p3.terminate()
            cprint("Frame-2 process terminated.","red","on_white", attrs=["bold"])
            #p4.terminate()
            #cprint("Frame-3 process terminated.","red","on_white", attrs=["bold"])
            p5.terminate()
            cprint("Display process terminated..\n","red","on_white", attrs=["bold"])

            p1.join()
            cprint("Capture process joined..","red","on_white", attrs=["bold"])
            p2.join()
            cprint("Frame-1 process joined..","red","on_white", attrs=["bold"])
            p3.join()
            cprint("Frame-2 process joined..","red","on_white", attrs=["bold"])
            #p4.join()
            #cprint("Frame-3 process joined..","red","on_white", attrs=["bold"])
            p5.join()
            cprint("Display process joined..\n","red","on_white", attrs=["bold"])

            # listener_process.terminate()
            # cprint("Listener process terminated..","red","on_white", attrs=["bold"])
            # listener_process.join()
            # cprint("Listener process joined..\n","red","on_white", attrs=["bold"])

    def ANA_GOREV_KONTROL(self):
        th1,th2,th3,th4,th5 , p1,p2,p3,p4,p5 = self.process_flow_manager()

        time.sleep(2)

        while True:
            try:
                self.secilen_görev_modu = self.Server_mod.recv_tcp_message()
            except Exception as e:
                cprint(f"MOD : Secilen modu alirken hata -> {e}","red",attrs=["bold"]) #TODO EKLENECEK...

            try:
                if self.SHUTDOWN_KEY == "ALGAN":
                    cprint("Final Shutdown..","red","on_white", attrs=["bold"])
                    self.terminate_all(p1=p1,p2=p2,p3=p3,p4=p4,p5=p5)
                    break

                if self.secilen_görev_modu == "kilitlenme" and not (self.önceki_mod=="kilitlenme"):
                    self.trigger_event(1,"kilitlenme")
                    self.trigger_event(2,"kilitlenme")
                    self.trigger_event(4,"yonelim")
                    self.önceki_mod = "kilitlenme"
                    cprint(f"GOREV MODU : Degisim -> {self.secilen_görev_modu}","red","on_white", attrs=["bold"])

                elif self.secilen_görev_modu == "kamikaze" and not (self.önceki_mod=="kamikaze"):
                    self.trigger_event(1,"kamikaze")
                    self.trigger_event(2,"kamikaze")
                    self.trigger_event(4,"qr")
                    self.önceki_mod = "kamikaze"
                    cprint(f"GOREV MODU : Degisim -> {self.secilen_görev_modu}","red","on_white", attrs=["bold"])

                elif self.secilen_görev_modu == "AUTO" and not (self.önceki_mod=="AUTO"):
                    self.trigger_event(1,"AUTO")
                    self.trigger_event(2,"AUTO")
                    self.trigger_event(4,"yonelim")
                    self.önceki_mod = "AUTO"
                    cprint(f"GOREV MODU : Degisim -> {self.secilen_görev_modu}","red","on_white", attrs=["bold"])

                elif self.secilen_görev_modu == "FBWA" and not (self.önceki_mod=="FBWA"):
                    self.trigger_event(1,"FBWA")
                    self.trigger_event(2,"FBWA")
                    self.trigger_event(4,"yonelim")
                    self.önceki_mod = "FBWA"
                    cprint(f"GOREV MODU : Degisim -> {self.secilen_görev_modu}","red","on_white", attrs=["bold"])

                elif self.secilen_görev_modu == "RTL" and not (self.önceki_mod=="RTL"):
                    self.trigger_event(1,"RTL")
                    self.trigger_event(2,"RTL")
                    self.trigger_event(4,"yonelim")
                    self.önceki_mod = "RTL"
                    cprint(f"GOREV MODU : Degisim -> {self.secilen_görev_modu}","red","on_white", attrs=["bold"])

                else:
                    cprint(f'GOREV MODU :{self.önceki_mod}','yellow', attrs=["bold"])

            except Exception as e:
                print("ANA_GOREV_KONTROL HATA: ",e)

            #? ISTENILEN BUTUN DURUMLAR EKLENEBILIR...

class gui:
    def __init__(self,Yer_istasyonu_obj) -> None:
        #GUI INIT
        self.root = tk.Tk()
        self.root.title("Ground Control Station")
        lock_img = tk.PhotoImage(file=os.getcwd()+'\\AlganYazilim\\Savasan-iha\\Mustafa Berkay\\Resources\\lock.png')
        unlock_img = tk.PhotoImage(file=os.getcwd()+'\\AlganYazilim\\Savasan-iha\\Mustafa Berkay\\Resources\\unlock.png')
        self.lock_img = lock_img.subsample(6, 6) 
        self.unlock_img = unlock_img.subsample(6, 6) 
        
        self.indicator_anasunucu = tk.Label(self.root, text="AnaSunucu", width=20, height=2, bg='red', font=('Helvetica', 12))
        self.indicator_yonelim = tk.Label(self.root, text="Yonelim", width=20, height=2, bg='red', font=('Helvetica', 12))
        self.indicator_mod = tk.Label(self.root, text="Mod", width=20, height=2, bg='red', font=('Helvetica', 12))
        self.indicator_kamikaze = tk.Label(self.root, text="Kamikaze", width=20, height=2, bg='red', font=('Helvetica', 12))
        self.indicator_UI_telem = tk.Label(self.root, text="UI_Telem", width=20, height=2, bg='red', font=('Helvetica', 12))
        self.indicator_YKI_ONAY = tk.Label(self.root, text="YKI_Onay", width=20, height=2, bg='red', font=('Helvetica', 12))
        self.indicator1_MAV_PROXY = tk.Label(self.root, text="MavProxy", width=20, height=2, bg='red', font=('Helvetica', 12))
        self.send_button = tk.Button(self.root, text="ONAY VER/REDDET", image = self.lock_img, command=Yer_istasyonu_obj.yki_onay_ver, font=('Helvetica', 14))
        self.exit_button = tk.Button(self.root, text="EXIT YKI", command=self.close_all, font=('Helvetica', 14))
        self.exit_button.pack(pady=20)
        self.indicator_anasunucu.pack(pady=10)
        self.indicator_yonelim.pack(pady=10)
        self.indicator_mod.pack(pady=10)
        self.indicator_kamikaze.pack(pady=10)
        self.indicator_UI_telem.pack(pady=10)
        self.indicator_YKI_ONAY.pack(pady=10)
        self.indicator1_MAV_PROXY.pack(pady=10)
        self.send_button.pack(pady=20)
        

        self.Yer_istasyonu_obj = Yer_istasyonu_obj

    def server_status_check(self):
        if self.Yer_istasyonu_obj.Yki_onayi_verildi:
            self.send_button.config(image=self.unlock_img)
        else:
            self.send_button.config(image=self.lock_img)

        if self.Yer_istasyonu_obj.ana_sunucu_status:
            self.indicator_anasunucu.config(bg='green')
        else:
            self.indicator_anasunucu.config(bg='red')
        
        if self.Yer_istasyonu_obj.Yönelim_sunucusu:
            self.indicator_yonelim.config(bg='green')
        else:
            self.indicator_yonelim.config(bg='red')

        if self.Yer_istasyonu_obj.kamikaze_sunucusu:
            self.indicator_mod.config(bg='green')
        else:
            self.indicator_mod.config(bg='red')

        if self.Yer_istasyonu_obj.kamikaze_sunucusu:
            self.indicator_kamikaze.config(bg='green')
        else:
            self.indicator_kamikaze.config(bg='red')

        if self.Yer_istasyonu_obj.UI_telem_sunucusu:
            self.indicator_UI_telem.config(bg='green')
        else:
            self.indicator_UI_telem.config(bg='red')

        if self.Yer_istasyonu_obj.YKI_ONAY_sunucusu:
            self.indicator_YKI_ONAY.config(bg='green')
        else:
            self.indicator_YKI_ONAY.config(bg='red')

        if self.Yer_istasyonu_obj.MAV_PROXY_sunucusu:
            self.indicator1_MAV_PROXY.config(bg='green')
        else:
            self.indicator1_MAV_PROXY.config(bg='red')
        
        # Schedule the next update
        self.root.after(500, self.server_status_check)

    def close_all(self):
        print("GUI: ('close_all') CALLED")
        yer_istasyonu_obj.trigger_event(event_number=10,message="stop_capture")
        time.sleep(3)
        yer_istasyonu_obj.SHUTDOWN_KEY = "ALGAN"
        self.root.destroy()

    def run(self):# Run the GUI event
        try:
            self.root.after(500, self.server_status_check)
            self.root.mainloop()
        except KeyboardInterrupt:
            print("KEYBOARD INTERRUPT\nKEYBOARD INTERRUPT\nKEYBOARD INTERRUPT\nKEYBOARD INTERRUPT\nKEYBOARD INTERRUPT\n")

def create_event_map():
    #Process frames
    message_queue_1 = mp.Queue()
    event_1 = mp.Event()
    message_queue_2 = mp.Queue()
    event_2 = mp.Event()
    message_queue_3 = mp.Queue()
    event_3 = mp.Event()

    #Kilitlenme mod change
    yonelim_queue = mp.Queue()
    yonelim_event = mp.Event()
    pwm_data_queue = mp.Queue()
    pwm_event = mp.Event()

    ana_sunucu_queue = mp.Queue()
    sunucu_event =  mp.Event()

    lock_once_event = mp.Event()
    qr_once_event = mp.Event()
    lock_outer_event = mp.Event()
    qr_outer_event = mp.Event()

    arayuz_frame_queue = mp.Queue()
    arayuz_telem_queue = mp.Queue()

    display_process_queue=mp.Queue()
    display_process_event=mp.Event()


    #event_map -> (1,2,3):process_frames <> (4,5):pwm-yonelim switch <> (6):Ana Sunucu <> (7,8):DEPRECATED <> (9):Arayüz veri yolları <> (10):Video kayıta erişim
    event_map = {
    1: (message_queue_1, event_1),
    2: (message_queue_2, event_2),
    3: (message_queue_3, event_3),
    4: (yonelim_queue,yonelim_event),
    5: (pwm_data_queue,pwm_event),
    6: (ana_sunucu_queue,sunucu_event),
    7: (lock_once_event,qr_once_event),
    8: (lock_outer_event,qr_outer_event),
    9: (arayuz_frame_queue,arayuz_telem_queue),
    10:(display_process_queue,display_process_event),
    #TODO EKLENECEK
    }
    return event_map

if __name__ == '__main__':
    SHUTDOWN_KEY = ""
    event_map = create_event_map()
    log_queue, listener_process = start_log_listener()
    setup_logging(log_queue)

#! Burada mission planner bilgisayarının ip'si(string) verilecek. 10.0.0.240
    yer_istasyonu_obj = Yerİstasyonu("10.80.1.60",
                                     event_map=event_map,
                                     SHUTDOWN_KEY=SHUTDOWN_KEY,
                                     frame_debug_mode="LOCAL",
                                     queue_size=2
                                     )

    Gui_obj = gui(Yer_istasyonu_obj=yer_istasyonu_obj)

    görev_kontrol = threading.Thread(target=yer_istasyonu_obj.ANA_GOREV_KONTROL)

    görev_kontrol.start()

    Gui_obj.run()

    cprint("FINAL","red",attrs=["bold"])