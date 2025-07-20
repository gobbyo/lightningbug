"""
Debug script for PCA9685 I2C communication issues
"""
import utime
from machine import Pin, I2C
from micropython_pca9685 import PCA9685

# Board configuration - Change this to match your microcontroller
BOARD_TYPE = "XIAO_RP2040"  # Options: "RP2040_ZERO" or "XIAO_RP2040"

# Set I2C pins based on board type
if BOARD_TYPE == "XIAO_RP2040":
    SDA_PIN = 6  # SDA pin for I2C on Xiao RP2040
    SCL_PIN = 7  # SCL pin for I2C on Xiao RP2040
else:  # Default to RP2040_ZERO
    SDA_PIN = 2  # SDA pin for I2C on RP2040 Zero
    SCL_PIN = 3  # SCL pin for I2C on RP2040 Zero

def test_i2c_basic():
    """Test basic I2C communication"""
    print("Testing basic I2C communication...")
    
    # Try different I2C frequencies
    frequencies = [100000, 400000, 50000]  # 100kHz, 400kHz, 50kHz
    
    for freq in frequencies:
        print(f"\nTrying I2C frequency: {freq} Hz")
        try:
            i2c = I2C(1, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=freq)
            utime.sleep(0.1)  # Give I2C time to initialize
            
            devices = i2c.scan()
            print(f"Devices found: {[hex(addr) for addr in devices]}")
            
            if len(devices) > 0:
                for addr in devices:
                    print(f"Device at address {hex(addr)} found!")
                
                    # Test basic read from a known register
                    try:
                        # Try to read the MODE1 register (0x00)
                        mode1_data = i2c.readfrom_mem(addr, 0x00, 1)
                        print(f"MODE1 register read successful: 0x{mode1_data[0]:02x}")
                        
                        # Try to write to MODE1 register
                        print("Attempting to write to MODE1 register...")
                        i2c.writeto_mem(addr, 0x00, bytes([0x00]))
                        print("MODE1 register write successful!")
                        
                        return i2c, freq  # Return successful I2C object and frequency
                        
                    except Exception as e:
                        print(f"Error reading/writing MODE1 register: {e}")
                        print()
            else:
                print(f"PCA9685 not found")
                print()
                
        except Exception as e:
            print(f"I2C initialization failed at {freq} Hz: {e}")
    
    return None, None

def test_pca_with_retry():
    """Test PCA9685 initialization with retry logic"""
    print("\nTesting PCA9685 initialization with retry...")
    
    i2c, freq = test_i2c_basic()
    if i2c is None:
        print("Could not establish basic I2C communication")
        return None
    
    print(f"Using I2C frequency: {freq} Hz")
    
    # Try PCA9685 initialization with retries
    max_retries = 5
    for attempt in range(max_retries):
        try:
            print(f"PCA9685 initialization attempt {attempt + 1}/{max_retries}")
            
            # Add a small delay before each attempt
            utime.sleep(0.1)
            
            pca = PCA9685(i2c, address=0x40)
            print("PCA9685 initialization successful!")
            return pca
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                utime.sleep(0.5)  # Wait before retry
            else:
                print("All attempts failed")
    
    return None

def test_power_sequence():
    """Test with proper power sequencing"""
    print("\nTesting with power sequence control...")
    
    PCA_SWITCH_PIN = 28  # Pin to control the PCA9685 modules
    pcaswitch = Pin(PCA_SWITCH_PIN, Pin.OUT)
    
    # Turn off modules first
    pcaswitch.on()  # PNP, turn off the PCA9685 modules
    utime.sleep(0.5)
    
    # Turn on modules
    pcaswitch.off()  # Turn on the PCA9685 modules (PNP)
    utime.sleep(1)  # Allow time for modules to stabilize
    
    # Now try I2C communication
    pca = test_pca_with_retry()
    
    if pca:
        print("Success with power sequencing!")
        # Test setting a channel
        try:
            pca.frequency = 1000
            pca.channels[0].duty_cycle = 0x8000  # 50% duty cycle
            print("Channel test successful!")
        except Exception as e:
            print(f"Channel test failed: {e}")
    
    return pca

if __name__ == "__main__":
    print("Starting PCA9685 debug tests...")
    print(f"Using SDA_PIN: {SDA_PIN}, SCL_PIN: {SCL_PIN}")
    
    # Test sequence
    pca = test_power_sequence()
    
    if pca is None:
        print("\nAll tests failed. Possible issues:")
        print("1. Check power supply to PCA9685 modules")
        print("2. Check I2C wiring (SDA/SCL)")
        print("3. Check pull-up resistors on I2C lines")
        print("4. Try different I2C frequency")
        print("5. Check for loose connections")
    else:
        print("\nPCA9685 is working correctly!")
