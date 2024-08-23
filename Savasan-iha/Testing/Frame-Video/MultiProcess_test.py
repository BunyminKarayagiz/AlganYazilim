import cv2
import multiprocessing as mp
import time
import YOLOv8_deploy
import datetime

def capture_frames(capture_queue):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error : Kamera...")
        return
    while True:
        #current = time.perf_counter()  --BENCHMARK
        ret, frame = cap.read()
        if not ret:
            break
        if not capture_queue.full():
            capture_queue.put(frame)
            #print("Frame saved in :",time.perf_counter()-current)  --BENCHMARK
    cap.release()
 
def process_frames(capture_queue, display_queue):

    yolo_model = YOLOv8_deploy.Detection("D:\\Visual Code File Workspace\\ALGAN\\AlganYazilim\\Savasan-iha\\Mustafa Berkay\\Model2024_V1.pt")
    lockedOrNot = 0
    locked_prev = 0
    prev_frame_time = 0
    is_locked=0
    sent_once=0
    elapsed_time=0
    start_time=0
    while True:



        if not capture_queue.empty():
            frame = capture_queue.get()
            benchmark_Timer = time.perf_counter()
            new_frame_time = time.perf_counter()
            pwm_verileri, processed_frame, lockedOrNot = yolo_model.model_predict(frame=frame)

            #Kilitlenme kontrol

            "Rakip kilitlenme"
            if lockedOrNot == 1 and locked_prev== 0:
                start_time=time.perf_counter()
                start_now =datetime.datetime.now()
                cv2.putText(img=processed_frame,text="HEDEF GORULDU",org=(50,400),fontFace=1,fontScale=2,color=(0,255,0),thickness=2)
                locked_prev=1

                #Hedef Görüldü. Yönelim modu devre dışı.
                #yönelim_modu=False

            if lockedOrNot == 0 and locked_prev== 1:
                cv2.putText(img=processed_frame,text="HEDEF KAYBOLDU",org=(50,400),fontFace=1,fontScale=2,color=(0,255,0),thickness=2)
                locked_prev= 0
                is_locked= 0
                sent_once = 0

                #Hedef kayboldu. Yönelim Moduna geri dön.
                #yönelim_modu=True
                #yönelim_modundan_cikis_eventi.set()

            if lockedOrNot == 1 and locked_prev== 1:
                elapsed_time= time.perf_counter()- start_time
                cv2.putText(img=processed_frame,text=str(round(elapsed_time,3)),org=(50,370),fontFace=1,fontScale=1.5,color=(0,255,0),thickness=2)

                if is_locked == 0:
                    cv2.putText(img=processed_frame,text="KILITLENIYOR",org=(50,400),fontFace=1,fontScale=1.8,color=(0,255,0),thickness=2)
                if elapsed_time >= 4.0:
                    cv2.putText(img=processed_frame,text="KILITLENDI",org=(50,400),fontFace=1,fontScale=1.8,color=(0,255,0),thickness=2)
                    kilitlenme_bilgisi=True
                    is_locked=1
                    print("KİLİTLENME BAŞARILI\nKİLİTLENME BAŞARILI\nKİLİTLENME BAŞARILI\nKİLİTLENME BAŞARILI\n")

                    #Kilitlenme gerçekleşti. Yönelim moduna geri dön.
                    #yönelim_modu=True
                    #yönelim_modundan_cikis_eventi.set()

            fps = 1/(new_frame_time-prev_frame_time)

            # try:
            #     if self.pwm_release==True:
            #         self.pwm_gönder(pwm_verileri)
            # except Exception as e:
            #     print("PWM SERVER : PWM GÖNDERİLİRKEN HATA...")

            prev_frame_time=time.perf_counter()

            # if is_locked == 1 and sent_once == 0:
            #     end_now = datetime.datetime.now()
            #     kilitlenme_bilgisi = {
            #         "kilitlenmeBaslangicZamani": {
            #             "saat": start_now.hour,
            #             "dakika": start_now.minute,
            #             "saniye": start_now.second,
            #             "milisaniye": start_now.microsecond #TODO düzeltilecek
            #         },
            #         "kilitlenmeBitisZamani": {
            #             "saat": end_now.hour,
            #             "dakika": end_now.minute,
            #             "saniye": end_now.second,
            #             "milisaniye": end_now.microsecond #TODO düzeltilecek
            #         },
            #         "otonom_kilitlenme": 0
            #     }
                # self.ana_sunucu.sunucuya_postala(json.dumps(kilitlenme_bilgisi))
                # self.sent_once = 1

            if not display_queue.full():
                print("Frame processed in : ",time.perf_counter()-benchmark_Timer)
                display_queue.put((processed_frame, fps))

def display_frames(display_queue):
    while True:
        if not display_queue.empty():
            frame, fps = display_queue.get()
            cv2.putText(frame, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.imshow('Webcam', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cv2.destroyAllWindows()

if __name__ == '__main__':
    capture_queue = mp.Queue(maxsize=1)
    display_queue = mp.Queue(maxsize=1)

    p1 = mp.Process(target=capture_frames, args=(capture_queue,))
    p2 = mp.Process(target=process_frames, args=(capture_queue, display_queue,))
    p3 = mp.Process(target=process_frames, args=(capture_queue, display_queue,))
    p4 = mp.Process(target=display_frames, args=(display_queue,))

    p1.start()
    p2.start()
    p3.start()
    p4.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()
