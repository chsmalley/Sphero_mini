import sys
from gpiozero import Motor, Button
import time

CANDY_TIME = 2
BUBBLE_TIME = 2

def trick_or_treat():
    # Setup motors
    candy_motor = Motor(forward=4, backward=14)
    bubble_motor = Motor(forward=17, backward=27)
    # Setup buttons
    candy_button = Button(2)
    bubble_button = Button(3)
    # main loop
    try:
        while True:
            if candy_button.is_pressed:
                print("candy button pressed")
                self.candy_motor.forward()
                time.sleep(CANDY_TIME)
                self.candy_motor.stop()
            elif bubble_button.is_pressed:
                print("bubble button pressed")
                self.bubble_motor.forward()
                time.sleep(BUBBLE_TIME)
                self.bubble_motor.stop()
    except KeyboardInterrupt:
        candy_motor.stop()
        bubble_motor.stop()


if __name__ == '__main__':
    print("Welcome trick or treaters")
    trick_or_treat()
