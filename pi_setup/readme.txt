(On later raspberry pi os - you may want to create a python virtual environment....)
  python3 -m venv <path>
where <path> is the directory you want to put the environment in.

Then run 
source  <path>/bin/activate 
.. to start the venv each time you start a new terminal or debug session
That makes sure that pip etc point to the versions in the virtual environment - then you don't need to use "sudo"



# Install binka
# This gets support for gpi pins and things like that
https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi


----------------------------------
cd ~
pip3 install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo -E env PATH=$PATH python3 raspi-blinka.py

# Install servo support
sudo pip3 install adafruit-circuitpython-servokit


# Support for the gyros 
#.. smbus is an extension/subset of the I2C interface
#.. See https://www.kernel.org/doc/html/latest/i2c/summary.html
sudo apt install python3-smbus
# library for the mpu6050 itself (Use <path>/bin/pip if you have a venv (virtual environment))
sudo pip install mpu6050-raspberrypi
# 