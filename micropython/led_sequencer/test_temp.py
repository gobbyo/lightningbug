from machine import Pin, I2C
from micropython_pca9685 import PCA9685
import time

PCA_SWITCH_PIN = 28  # Pin to control the PCA9685 modules

pcaswitch = Pin(PCA_SWITCH_PIN, Pin.OUT)
pcaswitch.off()  # PNP, turn on the PCA9685 modules
time.sleep(10)

i2c = I2C(1, sda=Pin(2), scl=Pin(3))
devices = i2c.scan()
print("I2C devices found:", devices)
pca = PCA9685(i2c, address = 0x43)
pca.frequency = 512
pca.channels[0].duty_cycle = 0x0FFF  # Set channel 0 to full brightness
time.sleep(1)  # Wait for 1 second to observe the change
pca.channels[0].duty_cycle = 0x0000  # Set channel 0 to off

pcaswitch.on()