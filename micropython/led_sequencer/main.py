import asyncio
from machine import Pin, I2C, deepsleep
from photoresistor import photoresistor
from micropython_pca9685 import PCA9685
import neopixel
import random
import os
import ujson
import uio
import utime

MINIMUM_SEQUENCE_RUN = 3  # Minimum number of sequences to run
PWM_FREQUENCY = 512  # PWM frequency for PCA9685
PHOTORESISTOR_PIN = 29  # Pin for the photoresistor
PCA_SWITCH_PIN = 28  # Pin to control the PCA9685 modules
SDA_PIN = 2  # SDA pin for I2C
SCL_PIN = 3  # SCL pin for I2C
PCA_MODULE_WARMUP_TIME = 1  # Time to wait for PCA9685 modules to warm up
NEOPIXEL_PIN = 16  # Pin for the NeoPixel LED
GREEN = (0, 255, 0)  # Color for the NeoPixel LED
NEOPIXEL_OFF = (0, 0, 0)  # Color to turn off the NeoPixel LED
BLINK_COUNT = 3  # Number of blinks for the startup LED
BLINK_SLEEP = 0.5  # Sleep time for each blink

async def run_sequence(pca, file_name):
    json_data = "{}"
    with uio.open("sequences/" + file_name, "r") as f:
        json_data = ujson.load(f)
        f.close()

        end = len(json_data)
        # Keep track of the last channel and module
        last_ch = None
        last_module = None
        
        for i in range(end):
            #print(f"json_data[{i}]={json_data[i]}")
            ch = json_data[i]['ch']
            m = json_data[i]['m']
            module = ord(m) - ord('a')
            brightness = json_data[i]['lu']
            sleeplen = json_data[i]['s']
            
            # Skip creating a fade task (tail) if this is the same channel and module as the last one
            if last_ch != ch or last_module != module:
                #print(f"fade module={module} ch={ch}, brightness={brightness}, sleep={sleeplen}")
                asyncio.create_task(fade(pca[module], ch, brightness, sleeplen)) # Create a task for each LED
            else:
                #print(f"fade module={module} ch={ch}, brightness={brightness}, sleep={sleeplen}")
                pca[module].channels[ch].duty_cycle = percentage_to_duty_cycle(brightness)
                #pca.channels[ch].duty_cycle = percentage_to_duty_cycle(brightness)
                await asyncio.sleep(sleeplen)
                
            # Update the last channel and module
            last_ch = ch
            last_module = module
            
            await asyncio.sleep(json_data[i]['w'])
        return True
    return False

def percentage_to_duty_cycle(percentage):
    return int((percentage / 100) * 0xFFFF)

async def fade(pca, ch, brightness, sleeplen=0.25, fadevalue=0.01):
    iter = (int)(sleeplen/fadevalue)
    dimval = brightness/iter
    for i in range(iter):
        pca.channels[ch].duty_cycle = percentage_to_duty_cycle((i+1)*dimval)
        await asyncio.sleep(fadevalue)
    #print(f"LED {ch} brightness at {(int)((i+1)*dimval)}%")
    for i in range(iter):
        pca.channels[ch].duty_cycle = percentage_to_duty_cycle(brightness - ((i+1)*dimval))
        await asyncio.sleep(fadevalue)
    #print(f"LED {ch} brightness at {brightness - (int)((i+1)*dimval)}%")
    pca.channels[ch].duty_cycle = percentage_to_duty_cycle(0)

def custom_shuffle(lst):
    for i in range(len(lst) - 1, 0, -1):
        j = random.randint(0, i)
        lst[i], lst[j] = lst[j], lst[i]

def show_startup_blink():
    led = neopixel.NeoPixel(Pin(NEOPIXEL_PIN), 1)
    for i in range(BLINK_COUNT):
        utime.sleep(BLINK_SLEEP)  # Sleep for 0.5 seconds
        led[0] = GREEN
        led.write()  # Turn on the LED
        utime.sleep(BLINK_SLEEP)
        led[0] = NEOPIXEL_OFF
        led.write()  # Turn off the LED

# Define the main function to run the event loop
async def main():
    light = photoresistor(PHOTORESISTOR_PIN)  # Initialize the photoresistor on the defined pin
    pcaswitch = Pin(PCA_SWITCH_PIN,Pin.OUT)  # Set the pin to control the PCA9685 modules
    
    dir = "sequences/"
    d = os.listdir(dir)
    files = []
    for e in d:
        files.append(e)

    print("Checking light level...")
    if light.read() < 2: # Check if the light level is below a certain threshold
        print("Light level is low, running sequences")
        #voltage_status(led, read_3v3_voltage())  # Check the voltage level and set the LED color accordingly
        custom_shuffle(files)  # Use the custom shuffle function

        i2c = I2C(1, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN))  # Correct I2C pins for rp2040 and wemos S2 mini
        pcaswitch.off()  # Turn on the PCA9685 modules (PNP)
        print("PCA9685 modules are on")
        utime.sleep(PCA_MODULE_WARMUP_TIME) # Allow time for the PCA9685 modules to initialize

        pca_A = PCA9685(i2c, address=0x40)
        pca_B = PCA9685(i2c, address=0x41)
        pca_C = PCA9685(i2c, address=0x42)
        pca_D = PCA9685(i2c, address=0x43)

        pca_A.frequency = pca_B.frequency = pca_C.frequency = pca_D.frequency = PWM_FREQUENCY
        pca = [pca_A, pca_B, pca_C, pca_D]
        
        # Initialize all channels to 0% duty cycle
        for pca_instance in pca:
            for channel in pca_instance.channels:
                channel.duty_cycle = 0

        iterEnd = random.randrange(MINIMUM_SEQUENCE_RUN, len(files) + 1)  # Randomly choose how many sequences to run
        print(f"Running {iterEnd} sequences out of {len(files)} available sequences")
        for i in range(iterEnd):
            print(f"Running sequence {files[i]}")
            await run_sequence(pca, files[i])
            await asyncio.sleep(random.randrange(1, 5))  # Allow the sequence time to finish
        # Uncomment the following lines if you want to run all sequences in the directory
        #for file in files:
            #print(f"Running sequence {file}")
        #    await run_sequence(pca, file)
        #    await asyncio.sleep(random.randrange(1, 5))  # Allow the sequence time to finish
        
        pcaswitch.on() #PNP, turn off the PCA9685 modules
        print("PCA9685 modules are off")
        utime.sleep(random.randrange(5, 30))
        deepsleep(1000 * random.randrange(5, 30))
        # Sleep for a random time between 5 and 30 seconds between sequences
    else:
        #print("Light level is high, sleeping")
        #utime.sleep(30)
        deepsleep(30 * 1000) # sleep before sampling for sunlight level

if __name__ == "__main__":
    # Create and run the event loop
    loop = asyncio.get_event_loop()  
    loop.create_task(main())  # Create a task to run the main function
    loop.run_forever()  # Run the event loop indefinitely