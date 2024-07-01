import json

import ana_sunucu_islemleri
import cv2

api = ana_sunucu_islemleri.sunucuApi("http://127.0.0.1:5000")
cap=cv2.VideoCapture(0)

def connect_to_anasunucu():
    "Burada durum kodu işlemin başarı kodunu vermektedir örn:200"
    ana_sunucuya_giris_durumu = False
    ana_sunucuya_giris_kodu, durum_kodu = api.sunucuya_giris(
        str("algan"),
        str("53SnwjQ2sQ"))
    if int(durum_kodu) == 200:
        print(f"\x1b[{31}m{'Ana Sunucuya Bağlanıldı: ' + durum_kodu}\x1b[0m")  # Ana sunucya girerkenki durum kodu.
        ana_sunucuya_giris_durumu = True
    return ana_sunucuya_giris_durumu


boolen = connect_to_anasunucu()
font = cv2.FONT_HERSHEY_SIMPLEX
def get_sunucusaat():
    status_code, sunuc_saati = api.sunucu_saati_al()
    sunuc_saati = json.loads(sunuc_saati)
    return sunuc_saati["saat"], sunuc_saati["dakika"], sunuc_saati["saniye"], sunuc_saati["milisaniye"]
def add_sunucusaati_to_frame(frame,text):
    cv2.putText(frame,
                text,
                (400, 30),
                font, 0.8,
                (0, 0, 255),
                1,
                cv2.LINE_4)

    return frame
while boolen:
    status_code, sunucu_saati = api.sunucu_saati_al()
    dict=json.loads(sunucu_saati)
    text= f"{ dict['saat'] , dict['dakika'], dict['saniye'] , dict['milisaniye'] }"
    print(text)
    ret, frame = cap.read()
    if ret :
        frame= add_sunucusaati_to_frame(frame,text)
        cv2.imshow("frame",frame )

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# After the loop release the cap object
cap.release()
# Destroy all the windows
cv2.destroyAllWindows()