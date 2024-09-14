from Modules import path_drone as path
from Modules import ana_sunucu_islemleri
import argparse
import time

ana_sunucu=ana_sunucu_islemleri.sunucuApi("http://10.0.0.239:5000")

ana_sunucu.sunucuya_giris("rakip2","rakip2")

parser = argparse.ArgumentParser()
parser.add_argument('--connect', default=f'tcp:127.0.0.1:5762')
args = parser.parse_args()
connection_string = args.connect
rakip=path.Plane(connection_string)

time.sleep(2)

while True:
    rakip_veri = {
                "takim_numarasi": 2,
                "iha_enlem": rakip.pos_lat,
                "iha_boylam": rakip.pos_lon,
                "iha_irtifa": rakip.pos_alt_rel,
                "iha_dikilme":rakip.att_pitch_deg,
                "iha_yonelme": rakip.att_heading_deg,
                "iha_yatis": rakip.att_roll_deg,
                "iha_hizi": rakip.airspeed,
                "zaman_farki": 500}
    
    status , rakip_telemetri= ana_sunucu.sunucuya_postala(rakip_veri)
    print(rakip_telemetri)
    time.sleep(1)