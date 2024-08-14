import time

başlangıç = time.time()
gonderilen_zaman=başlangıç
while True:
    if time.time()-gonderilen_zaman < 1:
        break
    else:
        print("1 saniye geçti")
        gonderilen_zaman=time.time()


