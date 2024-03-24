# For command line options
import argparse

# For support checking buttons
from gpiozero import Button

# The main robot script
from robot import Robot

# For sleep etc
import time

EARLY_EXIT_PIN = 21

# Check if there is a connection from pin EARLY_EXIT_PIN to gnd
# if there is - exit.
# This allows the script to run on boot - but if that connection is present it wont
# continue and block execution of the startup script so you can edit things
def check_early_exit():
    early_exit = Button(EARLY_EXIT_PIN)
    if early_exit.is_pressed:
        print("Shut down robot code - use --run or connect pin 21 to gnd to run") 
        exit (0)
    
if __name__ == "__main__":
    # Setup some command line options
    parser = argparse.ArgumentParser(prog="robot_demo",
                      description="The hello world of th mecanum robot")
    parser.add_argument("-r", "--run",
                        action="store_true",
                        help="If set - ignore the auto-run button/jumper and execute anyway")
    parser.add_argument("-f", "--force-run",
                        action="store_true",
                        help="If set - enable switch and run under python control. Use with caution")
    
    opts = parser.parse_args()
    
    # Decide whether we should run or now based on cmdline argument and the AUTORUN button
    if not opts.run:
        check_early_exit()
    else:
        print("Run option set - ignore auto-run button and execute anyway")
    # Create a robot object - optional callback function which will be called
    # when control is handed over to the application from the remote
    # robot = Robot(callback = take_control)

    robot = Robot()

    # Set up any gpio pins you need - TX, RX and the I2C pins are already in use.
    try:
        print("Start main loop")
        print(f"Robot heading is {robot.get_heading()}")
        was_in_control = False
        print(f"{opts.force_run=}")
        # Which demo to run
        run_test = 1
        while True:
            if robot.get_in_control():
                # You can read the valuse from the remote control
                values = robot.get_ibus_values()
                robot._ibus.enable()


                if run_test == 1:
                    # Set the speed of the robot as needed - here we use the remote control
                    # values to set ....
                    # (Speed, turn, strafe)
                    # Values are all in the range -500 to 500
                    robot.set_motion( values['knob1'] - 1500,0,values['knob2'] - 1500)
            was_in_control = robot.get_in_control()
                # Note - it is important to change speeds slowly - otherwise the stepper motors
                # can't cope.
            time.sleep(0.1)
    except:
        robot.atexit()
