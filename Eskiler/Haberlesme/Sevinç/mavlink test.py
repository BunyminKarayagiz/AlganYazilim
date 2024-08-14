from pymavlink import mavutil  # gerekli olan kütüphane yüklenir
master = mavutil.mavlink_connection('tcp:port='10.80.1.63:14450')
while True:
    msg = master.recv_match()
    if msg.get_type() == 'GPS_TIME':
        print(msg)