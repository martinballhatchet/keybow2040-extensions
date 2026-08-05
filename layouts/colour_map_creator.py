# Yes - "Colour", not "Color". I am British.
# (Just be glad I'm not dealing with my neighbour's favourite doughnut shop.)

from pmk import PMK, hsv_to_rgb
from pmk.platform.keybow2040 import Keybow2040 as Hardware
import time
from layouts.key_tools import resetKeys
from layouts.key_tools import Colours
import layouts.key_tools

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
colours = [
    Colours.black,
    Colours.red, 
    Colours.pale_red,
    Colours.orange,
    Colours.pale_orange,
    Colours.yellow,
    Colours.pale_yellow,
    Colours.green,
    Colours.pale_green,
    Colours.blue,
    Colours.pale_blue,
    Colours.indigo,
    Colours.pale_indigo,
    Colours.violet,
    Colours.pale_violet,
    Colours.pink,
    Colours.pale_pink,
    Colours.white]

keyIndices = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]


def setup(this_keybow):
    global keybow, keys
    keybow = this_keybow
    keys = keybow.keys
    resetKeys(keybow)
    
    
    for i in range(16):
        key_to_set = keys[i]
        
        @keybow.on_press(key_to_set)
        def press_handler(key):
            keyNumber = key.number
            global keyIndices
            keyIndices[keyNumber] += 1
            if keyIndices[keyNumber] >= len(colours):
                keyIndices[keyNumber] = 0
            key.set_led(*colours[keyIndices[keyNumber]])
            print(keyNumber, keyIndices[keyNumber])
            



def update():
    pass

#If not an import, run on your own. Be free!
if __name__ == '__main__':

    keybow = PMK(Hardware())
    setup(keybow)

    while True:
        keybow.update()
        update()




