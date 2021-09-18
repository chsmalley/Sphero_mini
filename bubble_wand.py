import sys
from .kano_wand.kano_wand import Wand
from typing import Any
from bluepy.btle import DefaultDelegate, Scanner
import RPi.GPIO as GPIO


class BubbleWand(Wand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pwm_pin = 18  # Broadcom pin 18 (P1 pin 12)
        GPIO.setup(self.pwm_pin, GPIO.OUT)  # PWM pin set as output
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


class BubbleWandScanner(DefaultDelegate):
    """A scanner class to connect to wands
    """
    def __init__(
        self,
        kano_mac: str,
        debug: bool=False
    ):
        """Create a new scanner

        Keyword Arguments:
            wand_class {class} -- Class to use when connecting
                                  to wand (default: {Wand})
            debug {bool} -- Print debug messages (default: {False})
        """
        super().__init__()
        self.wand_class = BubbleWand
        self.debug = debug
        self._kano_mac = kano_mac
        self.kano_device = None
        self.wand = None
        self._scanner = Scanner().withDelegate(self)

    def scan(
        self,
        timeout: float=1.0,
        connect: bool=False
    ):
        """Scan for devices

        Keyword Arguments:
            timeout {float} -- Timeout before returning from scan
                               (default: {1.0})
            connect {bool} -- Connect to the wands automatically
                              (default: {False})

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
            if self.kano_device is not None:
                if self.debug:
                    print("creating bubble wand")
                self.wand = BubbleWand(device,
                                       sphero_mac=self._sphero_mac,
                                       debug=self.debug)


if __name__ == '__main__':
    print("On Linux, use 'sudo hcitool lescan' to find your Sphero Mini's MAC address")
    kano_mac = sys.argv[1]
    # Create a new wand scanner
    shop = BubbleWandScanner(kano_mac)
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
    print("end of main")
