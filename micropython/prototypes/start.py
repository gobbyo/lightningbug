import asyncio
from machine import Pin, I2C
from micropython_pca9685 import PCA9685
import time
import ujson
import uio

def percentage_to_duty_cycle(percentage):
    return int((percentage / 100) * 65535)

async def main():
    i2c = I2C(1, sda=Pin(2), scl=Pin(3))  # Correct I2C pins for RP2040
    pca = PCA9685(i2c)

    pca.frequency = 500

    percent_lumin = 100
    tail_len = 5

    json_data = "{}"
    with uio.open("pattern1.json", "r") as f:
        json_data = ujson.load(f)
        f.close()

    steps = 0

    for i in range(0, len(json_data["steps"])):
        steps += 1
        if json_data["steps"][i]["type"] == "led":
            pca.channels[json_data["steps"][i]["ch"]].duty_cycle = percentage_to_duty_cycle(json_data["steps"][i]["val"])
        elif json_data["steps"][i]["type"] == "sleep":
            time.sleep(json_data["steps"][i]["val"])
        else:
            print("Unknown type: ", json_data["steps"][i]["type"])

    print("Total steps: ", steps)
if __name__ == "__main__":
    asyncio.run(main())