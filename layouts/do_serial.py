import usb_cdc
from pmk.platform.keybow2040 import Keybow2040 as Hardware
from pmk import PMK

# Initialise Keybow 2040 hardware
keybow = PMK(Hardware())
keys = keybow.keys

# Ensure we are listening on the secondary data port
serial = usb_cdc.data

print("Keybow listening for serial commands...")

while True:
    # Always keep the keybow hardware engine updating
    keybow.update()
    
    if serial and serial.in_waiting > 0:
        
        try:
            # Read a full line up to the newline character
            raw_line = serial.readline()
            
            # Clean up the string (remove spaces, newlines, etc.)
            command = raw_line.decode('utf-8').strip()
            
            # Skip empty transmissions
            if not command:
                continue
                
            # Expected format: "KEY_NUM,R,G,B" -> e.g., "0,255,0,0"
            parts = command.split(",")
            
            if len(parts) == 4:
                # Parse values into integers
                key_num = int(parts[0])
                r = int(parts[1])
                g = int(parts[2])
                b = int(parts[3])
                
                # Bound check RGB values between 0 and 255
                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))
                
                # Validate key number (Keybow 2040 has keys 0 to 15)
                if 0 <= key_num < 16:


                    # Set the specific key colour
                    keys[key_num].set_led(r, g, b)
                
                    # Set all!
                if key_num == 255:
                    
                    keybow.set_all(r, g, b)
                    
        except Exception as e:
            print("Exception")
            print(e)
            # Catch parsing or decoding errors gracefully
            pass
