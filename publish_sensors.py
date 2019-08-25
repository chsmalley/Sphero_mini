import sphero_mini
import sys
import zmq
import random
import time


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
    port = "5556"
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:%s" % port)

    if len(sys.argv) < 2:
        print("Usage: 'python [this_file_name.py] [sphero MAC address]'")
        print("eg f2:54:32:9d:68:a4")
        print("On Linux, use 'sudo hcitool lescan' to find your Sphero Mini's MAC address")
        sphero = None
    else:
        MAC = sys.argv[1] # Get MAC address from command line argument
        sphero = init_sphero(MAC)

    while True:
        try:
            if sphero is not None:
                # Read sphero sensor
                yaw = sphero.IMU_yaw
                print("Yaw angle: {}".format(round(yaw, 3)))
                if yaw > 0:
                    sphero.setLEDColor(red = 0, green = 255, blue = 0) # Turn LEDs green
                else:
                    sphero.setLEDColor(red = 0, green = 0, blue = 255) # Turn LEDs green
            topic = 10000
            messagedata = random.randrange(1, 215) - 80
            print("{} {}".format(topic, messagedata))
            socket.send_string("%d %d" % (topic, messagedata))
            time.sleep(1)
        except KeyboardInterrupt:
            break
    print("program complete")
