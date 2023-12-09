from pymavlink import mavutil

# os.system('dronekit-sitl plane --out tcp:127.0.0.1:5762')

master = mavutil.mavlink_connection('tcp:127.0.0.1:5762')
telemetri = {
    'enlem': 0.0,
    'boylam': 0.0,
    'yükseklik': 0.0,
    'yer_hızı': 0.0,
    'hava_hızı': 0.0,
    'roll': 0.0,
    'pitch': 0.0,
    'yaw': 0.0,
    'mode': 'Bilinmiyor'
}

mode_mapping = {
    0: "MANUAL",
    1: "CIRCLE",
    2: "STABILIZE",
    3: "TRAINING",
    4: "ACRO",
    5: "FBWA",
    6: "FBWB",
    7: "CRUISE",
    8: "AUTOTUNE",
    10: "AUTO",
    11: "RTL",
    12: "LOITER",
    13: "TAKEOFF",
    14: "AVOID_ADSB",
    15: "GUIDED",
    16: "INITIALISING",
    17: "QSTABILIZE",
    18: "QHOVER",
    19: "QLOITER",
    20: "QLAND",
    21: "QRTL",
    22: "QAUTOTUNE",
    23: "QACRO",
    24: "THERMAL"
}

while True:

    msg = master.recv_match(blocking=True)
    if msg.get_type() == 'GPS_RAW_INT':
        enlem = msg.lat / 10000000
        boylam = msg.lon / 10000000
    elif msg.get_type() == 'GLOBAL_POSITION_INT':
        yukseklik = msg.relative_alt / 1000
    elif msg.get_type() == 'VFR_HUD':
        yer_hizi = msg.groundspeed
        hava_hizi = msg.airspeed
    elif msg.get_type() == 'SYS_STATUS':
        batarya = msg.battery_remaining
    elif msg.get_type() == 'ATTITUDE':
        roll = msg.roll
        pitch = msg.pitch
        yaw = msg.yaw
    elif msg.get_type() == 'HEARTBEAT':
        custom_mode = msg.custom_mode
        mod = mode_mapping.get(custom_mode, str(custom_mode))
    telemetri = {
            "Emlen:": float(enlem),
            "Boylam": float(boylam),
            "Yükseklik": float(yukseklik),
            "Yer_Hızı": float(yer_hizi),
            "hava hızı": float(hava_hizi),
            "roll": float(roll),
            "pitch": float(pitch),
            "yaw": float(yaw),
            "mode": str(mod)
        }