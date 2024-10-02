import time
import logging
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander

# URI to the Crazyflie to connect to
URI = 'radio://0/98/2M/E7E7E7E7E8'

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

if __name__ == '__main__':
    # Initialize the low-level drivers
    cflib.crtp.init_drivers(enable_debug_driver=False)

    # Create a Crazyflie instance
    cf = Crazyflie(rw_cache='./cache')

    # Connect to the Crazyflie using the SyncCrazyflie context manager
    with SyncCrazyflie(URI, cf=cf) as scf:
        # Use the MotionCommander to control the drone
        with MotionCommander(scf) as mc:
            print("Taking off...")
            mc.take_off(0.5)  # Hover at 0.5 meters
            time.sleep(5)     # Hover in place for 5 seconds
            
            print("Landing...")
            mc.land()
            print("Landed!")
