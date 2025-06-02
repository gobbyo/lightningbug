from machine import ADC, Pin
import time

class photoresistor():
    def __init__(self, pin):
        self.photoRes = ADC(Pin(pin))
        self.light = 0
        self.max = 65767 # 100%
        self.min = 0 # 0%

    def read(self):
        range = self.max - self.min
        k = self.photoRes.read_u16()
        #print("Raw ADC value: {0}".format(k))
        k = k - self.min
        if k <= 0:
            k = 1
        self.light = int((k/range)*10)
        if self.light >= 10:
            self.light = 9
        elif self.light <= 0:
            self.light = 1
        return self.light

#Example usage:
def main():
    light = photoresistor(29)
    for i in range(10):
        # Read the value from the photoresistor
        print("Light level: {0}".format(light.read()))
        time.sleep(1)

if __name__ == "__main__":
    main() 