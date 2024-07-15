# import numpy as np
# from pyzbar import pyzbar

import Server_Udp
import Server_Tcp
# from path import Plane
import ana_sunucu_islemleri
import threading
import cv2
import YOLOv8_deploy
import json
import time, datetime
import asyncio
import mavproxy2
import hesaplamalar
from qr_detection import QR_Detection
import multiprocessing as mp
import ipConfig

#! KOD ÇALIŞTIRMA SIRASI: sunucuapi -> Yer_istasyonu_v6 -> Iha_test(PUTTY) -> Iha_haberlesme(PUTTY)
class Yerİstasyonu():

    def __init__(self, mavlink_ip,event_map): #TODO HER BİLGİSAYAR İÇİN PATH DÜZENLENMELİ

        self.kullanici_adi = "algan"
        self.sifre = "53SnwjQ2sQ"
        self.ana_sunucu = ana_sunucu_islemleri.sunucuApi("http://127.0.0.1:5000")

        self.Server_yönelim = Server_Tcp.Server(9002,name="YÖNELİM")
        self.Server_pwm = Server_Tcp.Server(9001,name="PWM")
        self.Server_mod = Server_Tcp.Server(9003,name="MOD")

        #Sunucu durumları için kullanılacak değişkenler
        self.ana_sunucu_status = False
        self.Yönelim_sunucusu=False
        self.Mod_sunucusu=False
        self.PWM_sunucusu=False
        self.MAV_PROXY_sunucusu=False

        #YÖNELİM yapılacak uçağın seçilmesi için kullanılacak obje
        self.yönelim_obj=hesaplamalar.Hesaplamalar()

        #M.PLANNER bilgisayarından telemetri verisi çekmek için kullanılacak obje
        self.mavlink_obj = mavproxy2.MAVLink(mavlink_ip)

        "Multiprocessing ile sorunlu objeler"
        "----------------------------------------------"
        #PWM sinyal üretiminin senkronizasyonu için kullanılan objeler
        # self.pwm_event=asyncio.Event()
        # self.pwm_release=False

        # #Görüntüye rakibin yakalanması durumunda pwm moduna geçiş yapacak obje
        # self.yönelim_modundan_cikis_eventi=threading.Event()
        # self.yönelim_modu=True
        "----------------------------------------------"

        self.fark = 0

        #GÖREV_MODU SEÇİMİ
        self.event_map = event_map
        self.secilen_görev_modu="kilitlenme"
        self.önceki_mod = ""
        self.sunucu_saati:str = ""

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
                self.Server_pwm.reconnect()
                print("MOD : SERVER OLUŞTURULDU\n")
        self.Mod_sunucusu_sunucusu = connection_status
        return connection_status

    def MAV_PROXY_sunucusu_oluştur(self):
        connection_status = False
        while not connection_status:
            try:
                self.mavlink_obj.connect()
                connection_status = True
                print("MAVLINK : SERVER OLUŞTURULDU\n")
            except (ConnectionError, Exception) as e:
                print("MAVLINK SERVER: oluştururken hata : ", e , " \n")
                print("MAVLINK SERVER: yeniden bağlanılıyor...\n")
                connection_status=self.mavlink_obj.connect()
        self.MAV_PROXY_sunucusu=connection_status
        return connection_status

    #! KONTROL FONKSİYONU
    def trigger_event(self, event_number, message): #*message -> "kilitlenme" veya "kamikaze"
        try:
            if event_number in self.event_map:
                    queue, event = self.event_map[event_number]
                    queue.put(message)
                    event.set()
            else:
                raise ValueError(f"Event_map do not contain {event_number}")
        except Exception as e:
            print("TRIGGER ERROR -> ",e)

    #! KİLİTLENME MODUNDA ÇALIŞACAK FONKSİYONLAR
    def pwm_gonder(self,pwm_verileri):
        try:
            self.Server_pwm.send_data_to_client(json.dumps(pwm_verileri).encode())
        except Exception as e:
            print("PWM SUNUCU HATASI : ",e)
            print("PWM SUNUCUSUNA TEKRAR BAGLANIYOR...")
            self.Server_pwm.reconnect()

    def yonelim_gonder(self):

        while True:

            # if self.secilen_görev_modu != "kilitlenme":
            #     print("YONELİM/TAKIP --> BEKLEME MODU")
            #     self.yönelim_release_event.wait()
            #     print("YONELİM/TAKIP --> AKTIF")
            #     self.yönelim_release_event.clear()

            try:
                #bizim_telemetri=self.mavlink_obj.veri_kaydetme()
                #print("Telemetri:",bizim_telemetri)
                #rakip_telemetri=self.ana_sunucu.sunucuya_postala(bizim_telemetri)
                #yönelim_yapılacak_rakip= self.yönelim_obj.rakip_sec(rakip_telemetri,bizim_telemetri)
                yönelim_yapılacak_rakip = 0
            except Exception as e:
                print("YONELİM: TELEMETRİ ALINIRKEN HATA --> ",e)

            try:
                self.Server_yönelim.send_data_to_client(json.dumps(yönelim_yapılacak_rakip).encode())
            except Exception as e:
                print("YONELİM : VERİ GÖNDERİLİRKEN HATA --> ",e)
                print("YONELİM YENİDEN BAĞLANIYOR...")
                self.Server_yönelim.reconnect()

            time.sleep(0.1) #TODO GEÇİÇİ
            # if self.yönelim_modu==False:
            #     print("YÖNELİM DEVRE DIŞI")
            #     self.pwm_release=True
            #     self.yönelim_modundan_cikis_eventi.wait()
            #     self.yönelim_modundan_cikis_eventi.clear()
            #     self.pwm_release=False

    #! KAMİKAZE MODUNDA ÇALIŞACAK FONKSİYONLAR
    def qrKonum_gonder(self):

        try:
            _, self.qr_coordinat = self.ana_sunucu.qr_koordinat_al()
        except Exception as e :
            print("KAMIKAZE : SUNUCUDAN QR-KONUM ALINIRKEN HATA -> ",e)
            #TODO EKLEME YAPILACAK
        try:
            self.Server_yönelim.send_data_to_client(json.dumps(self.qr_coordinat).encode())
            
        except:
            print("KAMIKAZE : QR-KONUM IHA'YA GONDERILIRKEN HATA -> ",e)
            #TODO EKLEME YAPILACAK

    #! ANA FONKSİYONLAR
    def sunuculari_oluştur(self):
        #t1 = threading.Thread(target=self.Görüntü_sunucusu_oluştur)  # YKI_PROCESS Class içinde KULLANILMIŞ
        t2 = threading.Thread(target=self.PWM_sunucusu_oluştur)
        t3 = threading.Thread(target=self.Yönelim_sunucusu_oluştur)
        t4 = threading.Thread(target=self.MAV_PROXY_sunucusu_oluştur)
        t5 = threading.Thread(target=self.Mod_sunucusu_oluştur)
        #t1.start()
        t2.start()
        t3.start()
        t4.start()
        t5.start()
        t5.join()
        return t2,t3,t4,t5

    def ANA_GOREV_KONTROL(self):
        self.sunuculari_oluştur()
        time.sleep(10)
        önceki_mod = ""

        while True:
            self.secilen_görev_modu = self.Server_mod.recv_tcp_message()

            if self.secilen_görev_modu == "kilitlenme" and not (self.önceki_mod=="kilitlenme"):        
                self.trigger_event(1,"kilitlenme")
                self.trigger_event(2,"kilitlenme")
                self.önceki_mod = "kilitlenme"

            if self.secilen_görev_modu == "kamikaze" and not (self.önceki_mod=="kamikaze"):
                self.trigger_event(1,"kamikaze")
                self.trigger_event(2,"kamikaze")
                self.önceki_mod = "kamikaze"

            if self.secilen_görev_modu == "AUTO" and not (self.önceki_mod=="AUTO"):
                self.trigger_event(1,"AUTO")
                self.trigger_event(2,"AUTO")
                self.önceki_mod = "AUTO"

            if self.secilen_görev_modu == "FBWA" and not (self.önceki_mod=="FBWA"):
                self.trigger_event(1,"FBWA")
                self.trigger_event(2,"FBWA")
                self.önceki_mod = "FBWA"
            
            if self.secilen_görev_modu == "RTL" and not (self.önceki_mod=="RTL"):
                self.trigger_event(1,"RTL")
                self.trigger_event(2,"RTL")
                self.önceki_mod = "RTL"

            #? ISTENILEN BUTUN DURUMLAR EKLENEBILIR...


class YKI_PROCESS():

    def __init__(self,fark,event_map,queue_size=1,):
        self.fark = fark
        self.yolo_model = YOLOv8_deploy.Detection("C:\\Users\\bunya\\Desktop\\git\\AlganYazilim\\Savasan-iha\\Mustafa Berkay\\Model2024_V1.pt")

        self.Server_udp = Server_Udp.Server()
        self.görüntü_sunucusu=False

        #MultiProcess-Mod Objeleri
        self.capture_queue = mp.Queue(maxsize=queue_size)
        self.display_queue = mp.Queue(maxsize=queue_size)
        self.event_map = event_map

        self.qr_coordinat = ""
        self.qr = QR_Detection()

    #! SUNUCU FONKSİYONLARI
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

    #!FRAME ISLEYEN FONKSIYONLAR
    def qr_oku(self, frame):
        qr_result = self.qr.file_operations(frame=frame)
        return qr_result ,frame
    
    def capture_frames(self):
        process_name = mp.current_process().name
        print(f"Starting Capture-process: {process_name}")

        self.Görüntü_sunucusu_oluştur()

        while True:
            try:
                frame = self.Server_udp.recv_frame_from_client()
                try:
                    if not self.capture_queue.full():
                        self.capture_queue.put(frame)
                        #print("FRAME :SAVED IN CAPTURE_QUEUE ...")
                    else:
                        #print("FRAME : CAPTURE_QUEUE FULL...")
                        pass
                except Exception as e:
                    print("FRAME : CAPTURE_QUEUE ERROR -> ",e)
            except Exception as e:
                print("FRAME : RECEIVE ERROR ->",e)

    def process_frames(self, event_map,num):
        process_name = mp.current_process().name
        print(f"Starting Frame_Processing process: {process_name}")
        event_queue,event_trigger = event_map[num]

        lockedOrNot = 0
        locked_prev = 0
        event_message = "none"
        is_locked = 0

        while True:
            if event_trigger.is_set():
                time.sleep(0.01)
                event_message = event_queue.get()
                print(f"{process_name} received event: {event_message}")
                event_trigger.clear()
            print("EVENT MESSAGE:", event_message)
            if not self.capture_queue.empty():
                frame = self.capture_queue.get()

                if event_message == "kilitlenme":
                    pwm_verileri, processed_frame, lockedOrNot = self.yolo_model.model_predict(frame=frame)

                    #* 4 SANIYE-KILITLENME
                    if lockedOrNot == 1 and locked_prev== 0:
                            lock_start_time=time.perf_counter()
                            start_now =datetime.datetime.now()
                            cv2.putText(img=frame,text="HEDEF GORULDU",org=(50,400),fontFace=1,fontScale=2,color=(0,255,0),thickness=2)
                            locked_prev=1

                            # #Hedef Görüldü. Yönelim modu devre dışı.
                            # self.yönelim_modu=False
                    if lockedOrNot == 0 and locked_prev== 1:
                            cv2.putText(img=frame,text="HEDEF KAYBOLDU",org=(50,400),fontFace=1,fontScale=2,color=(0,255,0),thickness=2)
                            locked_prev= 0
                            is_locked= 0
                            sent_once = 0

                            # #Hedef kayboldu. Yönelim Moduna geri dön.
                            # self.yönelim_modu=True
                            # self.yönelim_modundan_cikis_eventi.set()
                    if lockedOrNot == 1 and locked_prev== 1:
                            lock_elapsed_time= time.perf_counter()- lock_start_time
                            cv2.putText(img=frame,text=str(round(lock_elapsed_time,3)),org=(50,370),fontFace=1,fontScale=1.5,color=(0,255,0),thickness=2)

                            if is_locked == 0:
                                cv2.putText(img=frame,text="KILITLENIYOR",org=(50,400),fontFace=1,fontScale=1.8,color=(0,255,0),thickness=2)
                            if lock_elapsed_time >= 4.0:
                                cv2.putText(img=frame,text="KILITLENDI",org=(50,400),fontFace=1,fontScale=1.8,color=(0,255,0),thickness=2)
                                kilitlenme_bilgisi=True
                                is_locked=1

                                # #Kilitlenme gerçekleşti. Yönelim moduna geri dön.
                                # self.yönelim_modu=True
                                # self.yönelim_modundan_cikis_eventi.set()
                    # try:
                    #     if self.pwm_release==True:
                    #         self.pwm_gönder(pwm_verileri)
                    # except Exception as e:
                    #     print("PWM SERVER : PWM GÖNDERİLİRKEN HATA...")
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

                            print("KİLİTLENME BAŞARILI\nKİLİTLENME BAŞARILI\nKİLİTLENME BAŞARILI\nKİLİTLENME BAŞARILI\n")
                            self.ana_sunucu.sunucuya_postala(json.dumps(kilitlenme_bilgisi))
                            self.sent_once = 1
                    
                    if not self.display_queue.full():
                        self.display_queue.put(processed_frame)

                elif event_message == "kamikaze":
                    qr_text,processed_frame = self.qr_oku(frame)
                    print(qr_text)

                    if not self.display_queue.full():
                        self.display_queue.put(processed_frame)

                elif event_message == "AUTO" or event_message == "FBWA" or event_message == "RTL":
                    if not self.display_queue.full():
                        self.display_queue.put(frame)

                else:
                    print("INVALID MODE...")
                    time.sleep(0.5)

                cv2.putText(frame, f'Mod: {event_message}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 128, 0), 2)

    def display_frames(self): #TODO SUNUCU SAATİ EKRANA BASILACAK...
        process_name = mp.current_process().name
        print(f"Starting Display process: {process_name}")
        fps_start_time = time.perf_counter()
        frame_count:float= 0.0
        fps:float = 0.0
        #counter= 0
        while True:
            if not self.display_queue.empty():
                frame = self.display_queue.get() #TODO EMPTY Queue blocking test?
                current_time = time.strftime("%H:%M:%S")
                cv2.putText(frame,"SUNUCU : "+current_time , (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 128, 0), 2)
                cv2.putText(frame, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 128, 0), 2)
                cv2.imshow('Camera', frame)
                fps = frame_count / (time.perf_counter() - fps_start_time)
                frame_count += 1.0
                #counter = 0
            else:
                #counter +=1
                #print("FRAME : DISPLAY_QUEUE IS EMPTY...",counter)
                pass

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        cv2.destroyAllWindows()

    #! ANA FONKSİYONLAR
    def process_manager(self):
        p1 = mp.Process(target=self.capture_frames)
        p2 = mp.Process(target=self.process_frames, args=(self.event_map, 1))
        p3 = mp.Process(target=self.process_frames, args=(self.event_map, 2))
        p4 = mp.Process(target=self.process_frames, args=(self.event_map, 3))
        p6 = mp.Process(target=self.display_frames)

        p1.start()
        p2.start()
        p3.start()
        p4.start()
        p6.start()

        return p1,p2,p3,p4,p6

    def start(self):
        p1,p2,p3,p4,p6 = self.process_manager()

        time.sleep(5)

        p1.join()
        p2.join()
        p3.join()
        p4.join()
        p6.join()

def create_IPC(event_map):
    pass

def create_event_map():        
    
    #Process frames
    message_queue_1 = mp.Queue()
    event_1 = mp.Event()
    message_queue_2 = mp.Queue()
    event_2 = mp.Event()
    message_queue_3 = mp.Queue()
    event_3 = mp.Event()

    #Kilitlenme mod change
    pwm_lock_queue = mp.Queue()
    pwm_lock_event = mp.Event()
    
    #event_map -> (1,2,3):process_frames ; (4):pwm-yonelim switch
    event_map = {
    1: (message_queue_1, event_1),
    2: (message_queue_2, event_2),
    3: (message_queue_3, event_3),
    4: (pwm_lock_queue,pwm_lock_event),
    #TODO EKLENECEK
    }
    
    return event_map


if __name__ == '__main__':

    event_map = create_event_map()

    control_objects = create_IPC(event_map=event_map)
    ip=ipConfig.wlan_ip()
    yer_istasyonu = Yerİstasyonu(ip,event_map=event_map) #! Burada mission planner bilgisayarının ip'si(string) verilecek. 10.0.0.240
    yer_istasyonu.anasunucuya_baglan()
    fark = yer_istasyonu.senkron_local_saat()

    yki_process = YKI_PROCESS(queue_size=2,fark=fark,event_map=event_map) #TODO queue_size test + "sunucu+fark"

    görev_kontrol = threading.Thread(target=yer_istasyonu.ANA_GOREV_KONTROL)
    görev_kontrol.start()

    yki_process.start()
    görev_kontrol.join()