import math

def predict_next_position(x, y, speed, roll, pitch, yaw, delta_time):
    """
    Tahmin edilen bir sonraki konumu hesaplar.
    
    :param x: Mevcut x konumu
    :param y: Mevcut y konumu
    :param speed: Uçağın hızı
    :param roll: Roll açısı (derece cinsinden)
    :param pitch: Pitch açısı (derece cinsinden)
    :param yaw: Yaw açısı (derece cinsinden)
    :param delta_time: Zaman farkı (saniye cinsinden)
    
    :return: Tahmin edilen (x, y) konumu
    """
    # Dereceleri radyana çevir
    roll_rad = math.radians(roll)
    pitch_rad = math.radians(pitch)
    yaw_rad = math.radians(yaw)
    
    # Yaw açısını kullanarak hareket yönünü hesaplayın
    dx = speed * math.cos(yaw_rad) * delta_time
    dy = speed * math.sin(yaw_rad) * delta_time
    
    # Roll ve pitch açılarını dikkate alarak düzeltme yapalım
    # Bu basit bir düzeltme olarak eklenmiştir, daha kapsamlı bir model gerekebilir
    dx += speed * math.sin(roll_rad) * delta_time
    dy += speed * math.sin(pitch_rad) * delta_time
    
    # Yeni konumu hesaplayın
    next_x = x + dx
    next_y = y + dy
    
    return next_x, next_y


# Örnek veriler (x, y, hız, roll, pitch, yaw)
measurements = [
    [40.712776, -74.005974, 250, 5, 10, 15],
    [34.052235, -118.243683, 300, 10, 15, 20],
    [37.774929, -122.419418, 280, 15, 20, 25],
    [41.878113, -87.629799, 320, 20, 25, 30],
    [35.689487, 139.691711, 350, 25, 30, 35],
    [51.507351, -0.127758, 270, 30, 35, 40],
    [48.856613, 2.352222, 290, 35, 40, 45],
    [39.099727, -94.578568, 310, 40, 45, 50],
    [40.730610, -73.935242, 300, 45, 50, 55],
    [37.774929, -122.419418, 330, 50, 55, 60],
    [34.052235, -118.243683, 340, 55, 60, 65],
    [36.169941, -115.139832, 280, 60, 65, 70],
    [40.712776, -74.005974, 290, 65, 70, 75],
    [35.689487, 139.691711, 310, 70, 75, 80],
    [43.651070, -79.347015, 320, 75, 80, 85],
    [38.907654, -77.037683, 330, 80, 85, 90],
    [39.099727, -94.578568, 340, 85, 90, 95],
    [37.774929, -122.419418, 350, 90, 95, 100],
    [36.052235, -118.243683, 360, 95, 100, 105],
    [34.052235, -118.243683, 370, 100, 105, 110]
]

delta_time = 1  # Zaman farkı (saniye cinsinden)

# Her bir örnek veri için tahmin edilen konumu hesaplayın ve yazdırın
for index, meas in enumerate(measurements):
    x, y, speed, roll, pitch, yaw = meas
    next_x, next_y = predict_next_position(x, y, speed, roll, pitch, yaw, delta_time)
    
    print(f"Örnek {index + 1}:")
    print(f"Şu anki konum (x, y): ({x}, {y})")
    print(f"Hız: {speed}, Roll: {roll}, Pitch: {pitch}, Yaw: {yaw}")
    print(f"Tahmin edilen konum (x, y): ({next_x}, {next_y})")
    print("-------------------------------------------------")