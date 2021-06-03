import sphero_mini
import sys
from kano_wand.kano_wand import Shop, Wand, PATTERN
import moosegesture


class SpheroWand(Wand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pressed = False
        self.positions = []
        self.sphero_mac = 

    def post_connect(self):
        
        # Connect to sphero
        if len(sys.argv) < 2:
            print("Usage: 'python [this_file_name.py] [sphero MAC address]'")
            print("eg f2:54:32:9d:68:a4")
            print("On Linux, use 'sudo hcitool lescan' to find your Sphero Mini's MAC address")
            sphero = None
        else:
            MAC = sys.argv[1] # Get MAC address from command line argument
            sphero = init_sphero(MAC)
        self.subscribe_button()
        self.subscribe_position()

    def on_position(self, x, y, pitch, roll):
        if self.pressed:
            # Add the mouse's position to the positions array
            self.positions.append(tuple([x, -1 * y]))

    def on_button(self, pressed):
        self.pressed = pressed

        if not pressed:
            # If releasing the button, print out the gestures and reset the positions
            gesture = moosegesture.getGesture(self.positions)
            self.positions = []

            print(gesture)
            # If it is a counterclockwise circle disconnect the wand
            if gesture == ['R', 'UR', 'U', 'UL', 'L', 'DL', 'D', 'DR', 'R']:
                self.disconnect()

def init_sphero(MAC: str) -> sphero_mini.sphero_mini:
    # Connect:
    sphero = sphero_mini.sphero_mini(MAC, verbosity = 1)

    # battery voltage
    sphero.getBatteryVoltage()
    print(f"Bettery voltage: {sphero.v_batt}v")

    # firmware version number
    sphero.returnMainApplicationVersion()
    print(f"Firmware version: {'.'.join(str(x) for x in sphero.firmware_version)}")

    #Configure sensors to make IMU_yaw values available
    sphero.configureSensorMask(
        # sample_rate_divisor = 0x25, # Must be > 0
        # packet_count = 0,
        IMU_pitch = True,
        IMU_roll = True,
        IMU_yaw = True,
        IMU_acc_x = True,
        IMU_acc_y = True,
        IMU_acc_z = True,
        IMU_gyro_x = True,
        IMU_gyro_y = True,
        IMU_gyro_z = True
    )
    sphero.configureSensorStream()
    return sphero


if __name__ == '__main__':
    # Create a new wand scanner
    # shop = Shop(wand_class=SpheroWand, debug=debug)
    wand = SpheroWant()
    wands = []
    try:
        # While we don't have any wands
        while len(wands) == 0:
            print("Scanning...")
            # Scan for wands and automatically connect
            wands = shop.scan(connect=True)
    # Detect keyboard interrupt and disconnect wands
    except KeyboardInterrupt as e:
        for wand in wands:
            wand.disconnect()

        while True:
            try:
                # Read wand 

                # if wand command send to sphero
                sphero.setLEDColor(red = 0, green = 255, blue = 0)
                sphero.roll(30, 0)
                
                # Else change color
                sphero.setLEDColor(red = 255, green = 0, blue = 0) # Turn LEDs green
            except KeyboardInterrupt:
                sphero.wait(1)  # Allow time to stop
                sphero.sleep()
                sphero.disconnect()
                break
