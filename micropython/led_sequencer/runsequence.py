import asyncio
from machine import Pin, I2C, deepsleep
from micropython_pca9685 import PCA9685
import random
import os
import ujson
import uio

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

# Define the main function to run the event loop
async def main():
    pcaswitch = Pin(15,Pin.OUT)  # Set the pin to control the PCA9685 modules
    pcaswitch.off()  # Turn on the PCA9685 modules (PNP)
    i2c = I2C(1, sda=Pin(2), scl=Pin(3))  # Correct I2C pins for rp2040 and wemos S2 mini
    pca_A = PCA9685(i2c, address=0x40)
    pca_B = PCA9685(i2c, address=0x41)
    pca_C = PCA9685(i2c, address=0x42)
    pca_D = PCA9685(i2c, address=0x43)

    pca_A.frequency = pca_B.frequency = pca_C.frequency = pca_D.frequency = 512

    pca = [pca_A, pca_B, pca_C, pca_D] 

    def custom_shuffle(lst):
        for i in range(len(lst) - 1, 0, -1):
            j = random.randint(0, i)
            lst[i], lst[j] = lst[j], lst[i]

    i = 0
    while True:
        dir = "sequences/"
        d = os.listdir(dir)
        files = []
        for e in d:
            files.append(e)

        custom_shuffle(files)  # Use the custom shuffle function

        for file in files:
            print(f"Running sequence {file}")
            pcaswitch.off() #PNP
            await run_sequence(pca, file)
            await asyncio.sleep(2)  # Allow the sequence time to finish
            pcaswitch.on() #PNP
            await asyncio.sleep(random.randrange(1, 10))  # Allow the sequence time to finish
        print(f"finished sequence {i}")
        i += 1
        pcaswitch.on() # Turn off the PCA9685 modules (PNP)
        deepsleep(1000 * random.randrange(15, 60))
        pcaswitch.off() # Turn on the PCA9685 modules (PNP)

if __name__ == "__main__":
    # Create and run the event loop
    loop = asyncio.get_event_loop()  
    loop.create_task(main())  # Create a task to run the main function
    loop.run_forever()  # Run the event loop indefinitely