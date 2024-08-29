import ana_sunucu_islemleri as sunucuislemleri
import time
import SimpTelemCopy

ana_sunucu=sunucuislemleri.sunucuApi("http://10.80.1.71:5000")

ana_sunucu.sunucuya_giris("algan","53SnwjQ2sQ")
mavlink_obj = SimpTelemCopy.Telemetry("10.80.1.71","5762",2)
print("Before Connection")
mavlink_obj.connect()
print("Connected")
time.sleep(2)
time_start = time.perf_counter()
while True:
    rakip_veri,ui_telem = mavlink_obj.telemetry_packet()
    if time.perf_counter() - time_start > 0.8:
        status , rakip_telemetri= ana_sunucu.sunucuya_postala(rakip_veri)
        print(rakip_telemetri)
        time_start = time.perf_counter()