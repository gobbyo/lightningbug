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

async def run_sequence(pca, file_name):
    json_data = "{}"
    with uio.open("sequences/" + file_name, "r") as f:
        json_data = ujson.load(f)
        f.close()

        end = len(json_data)
        for i in range(end):
            #print(f"json_data[{i}]={json_data[i]}")
            ch = json_data[i]['ch']
            m = json_data[i]['m']
            module = ord(m) - ord('a')
            brightness = json_data[i]['lu']
            sleeplen = json_data[i]['s']
            #print(f"fade ch={ch}, brightness={brightness}, sleep={sleeplen}")
            #print(f"fade module={module} ch={ch}, brightness={brightness}, sleep={sleeplen}")
            asyncio.create_task(fade(pca[module], ch, brightness, sleeplen)) # Create a task for each LED
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

def read_3v3_voltage():
    adc = machine.ADC(28)  # 3V3 is connected to ADC28
    conversion_factor = 3.3 / (65535)
    
    reading = adc.read_u16() * conversion_factor
    return reading

def voltage_status(led, voltage):
    record_sample(voltage)  # Record the voltage sample
    print(f"Voltage: {voltage:.2f}V")
    v = round(voltage * 100,0)
    yellow = (200, 90, 0)
    red = (255, 0, 0)
    if v < 290:
        led[0] = red
        led.write()
    elif v < 310:
        led[0] = yellow
        led.write()
    else:
        led[0] = (0, 0, 0)
        led.write()

def record_sample(voltage):
    with uio.open("voltages.txt", "a") as f:
        f.write("{0}: {1:.2f}V\n".format(utime.time(), voltage))
        f.close()
    pcaswitch = Pin(15,Pin.OUT)  # Set the pin to control the PCA9685 modules
    print("PCA9685 modules are off")
    pcaswitch.off()  # Turn on the PCA9685 modules (PNP)
    print("PCA9685 modules are on")
    i2c = I2C(1, sda=Pin(2), scl=Pin(3))  # Correct I2C pins for rp2040 and wemos S2 mini
    pca_A = PCA9685(i2c, address=0x40)
    pca_B = PCA9685(i2c, address=0x41)
    pca_C = PCA9685(i2c, address=0x42)
    pca_D = PCA9685(i2c, address=0x43)

    pca_A.frequency = pca_B.frequency = pca_C.frequency = pca_D.frequency = 512

    pca = [pca_A, pca_B, pca_C, pca_D] 

    pcaswitch.on()

    def custom_shuffle(lst):
        for i in range(len(lst) - 1, 0, -1):
            j = random.randint(0, i)
            lst[i], lst[j] = lst[j], lst[i]

    dir = "sequences/"
    d = os.listdir(dir)
    files = []
    for e in d:
        files.append(e)

    while True:
        if light.read() < 2: # Check if the light level is below a certain threshold
            #print("Light level is low, running sequences")
            #voltage_status(led, read_3v3_voltage())  # Check the voltage level and set the LED color accordingly
            custom_shuffle(files)  # Use the custom shuffle function

            for file in files:
                #print(f"Running sequence {file}")
                pcaswitch.off() #PNP, turn on the PCA9685 modules
                await run_sequence(pca, file)
                await asyncio.sleep(random.randrange(1, 5))  # Allow the sequence time to finish
                pcaswitch.on() #PNP, turn off the PCA9685 modules
                
            #asyncio.sleep(1000 * random.randrange(5, 30))
            deepsleep(1000 * random.randrange(5, 30))
            # Sleep for a random time between 5 and 30 seconds between sequences
        else:
            #print("Light level is high, sleeping")
            #await asyncio.sleep(5)
            deepsleep(30 * 1000) # sleep before sampling for sunlight level

if __name__ == "__main__":
    # Create and run the event loop
    loop = asyncio.get_event_loop()  
    loop.create_task(main())  # Create a task to run the main function
    loop.run_forever()  # Run the event loop indefinitely