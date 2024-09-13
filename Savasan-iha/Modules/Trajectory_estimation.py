import math
import time
import numpy as np
import vincenty
from matplotlib.path import Path
import matplotlib.pyplot as plt

def simple_estimation(lat, lon, speed, roll_degree,pitch_degree,rotation_yaw):
    abs_speed= speed / 111320
    next_lat = lat + abs_speed * math.sin(rotation_yaw)
    next_lon = lon + abs_speed * math.cos(rotation_yaw)
    return next_lat,next_lon

def advanced_estimation(lat, lon, speed, roll_degree,pitch_degree,rotation_yaw,time_interval=1):
    # Convert degrees to radians
    lat = math.radians(lat)
    lon = math.radians(lon)
    yaw = math.radians(rotation_yaw)
    pitch = math.radians(pitch_degree)
    roll = math.radians(roll_degree)
    
    # Adjust yaw based on roll
    adjusted_yaw = yaw + roll
    
    # Decompose speed into horizontal and vertical components
    horizontal_speed = speed * math.cos(pitch)
    # vertical_speed = speed * math.sin(pitch) # Only needed if altitude change is relevant
    
    # Calculate the change in coordinates
    delta_lat = horizontal_speed * math.cos(adjusted_yaw) * time_interval / 6371000
    delta_lon = horizontal_speed * math.sin(adjusted_yaw) * time_interval / (6371000 * math.cos(lat))
    
    # Update latitude and longitude
    new_lat = lat + delta_lat
    new_lon = lon + delta_lon
    
    # Convert back to degrees
    new_lat = math.degrees(new_lat)
    new_lon = math.degrees(new_lon)
    
    return new_lat, new_lon
    
def high_resolution_estimation(lat, lon, speed, roll_degree,pitch_degree,rotation_yaw,time_interval=1):
     # Earth's radius in meters
    R = 6371000  

    # Convert degrees to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    yaw_rad = math.radians(rotation_yaw)
    pitch_rad = math.radians(pitch_degree)
    roll_rad = math.radians(roll_degree)

    # Gravitational acceleration
    g = 9.81  # m/s²

    # Check if roll angle is near ±90 degrees
    if abs(roll_degree) >= 89.9:
        omega = 0  # or handle as a special case
    else:
        omega = g * math.tan(roll_rad) / speed

    # Change in yaw over the time interval
    delta_yaw = omega * time_interval

    # Update yaw
    new_yaw_rad = yaw_rad + delta_yaw

    # Ground speed components considering pitch
    V_north = speed * math.cos(pitch_rad) * math.cos(new_yaw_rad)
    V_east = speed * math.cos(pitch_rad) * math.sin(new_yaw_rad)

    # Distance traveled
    delta_north = V_north * time_interval
    delta_east = V_east * time_interval

    # Convert distance to changes in latitude and longitude
    delta_lat = delta_north / R
    delta_lon = delta_east / (R * math.cos(lat_rad))

    # Update latitude and longitude
    new_lat = lat_rad + delta_lat
    new_lon = lon_rad + delta_lon

    # Convert back to degrees
    new_lat_deg = math.degrees(new_lat)
    new_lon_deg = math.degrees(new_lon)

    # Normalize longitude to be between -180 and 180 degrees
    new_lon_deg = (new_lon_deg + 180) % 360 - 180

    return new_lat_deg, new_lon_deg, math.degrees(new_yaw_rad)

def final_estimation(lat,lon,height,speed,roll_degree,pitch_degree,rotation_yaw,time_interval=1,referans_konum=(37.7348492, 29.0947473)):
    acilar = (roll_degree, pitch_degree,rotation_yaw)
    konum = (lat, lon, height)
    hiz = speed

    def Cartesian_to_LAT_LON(nokta, home_konumu):
        x_mesafe, y_mesafe = nokta
        # Enlem ve boylamı hesapla
        enlem = home_konumu[0] + y_mesafe / 111000  # 1 enlem derecesi yaklaşık 111 km'ye denk gelir
        boylam = home_konumu[1] + x_mesafe / (111000 * np.cos(np.radians(home_konumu[0])))
        nokta_yeni = (enlem, boylam)
        return nokta_yeni

    def LAT_LON_to_Cartesian(konum):
        i=konum
        y_ussu = (i[0], referans_konum[1])
        x_ussu = (referans_konum[0], i[1])

        y_mesafe = vincenty.vincenty(y_ussu, referans_konum)
        x_mesafe = vincenty.vincenty(x_ussu, referans_konum)
        # x i negatif yapmak için  boylamının home boylamından küçük olması gerekir
        if i[1] < referans_konum[1]:
            x_mesafe = x_mesafe * -1000
        else:
            x_mesafe = x_mesafe * 1000
        # y i negatif yapmak için enlemi home enleminin altında olması gerekir
        if i[0] < referans_konum[0]:
            y_mesafe = y_mesafe * -1000
        else:
            y_mesafe = y_mesafe * 1000
        nokta = (x_mesafe, y_mesafe, i[2])
        return nokta

    def noktayı_döndür(konum, açı):
        x, y = konum[0], konum[1]
        # Açıyı radyan cinsine çevir
        θ = np.deg2rad(açı)

        # Yeni koordinatları hesapla
        x_prime = x * np.cos(θ) - y * np.sin(θ)
        y_prime = x * np.sin(θ) + y * np.cos(θ)

        return x_prime, y_prime,

    def nokta_belirleme(konum0,hiz,yaw):
        konum=LAT_LON_to_Cartesian(konum0)
       # print(konum)
        # bir sonraki konumunun bulunma ihtimali en yüsek olan alanı belirleme
        #bu alan 5 nokta ile ifade edilecektir
        # a b c d e noktaları olarak isimlendirilecektir.
        #æ noktası için
        a_x=(hiz-4)*np.cos(np.deg2rad(0))
        a_y=(hiz-3)*np.sin(np.deg2rad(0))   

        a=(a_x,a_y)
        #b noktası için
        b_x=(hiz+4)*np.cos(np.deg2rad(0))
        b_y=(hiz+4)*np.sin(np.deg2rad(90))
        b=(b_x,b_y)
        #c noktası için
        c_x=(hiz+4)*np.cos(np.deg2rad(180))
        c_y=(hiz+4)*np.sin(np.deg2rad(90))

        c=(c_x,c_y)
        #d noktası için
        d_x=(hiz-4)*np.cos(np.deg2rad(180))
        d_y=(hiz-4)*np.sin(np.deg2rad(0))
        d=(d_x,d_y)
        #e noktası için
        #print(f"a:{a}\n b:{b}\n c:{c}\n d:{d}\n e:{e}")

        a=noktayı_döndür(a,-yaw)
        b=noktayı_döndür(b,-yaw)
        c=noktayı_döndür(c,-yaw)
        d=noktayı_döndür(d,-yaw)
        a=konum[0]+a[0],konum[1]+a[1]
        b=konum[0]+b[0],konum[1]+b[1]
        c=konum[0]+c[0],konum[1]+c[1]
        d=konum[0]+d[0],konum[1]+d[1]
        #print(f"a:{a}\n b:{b}\n c:{c}\n d:{d}\n e:{e}")


        return a,b,c,d
    
    a,b,c,d =nokta_belirleme(konum,hiz,konum[2])
    a_=Cartesian_to_LAT_LON(a,referans_konum)
    b_=Cartesian_to_LAT_LON(b,referans_konum)
    c_=Cartesian_to_LAT_LON(c,referans_konum)
    d_=Cartesian_to_LAT_LON(d,referans_konum)
    return a_,b_,c_,d_
