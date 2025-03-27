import asyncio
from machine import Pin, I2C
from micropython_pca9685 import PCA9685
from time import sleep

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
<<<<<<< HEAD
    slow = [0.25, 0.125]
    fast = [0.125, 0.05]
    veryfast = [0.125, 0.01]
    brightness = 100 #percent
    
    if True:
        sleeplen = slow[0]
        waitlen = slow[1]
    else:
        sleeplen = fast[0]
        waitlen = fast[1]

    i2c = I2C(1, sda=Pin(2), scl=Pin(3))  # Correct I2C pins for RP2040
    pca1 = PCA9685(i2c,address=0x40)
    pca2 = PCA9685(i2c,address=0x41)
    pca1.frequency = 512
    pca2.frequency = 512
    # Create tasks for fading 3 LEDs concurrently
    for i in range(2):
        print(f"LED {i} fade ")
        asyncio.create_task(fade(pca1, i, brightness, sleeplen)) # Create a task for each LED
        asyncio.create_task(fade(pca2, i, brightness, sleeplen)) # Create a task for each LED
        await asyncio.sleep(waitlen)
    
    await asyncio.sleep(sleeplen*2)

    for ch in range(2):
        print(f"LED {ch} heartbeat ")
        for i in range(3):
            sleeplen = 1
            #brightness = int(48/(i+1))
            asyncio.create_task(fade(pca1, ch, brightness, sleeplen))
            asyncio.create_task(fade(pca2, ch, brightness, sleeplen))
            await asyncio.sleep(sleeplen*2)
    await asyncio.sleep(1)
=======
    slow = [1, 1]
    walk = [0.5, 0.25]
    med = [0.19, 0.1]
    fast = [0.14, 0.07]
    veryfast = [0.125, 0.05]
    brightness = 30 #percent
    
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
    
    for i in range(len(pca)):
        for j in range(16):
            print(f"mod:{module[i]},{j}")
            asyncio.create_task(fade(pca[i], j, brightness, med[0])) # Create a task for each LED
            await asyncio.sleep(med[1])

    if True: # Set to True to SLOWLY Test all LEDs on all modules
        for j in range(16):
            print(f"mod:c,{j}")
            asyncio.create_task(fade(pca_C, j, brightness, slow[0])) # Create a task for each LED
            await asyncio.sleep(2)
    

>>>>>>> 1c2acedd56e36ec48f7546d43656a635558fff7c

if __name__ == "__main__":
    # Create and run the event loop
    loop = asyncio.get_event_loop()  
    loop.create_task(main())  # Create a task to run the main function
    loop.run_forever()  # Run the event loop indefinitely