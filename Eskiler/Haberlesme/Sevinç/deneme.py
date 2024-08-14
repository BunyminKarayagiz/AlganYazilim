import dronekit
import path
connection_string = 'tcp:127.0.0.1:5762'
vehicle = dronekit.connect(connection_string, wait_ready=True)
saat=vehicle.gps_time.hour()
print(saat)
