
from robot import Robot
import time

if __name__ == "__main__":

    # Create a robot object - optional callback function which will be called
    # when control is handed over to the application from the remote
    # robot = Robot(callback = take_control)

    robot = Robot()

    # Set up any gpio pins you need - TX, RX and the I2C pins are already in use.

    print("Start main loop")
    print(f"Robot heading is {robot.get_heading()}")
    while True:
        if robot.get_in_control():
            # You can read the valuse from the remote control
            values = robot.get_ibus_values()
            print(f"Main application - in control {values['knob1']}")
            robot._ibus.enable()

            # Set the speed of the robot as needed - here we use the remote control
            # values to set ....
            # (Speed, turn, strafe)
            # Values are all in the range -500 to 500
            robot.set_motion( values['knob1'] - 1500,0,values['knob2'] - 1500)

            # Note - it is important to change speeds slowly - otherwise the stepper motors
            # can't cope.
        time.sleep(0.1)