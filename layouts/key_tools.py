from adafruit_hid.keyboard import Keyboard
import usb_hid

keyboard = Keyboard(usb_hid.devices)

black = (0, 0, 0)

def resetKeys(keybow):
    
    keybow.set_all(*black)

    # Clear all the keys except the main shifter
    
    keys = keybow.keys
    for x in range(16):
        keys[x].hold_time = 0.5
        if (x != 3):
            # Clear decorators slightly more concisely :) 
            keys[x].press_function = None
            keys[x].hold_function = None
            keys[x].release_function = None

# This sets up each of key press, key hold and key release.
# It's more or less making a PMK key replicate a "normal" key
def setKeyEmulation(keybow, key_to_set, keycode):
    @keybow.on_press(key_to_set)
    def press_handler(key):
        keyboard.send(keycode)
    @keybow.on_hold(key_to_set)
    def hold_handler(key):
        keyboard.press(keycode)
    @keybow.on_release(key_to_set)
    def release_handler(key):
        keyboard.release(keycode)
        
# This sets up just key press and key release.
# It's more or less making a PMK key replicate a "modifier" key
def setModifierKeyEmulation(keybow, key_to_set, keycode):
    @keybow.on_press(key_to_set)
    def press_handler(key):
        keyboard.press(keycode)
    @keybow.on_release(key_to_set)
    def release_handler(key):
        keyboard.release(keycode)

# Similar to above, but mouse buttons
def setMouseButtonEmulation(keybow, mouse, key_to_set, mouseButton):
    @keybow.on_press(key_to_set)
    def press_handler(key):
        mouse.click(mouseButton)
    @keybow.on_hold(key_to_set)
    def hold_handler(key):
        mouse.press(mouseButton)
    @keybow.on_release(key_to_set)
    def release_handler(key):
        mouse.release(mouseButton)

