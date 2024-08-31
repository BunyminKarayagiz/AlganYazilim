import math
import numpy as np

def durum2(yaw, roll, konum, hiz):

    def r_hesapla(hiz, roll):
        g = 9.81
        return (hiz ** 2) / (g * np.tan(roll))
    
    def yaw_degisimi_hesapla(hiz, roll):
        return hiz*np.tan(roll)/r_hesapla(hiz, roll)
    
    y_yaw=np.rad2deg(yaw)+np.rad2deg(yaw_degisimi_hesapla(hiz, roll))

    konum[0]=konum[0] + hiz*np.cos(np.deg2rad(y_yaw))
    konum[1]=konum[1] + hiz*np.sin(np.deg2rad(y_yaw))

    return konum

konum = durum2(0, 0, [50, 70], [18, 10])
print(f'Konum : {konum}')