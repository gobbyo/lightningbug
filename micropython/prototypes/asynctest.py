import asyncio
from machine import Pin, PWM
from time import sleep

async def fade(pin, brightness = 65535, sleeplen=0.25, fadevalue=0.01):
    # Set up the PWM pin
    pwm = PWM(Pin(pin))
    pwm.freq(50)
    print(f"Fade pin:{pin}, sleeplen:{sleeplen}, fadevalue:{fadevalue}")
    pwm.duty_u16(brightness)
    iter = int(sleeplen/fadevalue)
    dimval = brightness/iter
    for i in range(iter):
        pwm.duty_u16((int)(i*dimval))
        await asyncio.sleep(fadevalue)
    for i in range(iter):
        pwm.duty_u16(brightness - (int)(i*dimval))
        await asyncio.sleep(fadevalue)
    pwm.duty_u16(0)

# Define the main function to run the event loop
async def main():
    brightness = 4096
    sleeplen = 0.25
    waitlen = .125
    # Create tasks for fading 3 LEDs concurrently
    asyncio.create_task(fade(29, brightness, sleeplen))
    await asyncio.sleep(waitlen)
    asyncio.create_task(fade(28, brightness, sleeplen))
    await asyncio.sleep(waitlen)
    asyncio.create_task(fade(27, brightness, sleeplen))
    await asyncio.sleep(1)
    for i in range(2):
        asyncio.create_task(fade(27, int(5535/(i+1)), 1))
        await asyncio.sleep(2)
    asyncio.create_task(fade(29, 1535, 1))
    await asyncio.sleep(2)

if __name__ == "__main__":
    # Create and run the event loop
    loop = asyncio.get_event_loop()  
    loop.create_task(main())  # Create a task to run the main function
    loop.run_forever()  # Run the event loop indefinitely