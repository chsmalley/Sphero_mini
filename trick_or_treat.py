import sys
from gpiozero import Motor, Button
import time


def trick_or_treat():
    # Setup motors
    candy_motor = Motor(forward=4, backward=14)
    bubble_motor = Motor(forward=17, backward=27)
    # Setup buttons
    candy_button = 
    bubble_button = 
    # main loop
    try:
        while True:
            if 
    except KeyboardInterrupt:
        candy_motor.stop()
        bubble_motor.stop()
    self.candy_motor.forward()
    self.bubble_motor.forward()
    time.sleep(2)
    self.candy_motor.stop()
    self.bubble_motor.stop()

    def on_position(self, x, y, pitch, roll):
        if self.pressed:
            # Add the mouse's position to the positions array
            self.positions.append(tuple([x, -1 * y]))

    def on_button(self, pressed):
        print(f"on_button: {pressed}")
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
