from ibus_encode import ibus_encode
import serial
import struct
import time

uart = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=3.0)
ibus = ibus_encode(uart)

# List a set of "commands" to send one by one
script = [
    {"speed":0.05,     "turn": 0.0,     "strafe": 0.0,   "duration": 1},
    {"speed":0.10,     "turn": 0.0,     "strafe": 0.0,   "duration": 1},
    {"speed":0.15,     "turn": 0.0,     "strafe": 0.0,   "duration": 1},
    {"speed":0.20,     "turn": 0.0,     "strafe": 0.0,   "duration": 1},
    {"speed":0.15,     "turn": 0.0,     "strafe": 0.0,   "duration": 1},
    {"speed":0.10,     "turn": 0.0,     "strafe": 0.0,   "duration": 1},
    {"speed":0.05,     "turn": 0.0,     "strafe": 0.0,   "duration": 1},
    {"speed":0.0,      "turn": 0.0,     "strafe": 0.0,   "duration": 1},]

# Turn on the motors
ibus.enable()
    
for command in script:
    print(f"{command=}")
    # Send the command to the robot.
    # Replace this with real controls
    ibus.move(command["speed"], command["turn"], command["strafe"])
    time.sleep(command["duration"])


# More commands with bigger changes in speeds. These would be a problem
# for the robot to suddenly change to, so we use the acceleration method
# to steadily change the speed over a period of time
script = [
    {"speed":0.25,     "turn": 0.0,     "strafe": 0.0,   "duration": 2},
    {"speed":0.00,     "turn": 0.25,     "strafe": 0.0,   "duration": 2},
    {"speed":0.0,     "turn": 0.0,     "strafe": 0.25,   "duration": 2},
    {"speed":1.0,     "turn": 0.0,     "strafe": 0.0,   "duration": 5},
    {"speed":0.5,     "turn": -0.5,     "strafe": 0.0,   "duration": 5},
    ]

# Repeat the commands, but using the acceleration method to smooth things out 
for command in script:
    print(f"{command=}")
    # Send the command to the robot.
    # Replace this with real controls
    ibus.accel(command["speed"], command["turn"], command["strafe"], command["duration"])
    # Each call to accel takes some time - so we don't sleep here
    
# Turn off the motors    
ibus.disable()