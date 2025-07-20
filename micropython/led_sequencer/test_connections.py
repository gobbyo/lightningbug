from machine import Pin, I2C
from micropython_pca9685 import PCA9685
import time

PCA_SWITCH_PIN = 28  # Pin to control the PCA9685 modules
# Board configuration - Change this to match your microcontroller
BOARD_TYPE = "XIAO_RP2040"  # Options: "RP2040_ZERO" or "XIAO_RP2040"

# Set I2C pins based on board type
if BOARD_TYPE == "XIAO_RP2040":
    SDA_PIN = 6  # SDA pin for I2C on Xiao RP2040
    SCL_PIN = 7  # SCL pin for I2C on Xiao RP2040
    XIAO_POWER_PIN = 11  # Power pin for Xiao RP2040
    XIAO_LED_PIN = 12  # RGB LED pin for Xiao RP2040
else:  # Default to RP2040_ZERO
    SDA_PIN = 2  # SDA pin for I2C on RP2040 Zero
    SCL_PIN = 3  # SCL pin for I2C on RP2040 Zero
    NEOPIXEL_PIN = 16  # Pin connected to the NeoPixel LED

pcaswitch = Pin(PCA_SWITCH_PIN, Pin.OUT)
pcaswitch.off()  # PNP, turn on the PCA9685 modules
time.sleep(1)

i2c = I2C(1, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN))
devices = i2c.scan()
time.sleep(1)
if not devices:
    print("No I2C devices found. Please check your connections.")
else:
    print("I2C devices found:", devices)
    pca = PCA9685(i2c, address = 0x40)  # Adjust the address as needed
    pca.frequency = 512
    pca.channels[0].duty_cycle = 0x0FFF  # Set channel 0 to full brightness
    time.sleep(1)  # Wait for 1 second to observe the change
    pca.channels[0].duty_cycle = 0x0000  # Set channel 0 to off

pcaswitch.on()