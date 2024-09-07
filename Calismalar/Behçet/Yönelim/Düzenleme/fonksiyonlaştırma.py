import matplotlib.pyplot as plt
import numpy as np

def konum_hesaplama(konum,v,roll,yaw0):
    g= 9.81
    konumlar=[]

    def noktayı_döndür(konum, açı):
        x, y = konum
        # Açıyı radyan cinsine çevir
        θ = np.deg2rad(açı)

        # Yeni koordinatları hesapla
        x_prime = x * np.cos(θ) - y * np.sin(θ)
        y_prime = x * np.sin(θ) + y * np.cos(θ)

        return x_prime, y_prime

    def dönüş_yarıçapı(v, roll):
        g = 9.81
        return (v ** 2) / (g * np.tan(roll))

    def yaw_değişimi(v, r, roll, dt):
        return v * np.tan(roll) / r * dt

    def dairesel_hareket(konum,yaw, roll, v, dt):
        roll = np.deg2rad(roll)

        x, y = konum[0], konum[1]
        r = dönüş_yarıçapı(v, roll)
        yaw_degisim = yaw_değişimi(v, r, roll, dt)

        if roll < 0:
            yaw -= yaw_degisim
        else:
            yaw += yaw_degisim

        x += v * np.sin(yaw) * dt
        y += v * np.cos(yaw) * dt

        return x, y, yaw

    konum0=konum
    konumlar.append(konum)
    for i in range(10):
        x, y, yaw = dairesel_hareket(konum, 60, 20, 20, 0.1)
        konum = (x, y, yaw)
        konumlar.append((konum[0], konum[1]))

        print(konum)

    son_konum = konumlar[-1]
    son = noktayı_döndür(son_konum, -yaw0)
    print(son_konum)
    print(son)
    return son

konum_hesaplama((0, 0, 0), 30, 20, 20)
