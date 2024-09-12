import time
from pymavlink import mavutil
import datetime
import pytz
import math

class Telemetry:
    def __init__(self, Mp_Ip,Mp_Port, takimNo):
        self.Mp_Ip = Mp_Ip
        self.takimNo = takimNo
        self.MP_Port = Mp_Port
        self.master = None
        self.telemetry_data = {
            'RC_CHANNELS': None,
            'VFR_HUD': None,
            'GPS_RAW_INT': None,
            'GLOBAL_POSITION_INT': None,
            'SERVO_OUTPUT_RAW': None,
            'SYS_STATUS': None,
            'POWER_STATUS': None,
            'SYSTEM_TIME': None,
            'VIBRATION': None,
            'ATTITUDE':None
        }
        self.simplified_telemetry_data = {
            'RC_CHANNELS': None,
            'VFR_HUD': None,
            'GPS_RAW_INT': None,
            'GLOBAL_POSITION_INT': None,
            'SERVO_OUTPUT_RAW': None,
            'SYS_STATUS': None,
            'SYSTEM_TIME': None,
            'POWER_STATUS': None,
            'VIBRATION': None
        }

    def connect(self):
        port = f'tcp:{self.Mp_Ip}:{self.MP_Port}'
        self.master = mavutil.mavlink_connection(port)
        self.master.wait_heartbeat()
        return self.master

    # def unix_to_datetime(self, unix_time):
    #     dt = datetime.datetime.fromtimestamp(unix_time, pytz.timezone('UTC'))
    #     print("datetime : ",dt)
    #     return dt.strftime("%H")[:-3] , dt.strftime("%M")[:-3] , dt.strftime("%S")[:-3] , dt.strftime("%f")[:-3]
    
    def unix_to_datetime(self, unix_time):
        dt = datetime.datetime.fromtimestamp(unix_time, pytz.timezone('UTC'))
        hour = dt.hour
        minute = dt.minute
        second = dt.second
        millisecond = dt.microsecond // 1000
        return hour,minute,second,millisecond


    def update_simplified_data(self, msg, msg_type):
        try:
            if msg_type == 'RC_CHANNELS':
                self.simplified_telemetry_data[msg_type] = {
                    'chan1_raw': msg.chan1_raw,
                    'chan2_raw': msg.chan2_raw
                }
            elif msg_type == 'VFR_HUD':
                self.simplified_telemetry_data[msg_type] = {
                    'airspeed': msg.airspeed,
                    'groundspeed': msg.groundspeed
                }
            elif msg_type == 'GPS_RAW_INT':
                self.simplified_telemetry_data[msg_type] = {
                    'lat': msg.lat,
                    'lon': msg.lon
                }
            elif msg_type == 'SERVO_OUTPUT_RAW':
                self.simplified_telemetry_data[msg_type] = {
                    'servo1_raw': msg.servo1_raw,
                    'servo2_raw': msg.servo2_raw
                }
            elif msg_type == 'SYS_STATUS':
                self.simplified_telemetry_data[msg_type] = {
                    'voltage_battery': msg.voltage_battery,
                    'current_battery': msg.current_battery
                }
            elif msg_type == 'POWER_STATUS':
                self.simplified_telemetry_data[msg_type] = {
                    'Vcc': msg.Vcc,
                    'Vservo': msg.Vservo
                }
            elif msg_type == 'SYSTEM_TIME':
                unix_time = msg.time_unix_usec / 1e6
                self.simplified_telemetry_data[msg_type] = {
                    'Time': self.unix_to_datetime(unix_time)
                }
            elif msg_type == 'VIBRATION':
                self.simplified_telemetry_data[msg_type] = {
                    'vibration_x': msg.vibration_x,
                    'vibration_y': msg.vibration_y
                }
        except Exception as e:
            print(f"Error updating simplified data for {msg_type}: {e}")

    def telemetry_packet(self):
        try:
            msg = self.master.recv_match(blocking=True)
            if msg is None:
                print("No message received")
                return [self.telemetry_data, self.simplified_telemetry_data]

            msg_type = msg.get_type()
            if msg_type in self.telemetry_data:
                self.telemetry_data[msg_type] = msg.to_dict()
                self.update_simplified_data(msg, msg_type)

            # gps_saati verisini çekme ve formatlama
            gps_saati_unix = self.telemetry_data['SYSTEM_TIME']['time_unix_usec'] / 1e6 if self.telemetry_data['SYSTEM_TIME'] and 'time_unix_usec' in self.telemetry_data['SYSTEM_TIME'] else None
            saat,dakika,saniye,milisaniye = self.unix_to_datetime(gps_saati_unix) if gps_saati_unix else None

            telemetry_output = {
                "takim_numarasi": self.takimNo,
                "iha_enlem": self.telemetry_data['GPS_RAW_INT']['lat'] / 1e7 if self.telemetry_data['GPS_RAW_INT'] and 'lat' in self.telemetry_data['GPS_RAW_INT'] else None,
                "iha_boylam": self.telemetry_data['GPS_RAW_INT']['lon'] / 1e7 if self.telemetry_data['GPS_RAW_INT'] and 'lon' in self.telemetry_data['GPS_RAW_INT'] else None,
                "iha_irtifa": self.telemetry_data['GLOBAL_POSITION_INT']['relative_alt'] / 1000 if self.telemetry_data['GLOBAL_POSITION_INT'] and 'relative_alt' in self.telemetry_data['GLOBAL_POSITION_INT'] else None,
                "iha_dikilme": self.telemetry_data['ATTITUDE']['pitch'] * (180 / math.pi) if self.telemetry_data['ATTITUDE'] and 'pitch' in self.telemetry_data['ATTITUDE'] else None,
                "iha_yonelme": (self.telemetry_data['ATTITUDE']['yaw'] * (180 / math.pi) + 360) % 360 if self.telemetry_data['ATTITUDE'] and 'yaw' in self.telemetry_data['ATTITUDE'] else None,
                "iha_yatis": self.telemetry_data['ATTITUDE']['roll'] * (180 / math.pi)if self.telemetry_data['ATTITUDE'] and 'roll' in self.telemetry_data['ATTITUDE'] else None,
                "iha_hiz": self.telemetry_data['VFR_HUD']['groundspeed'] if self.telemetry_data['VFR_HUD'] and 'groundspeed' in self.telemetry_data['VFR_HUD'] else None,
                "iha_batarya": self.telemetry_data['SYS_STATUS']['battery_remaining'] if self.telemetry_data['SYS_STATUS'] and 'battery_remaining' in self.telemetry_data['SYS_STATUS'] else None,
                "iha_otonom": 0,
                "iha_kilitlenme": 0,
                "hedef_merkez_X": 0,
                "hedef_merkez_Y": 0,
                "hedef_genislik": 0,
                "hedef_yukseklik": 0,
                "gps_saati":{
                    "saat": saat,
                    "dakika": dakika,
                    "saniye": saniye,
                    "milisaniye": milisaniye
                            }
                    }
            #gps_saati_formatted
            return [telemetry_output, self.simplified_telemetry_data]

        except Exception as e:
            print(f"Error: {e}")
            return [self.telemetry_data, self.simplified_telemetry_data]

"""if __name__ == "__main__":
    telemetry = Telemetry("127.0.0.1","5762",3)
    telemetry.master = telemetry.connect()
    while True:
        simplified_data, full_data = telemetry.telemetry_packet()
        print(simplified_data)
        print(full_data)"""