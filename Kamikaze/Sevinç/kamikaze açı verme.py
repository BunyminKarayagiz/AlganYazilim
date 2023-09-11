from dronekit import connect, VehicleMode, LocationGlobalRelative
import time


connection_string = 'tcp:127.0.0.1:5762'
iha = connect(connection_string, wait_ready=True, timeout=100)
print("iha ile bağlantı kuruldu")
yukseklik = iha.location.global_relative_frame.alt

def pitch_acısı(angle_degrees):
    iha.parameters['SERVO9_FUNCTION'] = 17
    servo_output = 1500 + angle_degrees * 20
    iha.channels.overrides['3'] = servo_output
def arm_ol_ve_yuksel(hedef_yukseklik):
    iha.armed = True
    if iha.armed == True:
        print("iha arm olmuştur.")
    iha.mode = VehicleMode('GUIDED')
    print("GUIDED moduna geçiş yapıldı")
    iha.simple_takeoff(hedef_yukseklik) # bu komutun çalışması için guided modda olması gerek
    iha.mode = VehicleMode("TAKEOFF")
    time.sleep(3)
    iha.mode = VehicleMode("AUTO") # bunun 50 metreden daha yüksek olması için auto moda geçiş yapması gerek
    while iha.location.global_relative_frame.alt <=100:
        print(f" yükseklik: { iha.location.global_relative_frame.alt}")
        time.sleep(0.5)
    if iha.location.global_relative_frame.alt >= 100:
        print("takeoff gerçekleşti.")
    time.sleep(1.5)
    konum = LocationGlobalRelative(iha.location.global_relative_frame.lat, iha.location.global_relative_frame.lon, 100)
    dalis = LocationGlobalRelative(iha.location.global_relative_frame.lat, iha.location.global_relative_frame.lon, 30)
    iha.simple_goto(konum)
    iha.mode = VehicleMode('FBWA')
    if iha.mode.name == "FBWA":
        print("FBWA moduna geçiş yapıldı ")
    print("dalışa geçiliyor")
    iha.simple_goto(dalis)
    pitch_acısı(-45)
    while iha.location.global_relative_frame.alt >= 30:
        print("alçalıyoruz...")
    time.sleep(0.5)
    iha.mode=VehicleMode('AUTO')
    iha.simple_goto(konum)
    while iha.location.global_relative_frame.alt <= 100:
        print("yükseliyoruz...")
        time.sleep(0.5)
    print("hedeflenen yüksekliğe ulaşıldı")


arm_ol_ve_yuksel(100)
