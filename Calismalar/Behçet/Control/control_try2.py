from prediction_algorithm_try import KalmanFilter
from hss_veri_gonderme import AirDefenseSystem
import socket
import time
from colorama import Fore, init
import concurrent.futures
from YOLOv8_deploy import Detection
import cv2
import threading

class KararMekanizmasi:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 65432
        init(autoreset=True)
        self.kf = KalmanFilter()
        self.datas = []

    def receive_status(self):
        baglanti_dogrulama = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(Fore.GREEN + "Hava Savunma Sisteminden Mesaj Bekleniyor...")
            while True:
                conn, addr = s.accept()
                with conn:
                    if not baglanti_dogrulama:
                        print(f"Bağlanti kuruldu: {addr}")
                        baglanti_dogrulama = True
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        status = data.decode('utf-8').split(',')[0]
                        if status == "active":
                            print(Fore.GREEN + "Hava savunma sistemi aktiftir.")
                        elif status == "inactive":
                            print(Fore.RED + "Hava savunma sistemi pasiftir.")

    def hss_start(self):
        self.connetction_thread = threading.Thread(target=self.receive_status, daemon=True)
        self.connetction_thread.start()

    def kalman_veri(self):
        def video_capture():
            cap = cv2.VideoCapture(0)

            while True:
                ret, frame = cap.read()

                if ret:
                    frame = cv2.resize(frame, (640, 480))
                    detect = Detection()

                    tahmin_pwm, annotated_frame, locked_or_not = detect.model_predict(frame)
                    
                    data = tahmin_pwm
                    self.datas.append([data])
                    cv2.imshow("Kalman Tahmin", annotated_frame)
                    print(f'Kalman PWM verileri: {data}')
                    print("Datas : ", self.datas)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
            cap.release()
            cv2.destroyAllWindows()

        video_thread = threading.Thread(target=video_capture)
        video_thread.start()
    
    def kalman_start(self):
        self.kalman_veri()
    
    def algorithm_start(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            feature_kalman = executor.submit(self.kalman_start)
            feature_hss = executor.submit(self.hss_start)

            kalman = feature_kalman.result()
            hss = feature_hss.result()

        combined_results = (kalman, hss)
        print("Datas: ", combined_results)

if __name__ == '__main__':
    karar = KararMekanizmasi()
    karar.algorithm_start()


    """def karar_ver(self):
        if self.hss :
            self.rota_hesapla()
        else:
            self.rakip_takip()

    def rota_hesapla(self):
        yonelim_tahmin = self.yonelim.tahmin_et()
        kalman_tahmin = self.kalman.tahmin_et()
        return yonelim_tahmin, kalman_tahmin

    def rakip_takip(self):
        yonelim_tahmin = self.yonelim.tahmin_et()
        return yonelim_tahmin"""


    """if __name__ == "__main__":
    karar = KararMekanizmasi()

    kalman = karar.kalman_start()
    veri = karar.hss_start()

    print(kalman)
    print(veri)"""

#! en sonki alınan hatanın alternatif çözümü:
"""
receive_status fonksiyonunuz, conn.recv(1024) çağrısında veri almayı bekler ve eğer bu çağrı bir veri alamazsa veya bağlantı kapanırsa, döngüden çıkıp fonksiyon sonlanır. İşte bunun olası nedenleri:

Olası Nedenler ve Çözümler:
Bağlantı Kapanması:

Eğer istemci (hava savunma sistemi) bağlantıyı kapatırsa, conn.recv(1024) çağrısı datayı boş bir bytes nesnesi (b'') olarak döndürür. Bu durumda, not data koşulu True olur ve while döngüsünden çıkarak fonksiyon sonlanır.
Çözüm: Bağlantı kapanmasını yönetmek istiyorsanız, fonksiyonun sonlanmasını engellemek için break komutundan sonra bağlantıyı tekrar başlatabilirsiniz veya yeniden listen durumuna dönebilirsiniz.
İstemci Veriyi Düzgün Göndermemesi:

İstemci, veriyi kesintisiz olarak göndermiyor olabilir. Örneğin, belirli bir süre sonra veri gönderimi duruyorsa, bu durumda conn.recv(1024) beklemede kalabilir veya bağlantı kesildiğinde yukarıdaki senaryo yaşanır.
Çözüm: İstemcinin veri gönderme durumu kontrol edilmelidir. Verinin nasıl gönderildiğini ve kesintisiz olup olmadığını kontrol edebilirsiniz.
Bağlantı Zaman Aşımı:

Bağlantının zaman aşımına uğraması, recv çağrısının None döndürmesine veya hata fırlatmasına neden olabilir. Bu da while döngüsünün sonlanmasına sebep olur.
Çözüm: Bağlantı zaman aşımını kontrol ederek, zaman aşımı durumunda yeniden bağlantı kurulmasını sağlayabilirsiniz. Ayrıca try-except bloğu ile hataları yakalayarak bağlantıyı yönetebilirsiniz.
Bağlantının Tekrar Dinlenmemesi:

Eğer bağlantı kapandıktan sonra yeniden listen durumuna geçilmiyorsa, yeni bağlantılar beklenmez ve fonksiyon sonlanır.
Çözüm: Bağlantı kapandıktan sonra s.listen() ile tekrar dinlemeye başlayabilirsiniz. Bu sayede yeni bağlantıları kabul etmeye devam edersiniz.

Bu iyileştirme ile:

Bağlantı kesilse bile, fonksiyon yeni bağlantıları beklemeye devam eder.
Hatalar try-except bloğuyla yönetilir, bu sayede fonksiyonun beklenmedik bir şekilde sonlanması engellenir.
Bağlantı kapandığında ve yeni bir bağlantı geldiğinde, yeniden listen durumu aktif hale gelir.
"""

#! KOD:
"""
def receive_status(self):
    baglanti_dogrulama = False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((self.host, self.port))
        s.listen()
        print(Fore.GREEN + "Hava Savunma Sisteminden Mesaj Bekleniyor...")
        while True:
            conn, addr = s.accept()
            with conn:
                if not baglanti_dogrulama:
                    print(f"Bağlanti kuruldu: {addr}")
                    baglanti_dogrulama = True
                try:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            print("Bağlantı kapandı.")
                            break
                        status = data.decode('utf-8').split(',')[0]
                        if status == "active":
                            print(Fore.GREEN + "Hava savunma sistemi aktiftir.")
                        elif status == "inactive":
                            print(Fore.RED + "Hava savunma sistemi pasiftir.")
                except Exception as e:
                    print(f"Hata oluştu: {e}")
                finally:
                    print("Bağlantı yeniden bekleniyor...")
                    baglanti_dogrulama = False  # Yeni bir bağlantı geldiğinde yeniden doğrulama yapılır

"""

