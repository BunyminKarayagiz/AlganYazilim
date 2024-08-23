import cv2
import numpy as np
import math
import time

class KalmanFilter:
    def __init__(self, xCenter=None, yCenter=None):
        print("Kalman algoritmasi devrede!")
        self.measurements = []
        self.kf = cv2.KalmanFilter(6, 2)

        self.kf.transitionMatrix = np.array([[1, 0, 1, 0, 0.5, 0],
                                             [0, 1, 0, 1, 0, 0.5],
                                             [0, 0, 1, 0, 1, 0],
                                             [0, 0, 0, 1, 0, 1],
                                             [0, 0, 0, 0, 1, 0],
                                             [0, 0, 0, 0, 0, 1]], dtype=np.float32)
        """Geçiş matrisi sistemin bir durumdan diğerine nasil geçtiğini modellemek için kullanilir.
        sistemin durumunun zaman içinde nasil degistigini tanimlar.
        klasik fizik denklemlerini kullanir.
        x' = x + vx + 0.5 * va * dt^2 (1. ve 2. satiir)
        vx' = vx + va * t (3. v 4. satir)
        transationMatrix sistemin önceki durum vektörü ile çarpilarak bir sonraki adimda sahip olduğu yeni durum vektörünü belilemek için kullanilir 
        """

        self.kf.measurementMatrix = np.array([[1, 0, 0, 0, 0, 0],
                                              [0, 1, 0, 0, 0, 0]], dtype=np.float32)
        """
        ölçüm matrisi gerçek dünyadan alinan gözlem verilerini durum vektörüyle ilişkilendirir. 
        kodda konum bilgileri direkt olarak ölcülebileceğinden x ve y konum bileşenleri ile ilgili satirlar 1 degerini almiştir
        ölçüm matirisinde sadece x ve y ölcümleri durum vektörüyle iliskilidir.
        güncelleme aşamasinda kalman filtresi bu matrisle ölçüm verilerini durum vektörü bileşenlerine ekler.
        kisaca bu matris doğrudan ölçebildiğimiz x ve y konum bileşenlerinin durum vektörüyle olan ilişkisini kurar.
        Hiz ve ivme doğrudan öçülemez. Bu yüzden matris içerisinde yer almazlar.
        """

        self.kf.processNoiseCov = np.array([[1e-1, 0, 0, 0, 0, 0],
                                            [0, 1e-1, 0, 0, 0, 0],
                                            [0, 0, 1e-1, 0, 0, 0],
                                            [0, 0, 0, 1e-1, 0, 0],
                                            [0, 0, 0, 0, 1e-1, 0],
                                            [0, 0, 0, 0, 0, 1e-1]], dtype=np.float32)
        """
        İşlem gürültüsü sistemin zamanla evrildiği rastgele sapmalari ifade eder. kalman filtresinde bu sapmalar işlem gürültüsü koveryans matrisi ile hesaplanir.
        işlem gürültüsü koveryans matrisi sistemin dinamik modelindeki belirsizlikleri yani modelin doğruluğundaki olasi sapmalari ifade eder.
        Kalman zamanla takip ettiği sistem durumunda bazi varsayimlarda bulunur ama gerçek dünyada bu varsayimlar sistemin modelinin mükemmel
        olmamasindan ve sistem üzerine etki eden gürültülerden dolayi tamamen doğru olmayacaktir.
        1e-1=0.1 lik bir gürültüyü temsil eder.
        Yukaridaki matriste her bir durum için gürültü seviyesi 1e-1 olarak atanmiştir.  processNoiseCov kalman filtresi tahmin aşamasinda kullanilir 
        ve sistemin bir sonraki adimda ne kadar belirsiz olacağini modeller. bu belirsizlik sistem durumunu tahmin ederken tahminlerin ne kadar güvenilir olduğunu belirtir.
        """
        
        self.kf.measurementNoiseCov = np.array([[1e-1, 0],
                                                [0, 1e-1]], dtype=np.float32)
        """
        Bu matris ölçümler sirasinda meydana gelebilecek gürültüleri modellemek için kullanilmiştir. Gerçek dünya verilerinde çeşitli sebeplerden dolayi hatalar
        olabilir. measurementNoiseCov matrisi bu hatalari modellemek içindir. bu matrisde x ve y konumlarinin gürültü seviyesi 1e-1 olarak alinmistir. bu matris
        kullanilarak her bir ölçümün ne kadar güvenilir olduğunu ve tahmin edilen durumun ne kadar güncellenmesi gerektiğini belirtir.
        Daha büyük değerler daha yüksek 
        ölçüm hatalarini ifade eder ve ölçümlerin daha az güvenilir olduğunu gösterir
        1e-1 gürültü katsayisi tahminlere ne kadar güvenileceğini belirtir. Bu katsayi ölçümler yapildikçe güncellenmektedir. 
        """

        self.kf.errorCovPre = np.array([[1, 0, 0, 0, 0, 0],
                                        [0, 1, 0, 0, 0, 0],
                                        [0, 0, 1, 0, 0, 0],
                                        [0, 0, 0, 1, 0, 0],
                                        [0, 0, 0, 0, 1, 0],
                                        [0, 0, 0, 0, 0, 1]], dtype=np.float32)
        """ #* Tahmin aşamasinda kullanilir.
        errorCovPre sistemin tahmin edilen durum vektöründeki hatalarin büyüklüğünü ve bu hatalarin nasil dagildiğini modellemek için kullanilir.
        hatalar ölçümler ile tahmin verileri arasindaki fark ile bulunur. bu matris hem tahmin hem güncelleme aşamasinda kullanilir. Bu matriste 
        her bir durum bileşeni için standart bir belirsizklik olduğunu gösterir. kalman filtresi bu matrisi kullanarak durum tahminlerindeki 
        belirsizliklerin nasil biriktigini hesaplar. sistem modeli ve processNoisCov ile birlikte kullanilir. ölçümler alindiğinda ölçüm verileri
        ile karşilaştirarak güncellenir. Sistem başlangiçta çokfazla bilgiye sahip olmadiğindan dolayi ile başta birim matris kullanilir. 
        """
        
        self.kf.errorCovPost = np.array([[1, 0, 0, 0, 0, 0],
                                        [0, 1, 0, 0, 0, 0],
                                        [0, 0, 1, 0, 0, 0],
                                        [0, 0, 0, 1, 0, 0],
                                        [0, 0, 0, 0, 1, 0],
                                        [0, 0, 0, 0, 0, 1]], dtype=np.float32)
        """ #* Kalman filtresinin güncelleme aşamasindan sonra kullanilir.
        errorCovPost kalman filtresinin ölçüm verilerini kullandiktan SONRA tahmin edilen duruma ne kadar güvenildiğini belirtir. bu errorrCovPost 
        bir sonraki aşamadaki tahminde errorCovPre olarak kullanilir. 
        """

        #* errorCovPre ve errorCovPost arasindaki farklar:
        """
        errorCovPre:
        - tahmin aşamasinda kullanilir.
        - güncellemeden önceki belirsizliği ifade eder.
        - bir önceki güncellemeden sonraki tahmin belirsizliğini yansitir

        errorCovPost:
        - güncelleme aşamasindan sonra kullanilir
        - güncellenmiş duruma olan güveni ve kalan belirsizliği ifade eder
        - güncel ölçümlerden sonra kalan belirsizliği ifade eder
        """

        self.kf.gain = np.array([[1, 0, 0, 0, 0, 0],
                                [0, 1, 0, 0, 0, 0],
                                [0, 0, 1, 0, 0, 0],
                                [0, 0, 0, 1, 0, 0],
                                [0, 0, 0, 0, 1, 0],
                                [0, 0, 0, 0, 0, 1]], dtype=np.float32)
        """
        Bu matris tahminler ve ölçümler arasindaki dengeyi kurmamiza yardimci olur. burada verilen kalman gain matrisi başlangiçta her bir
        durum bileşeninin tam olarak doğru olduğu varsayilarak başlatilir. kalman kazanci zamanala gelen verileri işleyerek tahmin ve ölçüm
        arasindaki farklardan yararlanarak hata sayilarini en aza indirip sonuçlari daha doğru bir şekilde tahmin etmeyi sağlar. özetle kalman 
        kazanci tahmin edilen durumlarla ölçümler arasindaki farklari alarak çalişir.
        """

        """
        #* bakilacak
        self.kf.controlMatrix = np.array([[0, 0],
                                 [0, 0],
                                 [1, 0],
                                 [0, 1],
                                 [0, 0],
                                 [0, 0]], dtype=np.float32)"""

    #* Bir sonraki zaman adimindaki konumu tahmin etmesini sağlayan fonksiyn
    def predict(self):
        """
        #* bakilacak
        acceleration = 0.5
        braking = 0.1
        control_input = np.array([[acceleration], [braking]], dtype=np.float32)
        statePre = self.kf.predict()
        self.kf.statePre += self.kf.controlMatrix @ control_input"""
        statePre = self.kf.predict()
        return statePre

    def correct(self, measurement):
        start_time = time.perf_counter()

        S = self.kf.measurementMatrix @ self.kf.errorCovPre @ self.kf.measurementMatrix.T + self.kf.measurementNoiseCov
        K = self.kf.errorCovPre @ self.kf.measurementMatrix.T @ np.linalg.inv(S)

        #* Yeni durum vektörü tahmini için kullanacağımız fark matrisini oluşturur.
        y = measurement - (self.kf.measurementMatrix @ self.kf.statePre)

        #* Kalman kazanci ve ölçüm-tahmin arasindaki farkları alarak yeni durum vektörünü oluşturur
        self.kf.statePost = self.kf.statePre + K @ y

        #* Bunun oluşturulmasini nedeni errorCovPost hata koveryansini güncellerken kullanilacak birim matrisi oluşturmaktir. 
        I = np.eye(self.kf.transitionMatrix.shape[0], dtype=np.float32)
        self.kf.errorCovPost = (I - K @ self.kf.measurementMatrix) @ self.kf.errorCovPre

        #* işlemler yapılırkenki geçen zamani hesaplamamiza yarar (yanlış hesaplanmş olabilir kontrol et!)
        elapsed_time = time.perf_counter() - start_time
        print(f"Correct işlemi Süresi: {elapsed_time:.9f} saniye")

        return self.kf.statePost

    #* Güncellenmiş durum vektörünü dişaridan erişilebilmek için oluşturulan fonksiyon
    def get_state(self):
        return self.kf.statePost

    def add_measurements(self, measurements):
        for meas in measurements:
            #* veriler ekleniyor
            x, y = meas
            measurement = np.array([[np.float32(x)], [np.float32(y)]])
            self.measurements.append([x, y])

            #* correct fonksiyonu işleme dahil ediliyor
            self.correct(measurement)

            #* tahmin aşaması gerçekleştirilir ve sistemin güncellenmiş durum vektörü alınır.
            predicted_state = self.predict()
            state_post = self.get_state()

            speed_x = predicted_state[2].item() #* dizinin 2. elemanini float veri tipine dönüştürür
            speed_y = predicted_state[3].item()
            speed = math.sqrt((speed_x**2) + (speed_y**2))

            np.set_printoptions(suppress=True) #* bilimsel hesaplamalari kapatır
            print(f"Son ölçüm: {self.measurements[-1]}")
            print(f"Tahmin edilen durum: {predicted_state.T}")
            print(f"Güncellenmiş durum: {state_post.T}")
            print(f"Hiz: {speed}")
            print("------")