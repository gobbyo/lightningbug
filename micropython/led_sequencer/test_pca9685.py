import asyncio
from machine import Pin, I2C
from micropython_pca9685 import PCA9685
import ujson
import uio
import os

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
            
            # Skip creating a fade task if this is the same channel and module as the last one
            if last_ch != ch or last_module != module:
                print(f"fade module={module} ch={ch}, brightness={brightness}, sleep={sleeplen}")
                asyncio.create_task(fade(pca[module], ch, brightness, sleeplen)) # Create a task for each LED
            else:
                print(f"fade module={module} ch={ch}, brightness={brightness}, sleep={sleeplen}")
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

# Define the main function to run the event loop
async def main():
    slow = [1, 1]
    walk = [0.5, 0.25]
    med = [0.19, 0.1]
    fast = [0.14, 0.07]
    veryfast = [0.125, 0.05]
    brightness = 50 #percent
    
    i2c = I2C(1, sda=Pin(2), scl=Pin(3))  # Correct I2C pins for RP2040
    pca_A = PCA9685(i2c, address=0x40)
    pca_B = PCA9685(i2c, address=0x41)
    pca_C = PCA9685(i2c, address=0x42)
    pca_D = PCA9685(i2c, address=0x43)


    #pca_A.frequency = pca_B.frequency = pca_C.frequency = 512
    pca_A.frequency = pca_B.frequency = pca_C.frequency = pca_D.frequency = 512

    #pca = [pca_A, pca_B, pca_C]
    pca = [pca_A, pca_B, pca_C, pca_D] 
    module = ['a', 'b', 'c', 'd']
    
    if True:
        filenum = 2
        dir = "sequences/"
        files = os.listdir(dir)
        print(f"Running sequence from file: {files[filenum]}")
        await run_sequence(pca, files[filenum]) # Run the sequence from the JSON file
        #for f in files:
        #    print(f"Running sequence from file: {f}")
        #    await run_sequence(pca, f) # Run the sequence from the JSON file
    
    if False: # Set to True to Test all LEDs on all modules
        for i in range(len(pca)):
            for j in range(16):
                print(f"mod:{module[i]},{j}")
                asyncio.create_task(fade(pca[i], j, brightness, med[0])) # Create a task for each LED
                await asyncio.sleep(med[1])

    if False: # Set to True to SLOWLY Test all LEDs on all modules
        i = 2
        for j in range(16):
            print(f"mod:{module[i]},{j}")
            asyncio.create_task(fade(pca[i], j, brightness, slow[0])) # Create a task for each LED
            await asyncio.sleep(2)

if __name__ == "__main__":
    # Create and run the event loop
    loop = asyncio.get_event_loop()  
    loop.create_task(main())  # Create a task to run the main function
    loop.run_forever()  # Run the event loop indefinitely