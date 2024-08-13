import os
import torch
import numpy as np
import cv2
from ultralytics import YOLO
from Calismalar.Behcet.kalmanfilter_eski import KalmanFilter

class Detection:

    def __init__(self, path):
        self.model = YOLO(path)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)
        self.konum_verileri = []

    def model_predict(self, frame,frame_id):
        kf = KalmanFilter()
        #results = self.model.predict(frame, verbose=False)
        results = self.model.track(source=frame, conf=0.3, iou=0.5, show=False, tracker="botsort.yaml", verbose=False)
        # ----------------------detect/track etmediği durum için düzenlenecek----------------------------

        """pwm_verileri = {
                        'pwmx': 1500,
                        'pwmy': 1500,
                        'frame_id':frame_id
                        }"""
        
        pwm_verileri = np.array([1500,1500,frame_id],dtype=np.uint32)
        
        x, y = frame.shape[0], frame.shape[1]

        target_area_y1, target_area_y2 = (int(x * 0.10), int(x * 0.90))
        target_area_x1, target_area_x2 = (int(y * 0.25), int(y * 0.75))

        cv2.rectangle(frame, (target_area_x1, target_area_y1), (target_area_x2, target_area_y2), (255, 0, 0), 2) #RGB

        locked_or_not = False
        if results:
            annotated_frame = results[0].plot()

            boxes = results[0].boxes.xyxy.cpu().tolist()

            for box in boxes:
                x1, y1, x2, y2 = box
                x_center = int((x1 + x2) / 2)
                y_center = int((y1 + y2) / 2)

                pwm_verileri = self.coordinates_to_pwm(x_center, y_center,frame_id)

                rakip_verileri = [x_center, y_center]
                self.konum_verileri.append(rakip_verileri)     
                print(self.konum_verileri) 

                if(target_area_x1<x1 and target_area_x2>x2 and target_area_y1<y1 and target_area_y2>y2):
                    locked_or_not = True  
                return pwm_verileri, annotated_frame, locked_or_not
                
        return pwm_verileri, annotated_frame, locked_or_not

    def coordinates_to_pwm(self, x_center, y_center, frame_id):
        screen_width = 640
        screen_height = 480
        min_pwm = 1100
        max_pwm = 1900
        
        pwm_x = int((x_center / screen_width) * (max_pwm - min_pwm) + min_pwm)
        pwm_y = int((y_center / screen_height) * (max_pwm - min_pwm) + min_pwm)

        if pwm_y > 1500:
            fark = pwm_y - 1500
            pwm_y = 1500 - fark
        else : 
            fark = 1500 - pwm_y
            pwm_y = 1500 + fark

        if x_center == 0 and y_center == 0:
            pwm_x = 1500
            pwm_y = 1500

        """pwm_verileri = {
                        'pwmx': pwm_x,
                        'pwmy': pwm_y,
                        'frame_id': frame_id
                        }"""
        pwm_verileri = np.array([pwm_x,pwm_y,frame_id],dtype=np.uint32)
        return pwm_verileri


    def __call__(self):

        cap = cv2.VideoCapture(0)  # webcam
        frame_id = 0

        while True:
            ret, frame = cap.read()

            if ret:
                frame = cv2.resize(frame, (640, 480))
                pwm_verileri, annotated_frame, locked_or_not = self.model_predict(frame, frame_id)
                cv2.imshow("YOLOv8 Tracking", annotated_frame)
                print("PWM Verileri: ", pwm_verileri)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()


detection = Detection("C:\\Users\\asus\\AlganYazilim\\Calismalar\\Behcet\\V5_best.pt")
detection()


"""rakip_verileri = np.array([x_center, y_center])
                    self.konum_verileri.append(rakip_verileri)     
                    self.konum_verileri = np.array(self.konum_verileri)                                         
                    #! Regresyon ile tahmin deneme(iptal olabilir farklı bir şey deniyorum)

                    print("Genel Konum Verileri", self.konum_verileri)

                    if len(self.konum_verileri) < 7: 
                        #! Buraya Kalman ile tahmin gelecek
                        print("Kalman Filtesi devrede!")
                        print(f"Kalman_girilen_x: {x_center}", f"Kalman_girilen_y: {y_center}")
                        predicted = kf.predict(x_center, y_center)
                        print("Kalman Filtresi ile Tahmin Edilen Sonraki Konum: ", predicted)

                    elif len(self.konum_verileri) >= 7 and len(self.konum_verileri) <= 10:
                        #! Tüm her şey iptal buraya polinomial regression gelecek
                        #! Şu anda böyle üzerinde denemeler yapılıp bizim verilerimize entegre edilecek


                        print("x_center tipi: ", type(x_center))
                        print("y_center tipi: ", type(y_center))
                        print("1.konum_verisi_tipi: ", type(self.konum_verileri))

                        # Veri görselleştirme
                            plt.figure(figsize=(10, 6))  # Grafik boyutunu ayarla
                            plt.plot(df['Pozisyon'], df['Maas'], 'o', color='b', label='Veriler')

                            # X ve y veri hazirligi
                            X = df.iloc[:, 0].values.reshape(-1, 1)
                            y = df.iloc[:, 1].values.reshape(-1, 1)

                            # Basit Linear Regression
                            lin_reg = LinearRegression()
                            lin_reg.fit(X, y)
                            basit_linear_regresyon = lin_reg.predict(X)

                            # Polynomial Regression
                            poly_reg = PolynomialFeatures(degree=3)
                            X_poly = poly_reg.fit_transform(X)
                            lin_reg_2 = LinearRegression()
                            lin_reg_2.fit(X_poly, y)
                            polinom_linear_regresyon = lin_reg_2.predict(X_poly)

                            # Tahmin edilecek pozisyon
                            pozisyon_tah = 12

                            # Polynomial Regression ile tahmin
                            pozisyon_poly = poly_reg.transform(np.array([[pozisyon_tah]]))
                            maas_tahmini_poly = lin_reg_2.predict(pozisyon_poly)
                            tahmini_maas = maas_tahmini_poly[0][0]
                            print(f"Polinom Regresyon ile {pozisyon_tah} pozisyonunda tahmin edilen maaş: {tahmini_maas}")


                            # Basit Linear Regression sonucunu grafiğe ekle
                            plt.plot(X, basit_linear_regresyon, color='red', label='Basit Linear Regresyon')

                            # Polynomial Regression sonucunu grafiğe ekle
                            X_grid = np.arange(min(X), max(X), 0.1).reshape(-1, 1)
                            X_grid_poly = poly_reg.transform(X_grid)
                            plt.plot(X_grid, lin_reg_2.predict(X_grid_poly), color='green', label='Polinom Regresyon (derece=3)')

                            # Başlık ve etiketler ekle
                            plt.title('Pozisyon vs Maaş')
                            plt.xlabel('index')
                            plt.ylabel('maas')

                            # Grid ekle
                            plt.grid(True)

                            # Grafik göster
                            plt.legend()
                            plt.show()


                        print("konum yazdirma ifin icine girdi")

                        # 1. konum
                        x1 = self.konum_verileri[0][0]
                        y1 = self.konum_verileri[0][1]
                        print(f"1.konum_x {x1}", f"1.konum_y {y1}")

                        # 7. konum
                        x2 = self.konum_verileri[6][0]
                        y2 = self.konum_verileri[6][1]
                        print(f"10.konum_x {x2}", f"10.konum_y {y2}")

                        m = (y2-y1) / (x1 - x2)
                        b = y1 - (m*x1)

                        print(f"Dogru Denklemi: y = {m}x {b}")

                        xs = self.konum_verileri[-1][0]
                        ys = (m*xs) + b

                        print(f"Su anki konum_x: {self.konum_verileri[-1][0]}", f"Su anki konum_y: {self.konum_verileri[-1][1]}")
                        print("bir sonraki gidecegi konum:", ys)

                    elif len(self.konum_verileri) >= 10:
                        self.konum_verileri = self.konum_verileri[-10:]
                                            
                        for sira, koordinat in enumerate(self.konum_verileri):
                        print(f'{sira+1}. Rakibin konumu:', koordinat) # type(sira) == int

                        if sira >= 5:
                            # (sira-4). konum
                            pred_x4, pred_y4 = rakip_verileri[sira-4][0], rakip_verileri[sira-4][1]
                            
                            # (sira-3). konum
                            pred_x3, pred_y3 = rakip_verileri[sira-3][0], rakip_verileri[sira-3][1]
                            
                            # (sira-2). konum
                            pred_x2, pred_y2 = rakip_verileri[sira-2][0], rakip_verileri[sira-2][1]
                            
                            # (sira-1). konum
                            pred_x1, pred_y1 = rakip_verileri[sira-1][0], rakip_verileri[sira-1][1]
                            
                            # (sira). konum
                            pred_x, pred_y = rakip_verileri[sira][0], rakip_verileri[sira][1]

                            x_data = (pred_x4 + pred_x3 + pred_x2 + pred_x1 + pred_x) / 4
                            y_data = (pred_y4 + pred_y3 + pred_y2 + pred_y1 + pred_y) / 4"""