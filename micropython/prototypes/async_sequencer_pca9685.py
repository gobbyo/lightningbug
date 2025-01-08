import asyncio
from machine import Pin, I2C
from micropython_pca9685 import PCA9685
from time import sleep
import ujson
import uio

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
    i2c = I2C(1, sda=Pin(2), scl=Pin(3))  # Correct I2C pins for RP2040
    pca = PCA9685(i2c)
    pca.frequency = 512

    json_data = "{}"
    with uio.open("sequence_studder.json", "r") as f:
        json_data = ujson.load(f)
        f.close()

        end = len(json_data['LEDPositions'])
        for r in range(10):
            for i in range(end):
                ch = json_data['LEDPositions'][i]['Ref']
                brightness = json_data['LEDPositions'][i]['Lumin']
                sleeplen = json_data['LEDPositions'][i]['SleepSec']
                print(f"fade ch={ch}, brightness={brightness}, sleep={sleeplen}")
                asyncio.create_task(fade(pca, ch, brightness, sleeplen)) # Create a task for each LED
                await asyncio.sleep(json_data['LEDPositions'][i]['WaitSec'])


if __name__ == "__main__":
    # Create and run the event loop
    loop = asyncio.get_event_loop()  
    loop.create_task(main())  # Create a task to run the main function
    loop.run_forever()  # Run the event loop indefinitely