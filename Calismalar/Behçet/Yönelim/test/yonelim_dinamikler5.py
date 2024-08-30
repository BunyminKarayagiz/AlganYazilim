import math

R = 6371000

def coğrafi_koordinatlari_xyzye_donustur(enlem, boylam, irtifa):
    enlem = math.radians(enlem)
    boylam = math.radians(boylam)
    
    x = (R + irtifa) * math.cos(enlem) * math.cos(boylam)
    y = (R + irtifa) * math.cos(enlem) * math.sin(boylam)
    z = (R + irtifa) * math.sin(enlem)
    
    return x, y, z

def xyz_koordinatlarini_coğrafi_koordinatlara_donustur(x, y, z):
    irtifa = math.sqrt(x**2 + y**2 + z**2) - R
    enlem = math.degrees(math.asin(z / (R + irtifa)))
    boylam = math.degrees(math.atan2(y, x))
    
    return enlem, boylam, irtifa

def hesaplamalar(enlem, boylam, irtifa, roll, pitch, hiz, sure):
    x, y, z = coğrafi_koordinatlari_xyzye_donustur(enlem, boylam, irtifa)
    
    roll = math.radians(roll)
    pitch = math.radians(pitch)
    
    vx = hiz * math.cos(pitch) * math.cos(roll)
    vy = hiz * math.cos(pitch) * math.sin(roll)
    vz = hiz * math.sin(pitch)
    
    X = x + vx * sure
    Y = y + vy * sure
    Z = z + vz * sure
    
    yeni_enlem, yeni_boylam, yeni_irtifa = xyz_koordinatlarini_coğrafi_koordinatlara_donustur(X, Y, Z)
    
    return yeni_enlem, yeni_boylam, yeni_irtifa

enlem, boylam, irtifa = 41.0082, 28.9784, 100
hesap = hesaplamalar(enlem, boylam, irtifa, 45, 30, 20, 60)

print(f'Yapilan hesaplamalar sonucu son konum (enlem, boylam, irtifa): {hesap}')
