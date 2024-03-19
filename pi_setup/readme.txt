# Install binka
https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi

cd ~
pip3 install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo -E env PATH=$PATH python3 raspi-blinka.py

# Install servo support
sudo pip3 install adafruit-circuitpython-servokit




sudo apt install python3-smbus
sudo pip install mpu6050-raspberrypi
# 