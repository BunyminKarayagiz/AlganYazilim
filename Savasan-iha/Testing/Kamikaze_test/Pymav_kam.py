from pymavlink import mavutil
import time

def arm_plane(plane):
    plane.mav.command_long_send(plane.target_system, plane.target_component,400, 0 ,1 ,21196, 0 ,0, 0, 0 ,0)
    msg = plane.recv_match(type="COMMAND_ACK",blocking=True)
    print(msg)

def disarm_plane(plane):
    plane.mav.command_long_send(plane.target_system, plane.target_component,400, 0 ,0 ,21196 , 0 ,0, 0, 0 ,0)
    msg = plane.recv_match(type="COMMAND_ACK",blocking=True)
    print(msg)

def takeoff(plane):
    plane.mav.command_long_send(plane.target_system,plane.target_component,mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,0,   0,0,0,0,0,0,10)
    msg = plane.recv_match(type="COMMAND_ACK",blocking=True)
    print(msg)

def change_mod(plane):
    # message COMMAND_LONG 0 0 176 0 1 6 0 0 0 0 0
    plane.mav.command_long_send(plane.target_system, plane.target_component, mavutil.mavlink.MAV_CMD_DO_SET_MODE,0,1,10,0,0,0,0,0)
    msg = plane.recv_match(type="COMMAND_ACK",blocking=True)
    print(msg)


if __name__ == "__main__":
    #tcp:localhost:5762
    iha = mavutil.mavlink_connection('tcp:localhost:5763')
    iha.wait_heartbeat()
    print('Heartbeat from system (system %u component %u)',(iha.target_system,iha.target_component))
    change_mod(iha)
    mainloop =True
    time.sleep(5)
    while mainloop:
        timer=time.perf_counter()

        

        #disarm_plane(iha)

        # msg_VFR=iha.recv_match(type="VFR_HUD",blocking=True) #4hz Calculated
        # print("MSG-VFR",msg_VFR)
        # print("Elapsed Time ->",time.perf_counter()-timer)

        # msg_ATT=iha.recv_match(type="ATTITUDE",blocking=True) #4hz Calculated
        # print("MSG-ATT",msg_ATT)
        # print("Elapsed Time ->",time.perf_counter()-timer)

        
        print("loop")
        time.sleep(1)
        #mainloop = False