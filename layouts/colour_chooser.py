# Yes - "Colour", not "Color". I am British.
# (Just be glad I'm not dealing with my neighbour's favourite doughnut shop.)

from pmk import PMK, hsv_to_rgb
from pmk.platform.keybow2040 import Keybow2040 as Hardware
import time
from layouts.key_tools import resetKeys

# Configuration constants
long_press_duration = 0.3  # Seconds to hold Mode Key to change modes
debounce_delay = 0.2       # Basic debounce interval for adjustments

# Step sizes for adjustments
hue_step = 0.006
saturation_step = 0.02
value_step = 0.02

# Operational variables
current_mode = 1           # Modes 1 through 6
is_add_mode = True         # True = Add, False = Subtract
mode_key_press_time = 0.0      # Tracks when Mode Key was pressed down
mode_key_handled = False       # Prevents short-press trigger after a long-press

# Non-blocking timer variables
key_debounce_end_time = 0.05 # When keys can be pressed again

# Global variables for keybow and keys
keybow = None
keys = None

initial_hues = [0.0, 0.037, 0.106, 0.32, 0.54, 0.69, 0.77, 0.94]
pale_saturations = [0.9, 0.9, 0.9, 0.88, 0.74, 0.6, 0.74, 0.74]
colour_names = ["red", "orange", "yellow", "green", "blue", "indigo", "violet", "pink"]
# Orange = hsv_to_rgb(0.037, 1, 1)
# Pale_Orange = hsv_to_rgb(0.037, 0.9, 1)
# 

def update_key_led(key):
    """Calculates and pushes current HSV values to a physical hardware key."""
    h, s, v = key.hue, key.saturation, key.value
    r, g, b = hsv_to_rgb(h, s, v)
    key.set_led(r, g, b)

def setup(this_keybow):
    global keybow, keys
    keybow = this_keybow
    keys = keybow.keys
    resetKeys(keybow)
    
    # Configure Mode Key default attributes (menu key)
    keys[0].hue = 0.0
    keys[0].saturation = 0.0
    keys[0].value = 1.0
    update_key_led(keys[0])
    
    # Configure keys 1 to 15 default spectrum attributes
    for i in range(1, 16):
        #keys[i].hue = initialHues[i % len(initialHues)]
        keys[i].hue = initial_hues[i//2]
        keys[i].saturation = 1.0
        if i % 2 == 1:
            keys[i].saturation = pale_saturations[i//2]            
            #print(keys[i].saturation)
        keys[i].value = 1.0
        update_key_led(keys[i])
        
        message = f"{colour_names[i//2]} = {keys[i].rgb[0], keys[i].rgb[1], keys[i].rgb[2]}"
        
        if i % 2 == 1:
            message = "pale_" + message
#        print(message)

def update_key_colours(key):
    """Applies step adjustments to a single key object based on active mode."""
    step_multiplier = 1.0 if is_add_mode else -1.0
    
    if current_mode in [1,4] :
        # Hue wraps around
        key.hue = (key.hue + (hue_step * step_multiplier)) % 1.0
    elif current_mode in [2, 5]:
        # Saturation stops at 0, 1
        key.saturation = max(0.0, min(1.0, key.saturation + (saturation_step * step_multiplier)))
    elif current_mode in [3, 6]:
        # Value stops at 0, 1
        key.value = max(0.0, min(1.0, key.value + (value_step * step_multiplier)))

    update_key_led(key)

def handleModeKey(current_time):

    global current_mode, is_add_mode, mode_key_press_time, mode_key_handled
    global keys

    # Mode Key (Mode and Direction Switcher)
    if keys[0].pressed:
        
        if mode_key_press_time == 0.0:
            #Begin processing key events
            keys[0].led_off()
            mode_key_press_time = current_time
            mode_key_handled = False
        else:
            if not mode_key_handled and (current_time - mode_key_press_time >= long_press_duration):
                current_mode += 1
                if current_mode > 6:
                    current_mode = 1

                mode_key_handled = True
                print("Mode changed to: ", current_mode)
                
                # Turn mode key white
                keys[0].set_led(255, 255, 255)
                
    else:
        #not pressed now
        
        if mode_key_press_time > 0.0:
            #was pressed previously
            
            #was not a mode operation
            if not mode_key_handled:
                is_add_mode = not is_add_mode
              
                print("Direction changed to: ", is_add_mode)
                
                # Turn Mode Key Green or Red
                if is_add_mode:
                    keys[0].set_led(0, 255, 0)
                else:
                    keys[0].set_led(255, 0, 0)
                
            
            mode_key_press_time = 0.0
            mode_key_handled = False




def update():
    """Main update loop handling non-blocking actions and inputs."""

    global key_debounce_end_time
    global keys

    current_time = time.monotonic()

    handleModeKey(current_time)
    # --- HANDLE KEYS 1 to 15 (LED Alterations) ---
    # Only process changes if the debounce window has elapsed
    if current_time >= key_debounce_end_time:
        for i in range(1, 16):
            if keys[i].pressed:
                
                print("RGB: ", keys[i].rgb, ", H:", keys[i].hue, ", S:", keys[i].saturation, ", V:", keys[i].value)
                # Modes 1-3: Target the individual key that was pressed
                if current_mode in [1, 2, 3]:
                    update_key_colours(keys[i])
                
                # Modes 4-6: Target the whole keyboard simultaneously (except Mode Key)
                elif current_mode in [4, 5, 6]:
                    for k in range(1, 16):
                        update_key_colours(keys[k])
                
                # Set future timestamp boundary to ignore rapid bounce inputs
                key_debounce_end_time = current_time + debounce_delay
                break  # Process one key press event flag per cycle iteration

#If not an import, run on your own. Be free!
if __name__ == '__main__':

    keybow = PMK(Hardware())
    setup(keybow)

    while True:
        keybow.update()
        update()


