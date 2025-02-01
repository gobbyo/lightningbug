import machine
import utime

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
    conversion_factor = 3.3 / (65535)
    
    reading = adc.read_u16() * conversion_factor
    # The voltage divider on the Pico board scales the VSYS voltage by a factor of 3
    supply_voltage = reading * 3
    return supply_voltage

def read_3v3_voltage():
    adc = machine.ADC(28)  # 3V3 is connected to ADC28
    conversion_factor = 3.3 / (65535)
    
    reading = adc.read_u16() * conversion_factor
    return reading

def main():
    print("VSYS voltage: {:.2f}V".format(read_vsys_voltage()))
    utime.sleep(1)
    print("3v3 Voltage: {:.2f}V".format(read_3v3_voltage()))
    utime.sleep(1)
    print("USB Voltage: {:.2f}V".format(read_vbus_voltage()))
    utime.sleep(1)
    

if __name__ == "__main__":
    main()