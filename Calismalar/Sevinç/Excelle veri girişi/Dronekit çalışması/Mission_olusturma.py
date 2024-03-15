import dronekit
from dronekit import VehicleMode , connect, Command
import time
home_location= (40.231981,	29.0037938)
target_locations=((40.2333464,	29.0041423 ,50),
                  (40.2312659,	29.0037775,50),
                  (40.2309219,	29.0093350,50),
                  (40.2330515,	29.0100861,50))

iha=connect('tcp:127.0.0.1:5762')
print("iha bağlandı")
mission_items=iha.commands
mission_items.download()
print('mission items downloaded')
mission_items.wait_ready()
print('mission items ready')
mission_items.clear()
print('mission items cleared')

mission_item=Command( 0, 0, 0,
                        dronekit.mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                        dronekit.mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
                        0, 0, 0, 0, 0, 0, 0, 0, 50)
print('mission item created')
mission_items.add(mission_item)
#navigation locations

for location in target_locations:
    mission_item=dronekit.Command( 0, 0, 0,
                                   dronekit.mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                   dronekit.mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                                   0, 0, 50, 50, 0, 0, location[0], location[1], location[2])
    print("şu anda eklenecek olan konum: ",location)
    mission_items.add(mission_item)

mission_items.add(mission_item)
print("do jump eklendi ")

mission_items.upload()
#uploaded mission

#start mission
while not iha.mode !='TAKEOFF':
    iha.mmode=VehicleMode('TAKEOFF')
    print("iha takeoff moduna alıniyor")
    time.sleep(1)
print(iha.mode)
iha.simple_takeoff(50)
while iha.location.global_relative_frame.alt<48:
    print('iha yüksekliği: ',iha.location.global_relative_frame.alt)
    time.sleep(1)
while iha.mode !='AUTO':
    iha.mode=VehicleMode('AUTO')
    print('iha auto moduna alınıyor')
    time.sleep(1)
while iha.location.global_relative_frame.alt<50:
    print('iha yüksekliği: ',iha.location.global_relative_frame.alt)
    time.sleep(1)
iha.mode=dronekit.VehicleMode('AUTO')
while True:
    iha.mode=VehicleMode('AUTO')



