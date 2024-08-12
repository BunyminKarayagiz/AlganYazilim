import time
from pymavlink import mavutil
import sys
import datetime
import pytz

class Telemetry:
    def __init__(self, Mp_Ip, frequency_hz=40):
        self.Mp_Ip = Mp_Ip
        self.frequency_hz = frequency_hz
        self.master = None
        self.telemetry_data = {
            'RC_CHANNELS': None,
            'VFR_HUD': None,
            'GPS_RAW_INT': None,
            'SERVO_OUTPUT_RAW': None,
            'SYS_STATUS': None,
            'POWER_STATUS': None,
            'SYSTEM_TIME': None,
            'VIBRATION': None
        }
        self.simplified_telemetry_data = {
            'RC_CHANNELS': None,
            'VFR_HUD': None,
            'GPS_RAW_INT': None,
            'SERVO_OUTPUT_RAW': None,
            'SYS_STATUS': None,
            'SYSTEM_TIME': None,
            'POWER_STATUS': None,
            'VIBRATION': None
        }
        self.start_time = time.time()

    def connect(self):
        port = ('tcp:' + (self.Mp_Ip) + ':14550')
        self.master = mavutil.mavlink_connection(port)
        self.master.wait_heartbeat()
        return self.master

    def request_message_interval(self, message_id):
        interval_us = 1e6 / self.frequency_hz
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
            message_id,
            interval_us,
            0, 0, 0, 0,
            0
        )

    def reset_intervals(self):
        if time.time() - self.start_time > 10:
            self.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_RC_CHANNELS)
            self.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_VFR_HUD)
            self.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_GPS_RAW_INT)
            self.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_SERVO_OUTPUT_RAW)
            self.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_SYS_STATUS)
            self.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_POWER_STATUS)
            self.request_message_interval(mavutil.mavlink.MAVLINK_MSG_ID_VIBRATION)
            self.start_time = time.time()

    def unix_to_datetime(self, unix_time):
        # UNIX zaman damgasını datetime objesine dönüştür ve Türkiye saatine ayarla
        dt = datetime.datetime.fromtimestamp(unix_time, pytz.timezone('Europe/Istanbul'))
        return dt.strftime("%d-%m-%Y %H:%M:%S.%f")[:-3]

    def update_simplified_data(self, msg, msg_type):
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
            # time_unix_usec değeri mikro saniye cinsinden olduğundan bunu saniye cinsine çeviriyoruz.
            unix_time = msg.time_unix_usec / 1e6
            self.simplified_telemetry_data[msg_type] = {
                'Time': self.unix_to_datetime(unix_time)
            }
        elif msg_type == 'VIBRATION':
            self.simplified_telemetry_data[msg_type] = {
                'vibration_x': msg.vibration_x,
                'vibration_y': msg.vibration_y
            }

    def telemetry_packet(self):
        try:
            self.reset_intervals()

            msg = self.master.recv_match(blocking=True)
            if msg is None:
                print("No message received")
                return [self.telemetry_data, self.simplified_telemetry_data]

            msg_type = msg.get_type()
            if msg_type in self.telemetry_data:
                self.telemetry_data[msg_type] = msg.to_dict()
                self.update_simplified_data(msg, msg_type)

            # gps_saati verisini çekme ve formatlama
            gps_saati_unix = self.telemetry_data['SYSTEM_TIME']['time_unix_usec'] / 1e6 if self.telemetry_data[
                                                                                                'SYSTEM_TIME'] and 'time_unix_usec' in self.telemetry_data['SYSTEM_TIME'] else None
            gps_saati_formatted = self.unix_to_datetime(gps_saati_unix) if gps_saati_unix else None

            telemetry_output = {
                "takim_numarasi": 1,
                "iha_enlem": self.telemetry_data['GPS_RAW_INT']['lat'] / 1e7 if self.telemetry_data[
                                                                                    'GPS_RAW_INT'] and 'lat' in
                                                                                self.telemetry_data[
                                                                                    'GPS_RAW_INT'] else None,
                "iha_boylam": self.telemetry_data['GPS_RAW_INT']['lon'] / 1e7 if self.telemetry_data[
                                                                                     'GPS_RAW_INT'] and 'lon' in
                                                                                 self.telemetry_data[
                                                                                     'GPS_RAW_INT'] else None,
                "iha_irtifa": self.telemetry_data['VFR_HUD']['alt'] if self.telemetry_data['VFR_HUD'] and 'alt' in
                                                                       self.telemetry_data['VFR_HUD'] else None,
                "iha_dikilme": self.telemetry_data['VFR_HUD']['pitch'] if self.telemetry_data['VFR_HUD'] and 'pitch' in
                                                                          self.telemetry_data['VFR_HUD'] else None,
                "iha_yonelme": self.telemetry_data['VFR_HUD']['heading'] if self.telemetry_data[
                                                                                'VFR_HUD'] and 'heading' in
                                                                            self.telemetry_data['VFR_HUD'] else None,
                "iha_yatis": self.telemetry_data['VFR_HUD']['roll'] if self.telemetry_data['VFR_HUD'] and 'roll' in
                                                                       self.telemetry_data['VFR_HUD'] else None,
                "iha_hiz": self.telemetry_data['VFR_HUD']['airspeed'] if self.telemetry_data[
                                                                             'VFR_HUD'] and 'airspeed' in
                                                                         self.telemetry_data['VFR_HUD'] else None,
                "iha_batarya": self.telemetry_data['SYS_STATUS']['battery_remaining'] if self.telemetry_data[
                                                                                             'SYS_STATUS'] and 'battery_remaining' in
                                                                                         self.telemetry_data[
                                                                                             'SYS_STATUS'] else None,
                "iha_otonom": 1,
                "iha_kilitlenme": 1,
                "hedef_merkez_X": 300,
                "hedef_merkez_Y": 230,
                "hedef_genislik": 30,
                "hedef_yukseklik": 43,
                "gps_saati": gps_saati_formatted
            }

            return [telemetry_output, self.simplified_telemetry_data]
        except Exception as e:
            print(f"Error: {e}")
            return [self.telemetry_data, self.simplified_telemetry_data]

"""if __name__ == "__main__":
    telemetry = Telemetry("127.0.0.1")
    telemetry.master = telemetry.connect()
    while True:
        simplified_data, full_data = telemetry.telemetry_packet()
        print(simplified_data)
        print(full_data)"""
