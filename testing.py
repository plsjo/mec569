import time
import logging
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.utils.multiranger import Multiranger
from cflib.utils import uri_helper

URI = 'radio://0/98/2M/8'
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
    
def move():
    cf = Crazyflie(rw_cache='./cache')
    with SyncCrazyflie(URI, cf=cf) as scf:
            with MotionCommander(scf) as mc:
                with PositionHlCommander(scf) as pc:
                    with Multiranger(scf) as multiranger:
                        mc.take_off(0.2) 
                        time.sleep(1)#hover at 0.2 meters for 1 second
                        mc.forward()
                        time.sleep(1.5) #move forward for 1.5 seconds to move away from starting box

                        while True:
                            if box_detected(multiranger.down): #detects if there is a box under the drone
                                mc.land() #lands if there is a box
                                break
                            
                            if is_close(multiranger.front): #detects if there is an obstacle in front of the drone
                                mc.stop()
                                time.sleep(0.5) #stops for 0.5 seconds
                                if is_close(multiranger.left): #if obstacle to left of drone
                                    mc.right(0.1) #then move to the right by 0.1m
                                elif is_close(multiranger.right): #if obstacle to right of drone
                                    mc.left(0.1) #then move to left by 0.1m
                                else:
                                    mc.stop #if no obstacle detected
                                    time.sleep(0.5) #hover for 0.5 seconds

                            else:
                                mc.forward() #move forward if no obstacles are detected

                            time.sleep(0.1)

if __name__ == '__main__':
    cflib.crtp.init_drivers()
    
    move()