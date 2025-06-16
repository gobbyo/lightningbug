import asyncio
from machine import Pin, I2C, PWM
from micropython_pca9685 import PCA9685
import ujson
import uio
import os
import neopixel
import random
import utime

SHORT = 0.125
LONG = 0.5
BLINK_SLEEP = 0.25
NEOPIXEL_PIN = 16  # Pin connected to the NeoPixel LED
RED = (255, 0, 0)  # Color for the NeoPixel LED
LED_OFF = (0, 0, 0)  # Color to turn off the NeoPixel LED

STATIC_CHOICES = [("a", 2), ("c", 14), ("c", 2), ("d", 2), ("b", 2), ("b", 13)]
LED_PINS = [("d1", 0), ("d2", 1),("d3", 4), ("d4", 5), ("d5", 6), ("d6", 7), ("d7", 8), ("d8", 9), ("d9", 10), ("d10", 11), ("d11", 12), ("d12", 13), ("d13", 14), ("d14", 15), ("d15", 26), ("d16", 27)]  # Example LED pins

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

async def fade_mc(pwm, brightness, sleeplen=0.25, fadevalue=0.01):
    iter = (int)(sleeplen/fadevalue)
    dimval = brightness/iter
    for i in range(iter):
        pwm.duty_u16(percentage_to_duty_cycle((i+1)*dimval))
        await asyncio.sleep(fadevalue)
    #print(f"LED {ch} brightness at {(int)((i+1)*dimval)}%")
    for i in range(iter):
        pwm.duty_u16(percentage_to_duty_cycle(brightness - ((i+1)*dimval)))
        await asyncio.sleep(fadevalue)
    #print(f"LED {ch} brightness at {brightness - (int)((i+1)*dimval)}%")
    pwm.duty_u16(0)

async def flashLED(led, color, duration=0.5):
    led[0] = color
    led.write()
    await asyncio.sleep(duration)
    led[0] = (0, 0, 0)  # Turn off the LED
    led.write()
    await asyncio.sleep(duration)

# Define the main function to run the event loop
async def main():
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    led = neopixel.NeoPixel(machine.Pin(16), 1)  # Using internal NeoPixel on Pin 16

    slow = [1, 1]
    walk = [0.5, 0.25]
    med = [0.19, 0.1]
    fast = [0.14, 0.07]
    veryfast = [0.125, 0.05]
    brightness = 50 #percent

    led_pins_dict = dict(LED_PINS)

    leds = []
    for i in range(len(LED_PINS)):
        led = machine.PWM(Pin(LED_PINS[i][1]))
        led.freq(512)
        led.duty_u16(0)
        leds.append(led)

    m = "d"
    for i in range(0, len(leds)):
        item = m + str(i+1)
        print(f"Item '{item}'")
        print(f"led_pins_dict[{item}]={led_pins_dict[item]}")
        asyncio.create_task(fade_mc(leds[i], brightness, med[0])) # Create a task for each LED
        await asyncio.sleep(med[1])

if __name__ == "__main__":
    # Create and run the event loop
    loop = asyncio.get_event_loop()  
    loop.create_task(main())  # Create a task to run the main function
    loop.run_forever()  # Run the event loop indefinitely