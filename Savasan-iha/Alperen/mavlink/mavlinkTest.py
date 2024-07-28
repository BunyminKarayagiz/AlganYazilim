import time
from pymavlink import mavutil


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

# Initial message request
request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_RC_CHANNELS, 40)
request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_VFR_HUD, 40)
request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_GPS_RAW_INT, 40)
request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_SERVO_OUTPUT_RAW, 40)
request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_SYS_STATUS, 40)
request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_POWER_STATUS, 40)
request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_VIBRATION, 40)

# Get the messages and reset intervals periodically
start_time = time.time()
while True:
    try:
        # Reset message intervals every 15 seconds
        if time.time() - start_time > 20:
            request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_RC_CHANNELS, 40)
            request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_VFR_HUD, 40)
            request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_GPS_RAW_INT, 40)
            request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_SERVO_OUTPUT_RAW, 40)
            request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_SYS_STATUS, 40)
            request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_POWER_STATUS, 40)
            request_message_interval(master, mavutil.mavlink.MAVLINK_MSG_ID_VIBRATION, 40)
            start_time = time.time()
        msg = master.recv_match(blocking=True, timeout=1)
        if msg is None:
            print("No message received")
            continue

        msg_dict = msg.to_dict()

        if msg.get_type() == 'RC_CHANNELS':
            print(f"RC_CHANNELS: {msg_dict}")

        elif msg.get_type() == 'VFR_HUD':
                print(f"VFR_HUD: {msg_dict}")
                """for key, value in msg_dict.items():
                    if key == 'airspeed':
                        print(key, ':', value, '------------------------------')"""

        elif msg.get_type() == 'GPS_RAW_INT':
            print(f"GPS_RAW_INT: {msg_dict}")

        elif msg.get_type() == 'SERVO_OUTPUT_RAW':
            print(f"SERVO_OUTPUT_RAW: {msg_dict}")

        elif msg.get_type() == 'SYS_STATUS':
            print(f"SYS_STATUS: {msg_dict}")

        elif msg.get_type() == 'POWER_STATUS':
            print(f"POWER_STATUS: {msg_dict}")

        elif msg.get_type() == 'VIBRATION':
            print(f"VIBRATION: {msg_dict}")

    except Exception as e:

        print(f"Error: {e}")

