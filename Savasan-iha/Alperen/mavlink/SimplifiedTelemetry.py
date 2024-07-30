import time
from pymavlink import mavutil
import sys


def connect():
    # Create the connection
    master = mavutil.mavlink_connection('tcp:localhost:14550')
    # Wait a heartbeat before sending commands
    master.wait_heartbeat()
    return master


def request_message_interval(master, message_id: int, frequency_hz: int):
    interval_us = 1e6 / frequency_hz  # Frequency in Hz to interval in microseconds
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
        message_id,
        interval_us,
        0, 0, 0, 0,
        0
    )


master = connect()
# Get the messages and reset intervals periodically
start_time = 0

# Initialize a dictionary to store the telemetry data
telemetry_data = {
    'RC_CHANNELS': None,
    'VFR_HUD': None,
    'GPS_RAW_INT': None,
    'SERVO_OUTPUT_RAW': None,
    'SYS_STATUS': None,
    'POWER_STATUS': None,
    'VIBRATION': None
}

# Initialize a dictionary to store the simplified telemetry data
simplified_telemetry_data = {
    'RC_CHANNELS': None,
    'VFR_HUD': None,
    'GPS_RAW_INT': None,
    'SERVO_OUTPUT_RAW': None,
    'SYS_STATUS': None,
    'POWER_STATUS': None,
    'VIBRATION': None
}

while True:
    try:
        # Reset message intervals every 10 seconds
        if time.time() - start_time > 10:
            request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_RC_CHANNELS, 40)
            request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_VFR_HUD, 40)
            request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_GPS_RAW_INT, 40)
            request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_SERVO_OUTPUT_RAW, 40)
            request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_SYS_STATUS, 40)
            request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_POWER_STATUS, 40)
            request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_VIBRATION, 40)
            start_time = time.time()

        msg = master.recv_match(blocking=True)
        if msg is None:
            print("No message received")
            continue

        msg_type = msg.get_type()
        if msg_type in telemetry_data:
            telemetry_data[msg_type] = msg.to_dict()

            # Update simplified telemetry data with selected fields
            if msg_type == 'RC_CHANNELS':
                simplified_telemetry_data[msg_type] = {
                    'chan1_raw': msg.chan1_raw,
                    'chan2_raw': msg.chan2_raw
                }
            elif msg_type == 'VFR_HUD':
                simplified_telemetry_data[msg_type] = {
                    'airspeed': msg.airspeed,
                    'groundspeed': msg.groundspeed
                }
            elif msg_type == 'GPS_RAW_INT':
                simplified_telemetry_data[msg_type] = {
                    'lat': msg.lat,
                    'lon': msg.lon
                }
            elif msg_type == 'SERVO_OUTPUT_RAW':
                simplified_telemetry_data[msg_type] = {
                    'servo1_raw': msg.servo1_raw,
                    'servo2_raw': msg.servo2_raw
                }
            elif msg_type == 'SYS_STATUS':
                simplified_telemetry_data[msg_type] = {
                    'voltage_battery': msg.voltage_battery,
                    'current_battery': msg.current_battery
                }
            elif msg_type == 'POWER_STATUS':
                simplified_telemetry_data[msg_type] = {
                    'Vcc': msg.Vcc,
                    'Vservo': msg.Vservo
                }
            elif msg_type == 'VIBRATION':
                simplified_telemetry_data[msg_type] = {
                    'vibration_x': msg.vibration_x,
                    'vibration_y': msg.vibration_y
                }

        print(f"Full telemetry data: {telemetry_data}")
        print(sys.getsizeof(telemetry_data))
        print(f"Simplified telemetry data: {simplified_telemetry_data}")
        print(sys.getsizeof(simplified_telemetry_data))

    except Exception as e:
        print(f"Error: {e}")
