from pymavlink import mavutil

def set_rc_channel_pwm(channel_id, pwm=1500):
    """ Set RC channel pwm value
    Args:
        channel_id (TYPE): Channel ID
        pwm (int, optional): Channel pwm value 1100-1900
    """
    if channel_id < 1 or channel_id > 18:
        print("Channel does not exist.")
        return

    # Mavlink 2 supports up to 18 channels:
    # https://mavlink.io/en/messages/common.html#RC_CHANNELS_OVERRIDE
    rc_channel_values = [65535 for _ in range(18)]
    rc_channel_values[channel_id - 1] = pwm
    master.mav.rc_channels_override_send(
        master.target_system,                # target_system
        master.target_component,             # target_component
        *rc_channel_values)                  # RC channel list, in microseconds.


if __name__=="__main__":

    master = mavutil.mavlink_connection('/dev/ttyAMA0')
    master.wait_heartbeat()
    print("Heartbeat from system (system %u component %u)" % (master.target_system, master.target_component))

    abc=input("CHANNEL")

    if abc == "1":
        set_rc_channel_pwm(channel_id=1,pwm=1500)
        set_rc_channel_pwm(channel_id=2,pwm=1500)
        set_rc_channel_pwm(channel_id=3,pwm=1100)
        set_rc_channel_pwm(channel_id=4,pwm=1700)
        set_rc_channel_pwm(channel_id=5,pwm=1300)
    if abc == "2":
        set_rc_channel_pwm(channel_id=1,pwm=1500)
        set_rc_channel_pwm(channel_id=2,pwm=1500)
        set_rc_channel_pwm(channel_id=3,pwm=1100)
        set_rc_channel_pwm(channel_id=4,pwm=1300)
        set_rc_channel_pwm(channel_id=5,pwm=1700)
    if abc == "3":
        set_rc_channel_pwm(channel_id=1,pwm=1500)
        set_rc_channel_pwm(channel_id=2,pwm=1500)
        set_rc_channel_pwm(channel_id=3,pwm=1100)
        set_rc_channel_pwm(channel_id=4,pwm=1500)
        set_rc_channel_pwm(channel_id=5,pwm=1500)
    if abc == "4":
        set_rc_channel_pwm(channel_id=1,pwm=1500)
        set_rc_channel_pwm(channel_id=2,pwm=1500)
        set_rc_channel_pwm(channel_id=3,pwm=1100)
        set_rc_channel_pwm(channel_id=4,pwm=1700)
        set_rc_channel_pwm(channel_id=5,pwm=1300)
    if abc == "5":
        set_rc_channel_pwm(channel_id=5,pwm=1900)
    if abc == "6":
        set_rc_channel_pwm(channel_id=1,pwm=1100)
    if abc == "7":
        set_rc_channel_pwm(channel_id=2,pwm=1100)
    if abc == "8":
        set_rc_channel_pwm(channel_id=3,pwm=1100)
    if abc == "9":
        set_rc_channel_pwm(channel_id=4,pwm=1100)
    if abc == "10":
        set_rc_channel_pwm(channel_id=5,pwm=1100)