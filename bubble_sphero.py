import sphero_mini
import sys
from .kano_wand.kano_wand import Wand
import moosegesture
from typing import Any
from bluepy.btle import DefaultDelegate, Scanner
import RPi.GPIO as GPIO


class BubbleWand(Wand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pwm_pin = 18  # Broadcom pin 18 (P1 pin 12)
        GPIO.setup(self.pwm_pin, GPIO.OUT) # PWM pin set as output
        self.pwm = GPIO.PWM(self.pvm_pin, 50)
        self.duty_cycle
        self.pwm.start(self.duty_cycle)
        
    def post_connect(self):
        self.subscribe_button()

    def on_position(self, x, y, pitch, roll):
        if self.pressed:
            # Add the mouse's position to the positions array
            self.positions.append(tuple([x, -1 * y]))

    def on_button(self, pressed):
        self.pressed = pressed


def control_sphero_gesture(
    sphero: sphero_mini.sphero_mini,
    gesture: str
) -> None:
    heading = 0
    speed = 0
    if "R" in gesture:
        heading += 50
    if "L" in gesture:
        heading -+ 50
    if "U" in gesture:
        speed += 100
    if "D" in gesture:
        speed -= 100
    sphero.roll(speed, heading)
    sphero.wait(2)  # Keep rolling for two seconds


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


class WandSpheroScanner(DefaultDelegate):
    """A scanner class to connect to wands
    """
    def __init__(
        self,
        kano_mac: str,
        sphero_mac: str,
        debug: bool=False
    ):
        """Create a new scanner

        Keyword Arguments:
            wand_class {class} -- Class to use when connecting to wand (default: {Wand})
            debug {bool} -- Print debug messages (default: {False})
        """
        super().__init__()
        self.wand_class = SpheroWand
        self.debug = debug
        self._kano_mac = kano_mac
        self._sphero_mac = sphero_mac
        self.kano_device = None
        self.sphero_device = None
        self.wand = None
        self._scanner = Scanner().withDelegate(self)

    def scan(
        self,
        timeout: float=1.0,
        connect: bool=False
    ):
        """Scan for devices

        Keyword Arguments:
            timeout {float} -- Timeout before returning from scan (default: {1.0})
            connect {bool} -- Connect to the wands automatically (default: {False})

        Returns {Wand} -- wand objects
        """

        if self.debug:
            print("Scanning for {} seconds...".format(timeout))

        self._scanner.scan(timeout)
        if connect:
            self.wand.connect()
        return self.wand

    def handleDiscovery(self, device, isNewDev, isNewData):
        """Check if the device matches

        Arguments:
            device {bluepy.ScanEntry} -- Device data
            isNewDev {bool} -- Whether the device is new
            isNewData {bool} -- Whether the device has already been seen
        """

        if isNewDev:
            # Perform initial detection attempt
            if device.addr == self._kano_mac:
                self.kano_device = device
                if self.debug:
                    print("found kano wand")
            if device.addr == self._sphero_mac:
                self.sphero_device = device
                if self.debug:
                    print("found sphero device")
            if self.kano_device is not None and self.sphero_device is not None:
                if self.debug:
                    print("creating sphero wand")
                self.wand = SpheroWand(device,
                                       sphero_mac=self._sphero_mac,
                                       debug=self.debug)


if __name__ == '__main__':
    print("On Linux, use 'sudo hcitool lescan' to find your Sphero Mini's MAC address")
    kano_mac = sys.argv[1]
    sphero_mac = sys.argv[2]
    # Create a new wand scanner
    shop = WandSpheroScanner(kano_mac, sphero_mac)
    wand = None
    try:
        # While we don't have any wands
        while wand is None:
            print("Scanning...")
            # Scan for wands and automatically connect
            wand = shop.scan(connect=True)
            print("after scan")
        print("out of while loop")
    # Detect keyboard interrupt and disconnect wands
    except KeyboardInterrupt as e:
        wand.disconnect()
