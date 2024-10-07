import time
import logging
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.utils.multiranger import Multiranger
from cflib.utils import uri_helper

URI = 'radio://0/98/2M2M/E7E7E7E8'
uri = uri_helper.uri_from_env(default='radio://0/98/2M2M/E7E7E7E8')

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

distance = 0.05  # Detects if there is an obstacle 0.05 meters from the drone
below = 0.3  # Detects if the drone is below 0.3 meters from the ground

def is_close(range, threshold = distance):
    if range is None:
        return False
    else:
        return range < threshold

def box_detected(range, threshold = below):
    if range is None:
        return False
    else:
        return range < threshold

def to_landing(scf):
    with MotionCommander(scf) as mc:
        with PositionHlCommander(scf) as pc:
            with Multiranger(scf) as multiranger:
                while True:
                    if box_detected(multiranger.down):  # If there is a box under the drone, it will land
                        mc.land()
                        break

                    if is_close(multiranger.front):  # Obstacle detection in front of drone
                        mc.stop()  # Stop and hover if an obstacle is detected
                        pc.right(0.05)  # Move 0.05 meters to the right
                        time.sleep(0.5)
                        pc.back(0.05)  # Move 0.05 meter back
                        time.sleep(0.5)

                    elif is_close(multiranger.right):  # Obstacle detection to right of drone
                        mc.stop()  # Stop and hover if obstacle is detected
                        pc.left(0.05)  # Move 0.2m to left
                        time.sleep(0.5)

                    elif is_close(multiranger.left):  # Obstacle detection to left of drone
                        mc.stop()  # Stop and hover if obstacle is detected
                        pc.right(0.05)  # Move 0.2m to right
                        time.sleep(0.5)
                    else:
                        mc.forward()  # Move forward if no obstacle is detected
                        time.sleep(0.5)

                    time.sleep(0.1)  # Check every 0.1 seconds

def to_start(scf):
    with MotionCommander(scf) as mc:
        with PositionHlCommander(scf) as pc:
            with Multiranger(scf) as multiranger:
                while True:
                    if box_detected(multiranger.down):
                        mc.land()
                        break

                    if is_close(multiranger.back):
                        mc.stop()
                        pc.left(0.2)
                        time.sleep(0.5)
                        pc.forward(0.1)
                        time.sleep(0.5)

                    elif is_close(multiranger.left):
                        mc.stop()
                        pc.right(0.2)
                        time.sleep(0.5)

                    elif is_close(multiranger.right):
                        mc.stop()
                        pc.left(0.2)
                        time.sleep(0.5)

                    else:
                        mc.back()
                        time.sleep(0.5)
                    time.sleep(0.1)

if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)

    cf = Crazyflie(rw_cache='./cache')
    
    with SyncCrazyflie(URI, cf=cf) as scf:
        # Initial actions
        with MotionCommander(scf) as mc:
            print("Taking off...")
            mc.take_off(0.2)  # Hover at 0.2 meters
            time.sleep(1)     # Hover for 1 second
            print("Moving forward...")
            mc.forward()      # Move forward
            time.sleep(1.5)   # Move forward for 1.5 seconds

        # Call functions for obstacle detection and landing
        to_landing(scf)
        to_start(scf)
