import machine
import utime
import uio
import neopixel

def read_vbus_voltage():
    loss_adjustment = 0.29 #factor to account for any losses in the measurement process
    adc = machine.ADC(29)  # VBUS is connected to ADC29
    conversion_factor = 3.3 / (65535)
    
    reading = adc.read_u16() * conversion_factor
    # The voltage divider on the Pico board scales the VBUS voltage by a factor of 3
    usb_voltage = (reading * 3) + loss_adjustment
    return usb_voltage

def read_vsys_voltage():
    adc = machine.ADC(3)  # VSYS is connected to ADC3
    conversion_factor = 1.62 / (65535)
    
    reading = adc.read_u16() * conversion_factor
    # The voltage divider on the Pico board scales the VSYS voltage by a factor of 3
    supply_voltage = reading * 3
    return supply_voltage

def read_3v3_voltage():
    adc = machine.ADC(27)  # 3V3 is connected to ADC28
    conversion_factor = 3.3 / (65535)
    reading = adc.read_u16() * conversion_factor
    return reading

def record_sample(m):
    v = read_vbus_voltage()
    with uio.open("voltages.txt", "a") as f:
        f.write("{0}: {1:.2f}V\n".format(m, v))
        f.close()
    return v

def voltage_status(led, voltage):
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

def main():
    led = neopixel.NeoPixel(machine.Pin(16), 1)
    min = 0

    while True:
        v = record_sample(min)
        print("Voltage: {0:.2f}V".format(v))
        voltage_status(led, v)
        utime.sleep(60)
        min += 1

if __name__ == "__main__":
    main()