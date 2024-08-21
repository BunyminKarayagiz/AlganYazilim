from pymavlink import mavutil
import time

#tcp:localhost:5762
iha = mavutil.mavlink_connection('udpin:localhost:14550')

iha.wait_heartbeat()
print('Heartbeat from system (system %u component %u)' %
    (iha.target_system,iha.target_component))

mainloop =True

while mainloop:
    timer=time.perf_counter()

    msg_VFR=iha.recv_match(type="VFR_HUD",blocking=True) #4HZ Calculated
    print("MSG-VFR",msg_VFR)
    print("Elapsed Time ->",time.perf_counter()-timer)

    msg_ATT=iha.recv_match(type="ATTITUDE",blocking=True) #4hz Calculated
    print("MSG-ATT",msg_ATT)
    print("Elapsed Time ->",time.perf_counter()-timer)

    #mainloop = False 