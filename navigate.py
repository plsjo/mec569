import time
import logging
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.utils.multiranger import Multiranger
from cflib.utils import uri_helper

URI = 'radio://0/98/2M2M/E7E7E7E7E8'
uri = uri_helper.uri_from_env(default='radio://0/98/2M2M/E7E7E7E7E8')

#Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

def is_close(range):
    distance = 0.1 #detects if there is an obstacle 0.1 meters in front of drone
    if range is None:
        return False
    else:
        return range < distance

def box_detected(range):
    below = 0.3 #detects if the drone is below 0.3 meters from the ground
    if range is None:
        return False
    else:
        return range < below

def to_landing():
    cf = Crazyflie(rw_cache='./cache')
    with SyncCrazyflie(URI, cf=cf) as scf:
            with MotionCommander(scf) as mc:
                with PositionHlCommander(scf) as pc:
                    with Multiranger(scf) as multiranger:
                        mc.take_off(0.2) 
                        time.sleep(1)#hover at 0.2 meters for 1 second
                        mc.forward()
                        time.sleep(1.5) #move forward for 1.5 seconds
                    
                        while True:
                            if box_detected(multiranger.down): #if there is a box under the drone, it will land
                                mc.land()
                                break

                            if is_close(multiranger.front): #obstacle detection in front of drone
                                mc.stop() #Stop and hover if an obstacle is detected
                                pc.right(0.2) #Move 0.2 meters to the right
                                pc.back(0.1) #Move 0.1 meter back

                            elif is_close(multiranger.right): #obstacle detection to right of drone
                                mc.stop() #Stop and hover if obstacle is detected
                                pc.left(0.2) #Move 0.2m to left

                            elif is_close(multiranger.left): #obstacle detection to left of drone
                                mc.stop() #Stop and hover if obstacle is detected
                                pc.right(0.2) #Move 0.2m to right
                            
                            else:
                                mc.forward() #Move forward if no obstacle is detected
                            time.sleep(0.1)  #Check every 0.1 seconds

def to_start():
    cf = Crazyflie(rw_cache='./cache')
    with SyncCrazyflie(URI, cf=cf) as scf:
            with MotionCommander(scf) as mc:
                with PositionHlCommander(scf) as pc:
                    with Multiranger(scf) as multiranger:
                        mc.take_off(0.2)
                        time.sleep(1) #Hover at 0.2m for 1 second
                        mc.back()
                        time.sleep(1.5) #Move left for 1.5 seconds

                        while True:
                            if box_detected(multiranger.down):
                                mc.land()
                                break
                            
                            if is_close(multiranger.back):
                                mc.stop()
                                pc.left(0.2)
                                pc.forward(0.1)

                            elif is_close(multiranger.left):
                                mc.stop()
                                pc.right(0.2)

                            elif is_close(multiranger.right):
                                mc.stop()
                                pc.left(0.2)

                            else:
                                mc.back()
                            time.sleep(0.1)

if __name__ == '__main__':
    #Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)

    to_landing()
    to_start()