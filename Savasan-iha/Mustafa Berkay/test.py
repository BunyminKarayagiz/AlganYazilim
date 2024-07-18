import cv2 
kamera = cv2.VideoCapture(0) # kamerayı çağırma


fourcc = cv2.VideoWriter_fourcc(*'MP4V') # XVID algoritmasını tanımlama
kayit = cv2.VideoWriter('kayit.mp4',fourcc,20.0,(640,480))
# fourcc ile saniyede 20 resim alarak 640x480 boyutlarında bir avi dosyası
 
while True:
    ret,goruntu=kamera.read() # kamera okumayı başlatma
    kayit.write(goruntu) # video yazmayı başlatma
    cv2.imshow('goruntu',goruntu) # görüntüyü gösterme
    if cv2.waitKey(25) & 0xFF ==ord('t'): # t tuşuna basılınca durdur.
        break
kamera.release() # kamerayı serbest bırak.
kayit.release() # kaydı durdur
cv2.destroyAllWindows() # açılan pencereleri kapat.