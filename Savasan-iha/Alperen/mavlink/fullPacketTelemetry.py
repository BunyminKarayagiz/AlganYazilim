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
telemetry_data = {
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
        # Reset message intervals every 15 seconds
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

        print(telemetry_data)
        print(sys.getsizeof(telemetry_data))

    except Exception as e:

        print(f"Error: {e}")

