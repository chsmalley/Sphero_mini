from bluepy.btle import UUID, Peripheral
from sphero_constants import *
import binascii
import time

class sphero_mini():
    def __init__(self, MACAddr):
        '''
        initialize class instance and then build dictionaries of BLE sevices and characteristics.
        Also sends text string to Anti-DOS characteristic to prevent returning to sleep.
        '''
        self.sequence = 1

        self.p = Peripheral(MACAddr, "random") #connect

        #Use Bluepy methods to create service and characteristic objects
        self.svc = {"API V2 Service": self.p.getServiceByUUID("00010001574f4f2053706865726f2121"),
                    "Nordic DFU Service": self.p.getServiceByUUID("00020001574f4f2053706865726f2121")}
        self.characteristics = dict(zip(characteristicNames, self.p.getCharacteristics()))

        # The following command seems be necessary to prevent the sphero mini from going to sleep again after 10 seconds
        self.characteristics["Anti DOS"].write("usetheforce...band".encode())
    def disconnect(self):
        self.p.disconnect()

    def _send(self, characteristic=None, devID=None, commID=None, payload=[]):
        '''
        A generic "send" method, which will be used by other methods to send a command ID, payload and
        appropriate checksum to a specified device ID. Mainly useful because payloads are optional,
        and can be of varying length, to convert packets to binary, and calculate and send the
        checksum. For internal use only.
        '''
        self.sequence += 1 # Increment sequence number (I am not sure that this is necessary, but probably good practice)
        sendBytes = [sendPacketConstants["StartOfPacket"],
                    sum([flags["resetsInactivityTimeout"],flags["requestsResponse"]]),
                    devID,
                    commID,
                    self.sequence] + payload

        # Compute and append checksum and EOP byte:
        # From Sphero docs: "The [checksum is the] modulo 256 sum of all the bytes
        #                   from the device ID through the end of the data payload,
        #                   bit inverted (1's complement)"
        checksum = 0
        for num in sendBytes[1:]:
            checksum = (checksum + num) & 0xFF # bitwise "and to get modulo 256 sum of appropriate bytes
        checksum = 0xff - checksum # bitwise 'not' to invert checksum bits
        sendBytes += [checksum, sendPacketConstants["EndOfPacket"]] #append

        # Convert to bytes type object
        for byteIndex in range(len(sendBytes)):
            sendBytes[byteIndex] = sendBytes[byteIndex].to_bytes(1, byteorder='big')
        output = b"".join(sendBytes)

        #send to specifiec characteristic:
        characteristic.write(output)
        time.sleep(0.1) # short pause because it seems that successive commands collide with each other

    def wake(self):
        '''
        Bring device out of sleep mode
        '''
        self._send(characteristic=self.characteristics["API V2"],
                   devID=deviceID['powerInfo'],
                   commID=powerCommandIDs["wake"],
                   payload=[]) #empty payload

    def sleep(self, deepSleep=False):
        '''
        Put device to sleep or deep sleep (deep sleep needs USB power connected to wake up)
        '''
        if deepSleep:
            sleepCommID=powerCommandIDs["deepSleep"]
        else:
            sleepCommID=powerCommandIDs["sleep"]
        self._send(characteristic=self.characteristics["API V2"],
                   devID=deviceID['powerInfo'],
                   commID=sleepCommID,
                   payload=[]) #empty payload

    def setLEDColour(self, red = None, green = None, blue = None):
        '''
        Set device LED colour based on RGB vales (each can  range between 0 and 0xFF)
        '''
        self._send(characteristic = self.characteristics["API V2"],
                  devID = deviceID['userIO'],
                  commID = userIOCommandIDs["allLEDs"],
                  payload = [0x00, 0x70, red, green, blue]) #no idea where the 0x00 or 0x70 come from - borrowed from igbopie's code

    def roll(self, speed=None, heading=None):
        '''
        Start to move the Sphero at a given direction and speed.
        heading: integer from 0 - 360 (degrees)
        speed: Integer from 0 - 255

        NOTE: Aiming has not yet been implemented, so the Sphero will likely begin to move
        in a seemingly random direction (not actuallly random because the device probably wasn't
        pointing at zero degrees when you started)
        '''
        if speed < 0 or speed > 255:
            print("WARNING: roll speed argument outside of allowed range")

        speedH = (speed & 0xFF00) >> 8
        speedL = speed & 0xFF
        headingH = (heading & 0xFF00) >> 8
        headingL = heading & 0xFF
        self._send(characteristic = self.characteristics["API V2"],
                  devID = deviceID['driving'],
                  commID = drivingCommands["driveWithHeading"],
                  payload = [speedL, speedH, headingL, headingH])

    def setBackLEDIntensity(self, brightness=None):
        '''
        Set device LED backlight intensity based on 0-255 values

        NOTE: this is not the same as aiming - it only turns on the LED
        '''
        self._send(characteristic = self.characteristics["API V2"],
                  devID = deviceID['userIO'],
                  commID = userIOCommandIDs["allLEDs"],
                  payload = [0x00, 0x01, brightness]) #no idea where the 0x00 or 0x70 come from - borrowed from igbopie's code
