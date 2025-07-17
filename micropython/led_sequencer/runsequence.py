import asyncio
from machine import Pin, I2C, deepsleep, reset
from photoresistor import photoresistor
from micropython_pca9685 import PCA9685
import random
import neopixel
import os
import ujson
import uio
import utime
import gc

MINIMUM_SEQUENCE_RUN = 1  # Minimum number of sequences to run
MIN_SLEEP_TIME_BETWEEN_RUNS = 1  # Minimum sleep time in seconds
MAX_SLEEP_TIME_BETWEEN_RUNS = 5  # Maximum sleep time in seconds
LIGHT_DETECTION_SLEEP = 30  # Sleep time in seconds for light detection
PWM_FREQUENCY = 512  # PWM frequency for PCA9685
PHOTORESISTOR_PIN = 29  # Pin for the photoresistor
PCA_SWITCH_PIN = 28  # Pin to control the PCA9685 modules
# PHOTORESISTOR_PIN = 28  # Pin for the photoresistor
# PCA_SWITCH_PIN = 27  # Pin to control the PCA9685 modules
SDA_PIN = 2  # SDA pin for I2C
SCL_PIN = 3  # SCL pin for I2C
PCA_MODULE_WARMUP_TIME = 1  # Time to wait for PCA9685 modules to warm up
LIGHT_THRESHOLD = 2
SEQUENCE_SLEEP_MIN = 1
SEQUENCE_SLEEP_MAX = 5

# error warning flashes
SHORT = 0.125
LONG = 0.5
BLINK_SLEEP = 0.25
NEOPIXEL_PIN = 16  # Pin connected to the NeoPixel LED
RED = (255, 0, 0)  # Color for the NeoPixel LED
LED_OFF = (0, 0, 0)  # Color to turn off the NeoPixel LED

STATIC_CHOICES = [("a", 2), ("c", 14), ("c", 2), ("d", 2), ("b", 2), ("b", 13)]

def blink_led(blink_pattern):
    led = neopixel.NeoPixel(Pin(NEOPIXEL_PIN), 1)
    for i in range(3):
        for duration in blink_pattern:
            led[0] = RED  # Set the color of the NeoPixel
            led.write()
            utime.sleep(duration)
            led[0] = LED_OFF  # Set the color of the NeoPixel
            led.write()  # Turn off the LED
            utime.sleep(BLINK_SLEEP)  # Sleep for the specified duration
        utime.sleep(3)

# Add this at strategic points in your code where memory might be an issue
def collect_garbage():
    gc.collect()
    #print(f"Free memory: {gc.mem_free()} bytes")

async def run_sequence(pca, file_name):
    try:
        with uio.open("sequences/" + file_name, "r") as f:
            json_data = ujson.load(f)
            
        end = len(json_data)
        #print(f"Running sequence from file: {file_name}, total entries: {end}")

        # Keep track of the last channel and module
        last_ch = None
        last_module = None
        is_static = False

        if file_name.startswith("static"):
            is_static = True
        
        static_substitutions = random.choice(STATIC_CHOICES)

        for i in range(end):
            
            #print(f"json_data[{i}]={json_data[i]}")

            if is_static:
                #print(f"static_substitutions={static_substitutions}")
                m = static_substitutions[0]
                ch = static_substitutions[1]
            else:
                m = json_data[i]['m']
                ch = json_data[i]['ch']

            #print(f"is_static={is_static}, ch={ch}, m={m}")
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
    except OSError as e:
        #print(f"Error opening file {file_name}: {e}")
        blink_led([SHORT, LONG])
        return False
    except ujson.JSONDecodeError:
        blink_led([SHORT, SHORT, SHORT])
        #print(f"Error parsing JSON in file {file_name}")
        return False
    except Exception as e:
        blink_led([LONG, SHORT, LONG])
        #print(f"Unexpected error: {e}")
        return False

def percentage_to_duty_cycle(percentage):
    return int((percentage / 100) * 0xFFFF)

async def fade(pca, ch, brightness, sleeplen=0.25, fadevalue=0.01):
    iterations = max(1, int(sleeplen/fadevalue))
    step_value = brightness / iterations
    
    # Fade up
    for i in range(iterations):
        duty_cycle = percentage_to_duty_cycle((i+1) * step_value)
        pca.channels[ch].duty_cycle = duty_cycle
        await asyncio.sleep(fadevalue)
    
    # Fade down
    for i in range(iterations):
        duty_cycle = percentage_to_duty_cycle(brightness - ((i+1) * step_value))
        pca.channels[ch].duty_cycle = duty_cycle
        await asyncio.sleep(fadevalue)
    
    # Ensure LED is fully off
    pca.channels[ch].duty_cycle = 0

def custom_shuffle(lst):
    for i in range(len(lst) - 1, 0, -1):
        j = random.randint(0, i)
        lst[i], lst[j] = lst[j], lst[i]

async def setup_pca_modules(i2c):
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
    
    return pca

# Define the main function to run the event loop
async def main(light, pcaswitch, files):
    #print("Checking light level...")
    if light.read() < LIGHT_THRESHOLD: # Check if the light level is below a certain threshold
        #print("Light level is low, running sequences")
        custom_shuffle(files)  # Use the custom shuffle function

        # Setup I2C and PCA modules
        i2c = I2C(1, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN))  # Correct I2C pins for rp2040 and wemos S2 mini
        pcaswitch.off()  # Turn on the PCA9685 modules (PNP)
        #print("PCA9685 modules are on")
        utime.sleep(PCA_MODULE_WARMUP_TIME) # Allow time for the PCA9685 modules to initialize
        
        try:
            pca = await setup_pca_modules(i2c)
            await run_sequences(pca, files)
        finally:
            # Ensure we turn off the modules even if an error occurs
            pcaswitch.on()  # PNP, turn off the PCA9685 modules
        
        #utime.sleep(5)  # Allow time for the last sequence to finish
        deepsleep(1000 * random.randrange(MIN_SLEEP_TIME_BETWEEN_RUNS, MAX_SLEEP_TIME_BETWEEN_RUNS))
        # Sleep for a random time between 5 and 30 seconds between sequences
    else:
        pcaswitch.on() #PNP, turn off the PCA9685 modules
        #print("Light level is high, sleeping")
        #utime.sleep(LIGHT_DETECTION_SLEEP)
        deepsleep(LIGHT_DETECTION_SLEEP * 1000) # sleep before sampling for sunlight level

async def run_sequences(pca, files):
    iterEnd = random.randint(MINIMUM_SEQUENCE_RUN, len(files))
    try:
        for i in range(iterEnd):
            await run_sequence(pca, files[i])
            await asyncio.sleep(random.randint(SEQUENCE_SLEEP_MIN, SEQUENCE_SLEEP_MAX))

    except Exception as e:
        blink_led([SHORT, SHORT, SHORT])
        print(f"Error running sequences: {e}")
        # Turn off all LEDs in case of error
        for pca_instance in pca:
            for channel in pca_instance.channels:
                channel.duty_cycle = 0
    
if __name__ == "__main__":
    try:
        # Create and run the event loop
        light = photoresistor(PHOTORESISTOR_PIN)
        pcaswitch = Pin(PCA_SWITCH_PIN, Pin.OUT)
        pcaswitch.on()  # PNP, turn off the PCA9685 modules

        dir = "sequences/"
        try:
            files = os.listdir(dir)
        except OSError:
            #print(f"Error: '{dir}' directory not found or empty")
            files = []
       
        if files:
            loop = asyncio.get_event_loop()
            loop.create_task(main(light, pcaswitch, files))
            loop.run_forever()
        else:
            #print("No sequence files found. Going to sleep.")
            deepsleep(LIGHT_DETECTION_SLEEP * 1000)
    except Exception as e:
        blink_led([SHORT, SHORT, SHORT, LONG, LONG, LONG, SHORT, SHORT, SHORT])
        print(f"Fatal error: {e}")
        # Try to ensure clean shutdown
        reset()