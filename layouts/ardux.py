from pmk import PMK
from pmk.platform.keybow2040 import Keybow2040 as Hardware
import usb_hid
from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import layouts.key_tools as tools
import time
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

mouse = Mouse(usb_hid.devices)
consumer = ConsumerControl(usb_hid.devices)
consumer_control = ConsumerControl(usb_hid.devices)
keyboard = Keyboard(usb_hid.devices)
keybow = None
keys = None

#OK ... need to be able to distinguish between held and pressed
# Can try using the built in functionality?
#
# Let's do this .. when keys are pressed, we start a timer
# ... when we get to H seconds we say keys are held
# ... thought about doing a keypress when we press down, but that won't work
# ... as we won't know if we are going to hold them
# ... so has to be on the release
# ... so ... until we get to H seconds, capture all keys pressed
# .... when all keys released, send that combo!
# What do we need to implement?
# Combo -> key press
# Combo -> change mode
# Combo -> Lock modifier
# Hold + tap -> key press

keys_pressed_for_tap = 0

debounce_delay = 0.1

# Keybow 2040 Hardware Index Tracking Map
# Top Row buttons:    Key 4 (A), Key 5 (R), Key 6 (T), Key 7 (S)
# Bottom Row buttons: Key 0 (E), Key 1 (Y), Key 2 (I), Key 3 (O)

#These are the Keybow keys I'm using. This is "upside down" because for me I'm trying it that way :)
Ardux_Keys = [14, 10, 6, 2, 15, 11, 7, 3]

#OK - got the idea of using a bitmask like this from Google (AI), and I like it. It shows easily which
#of the 8 keys need to be activated. 
keybindings = [
    #(Bitmask, Keycode, debug print :D)
    (0b10000000, Keycode.S, "S"),
    (0b01000000, Keycode.T, "T"),
    (0b00100000, Keycode.R, "R"),
    (0b00010000, Keycode.A, "A"),
    (0b00001000, Keycode.O, "O"),
    (0b00000100, Keycode.I, "I"),
    (0b00000010, Keycode.Y, "Y"),
    (0b00000001, Keycode.E, "E"),
    (0b00000000, Keycode.T, "T"),
    (0b11000000, Keycode.J, "J"),
    (0b01100000, Keycode.G, "G"),
    (0b00110000, Keycode.F, "F"),
    (0b00001100, Keycode.N, "N"),
    (0b00000110, Keycode.U, "U"),
    (0b00000011, Keycode.C, "C"),
    (0b10100000, Keycode.V, "V"),
    (0b00001010, Keycode.K, "K"),
    (0b00000101, Keycode.H, "H"),
    (0b10010000, Keycode.W, "W"),
    (0b00001001, Keycode.B, "B"),
    (0b11100000, Keycode.X, "X"),
    (0b01110000, Keycode.D, "D"),
    (0b00001110, Keycode.M, "M"),
    (0b00000111, Keycode.L, "L"),
    (0b11010000, Keycode.Q, "Q"),
    (0b00001101, Keycode.P, "P"),
    (0b11110000, Keycode.Z, "Z"),
    (0b01000100, Keycode.ONE, Keycode.SHIFT, "!"), #Special
    (0b00011000, Keycode.FORWARD_SLASH, "/"),
    (0b00010010, Keycode.PERIOD, "."),
    (0b00010100, Keycode.COMMA, ","),
    (0b00010110, Keycode.QUOTE, "'"),
    (0b00001111, Keycode.SPACE, "<space>"),
    (0b00010001, Keycode.RETURN, "<return>"),
    (0b01111000, Keycode.TAB, "<tab>"),
    (0b00100001, Keycode.BACKSPACE, "<backspace>"),
    (0b00000000, Keycode.DELETE, "<delete>"),
    (0b11100001, Keycode.SHIFT, "<shift>"),
#    (0b00100010, Keycode., "<shift lock>"), TODO
    (0b00011110, Keycode.CAPS_LOCK, "<caps lock>"),
    (0b10000001, Keycode.LEFT_CONTROL, "<left control>"),
    (0b10000100, Keycode.LEFT_ALT, "<left alt>"),
    (0b10000010, Keycode.LEFT_GUI, "<left gui>"),
    (0b00111000, Keycode.ESCAPE, "<escape>")


#TODO: Exclamation mark
#TODO: Lock on modifiers
    
#TODO: Hold-tap layers

#TODO: Arrow layer
#TODO: Mouse layer
#TODO: Commands... Copy, Paste, Cut, Undo, Redo
#TODO: Function keys?

    ]



def setup(this_keybow):
    global keys, keybow
    keybow = this_keybow
    keys = keybow.keys
#    keybow.led_sleep_enabled = True
#    keybow.led_sleep_time = 30
    tools.resetKeys(keybow)



def update():
    #print(keybow.get_pressed())
    # So - let's check what's pressed. Let's start with one key as we'll have to do some debounce stuff
    global keys_pressed_for_tap
    #print("hi")
    #current_mask = get_current_mask()
    
    
    add_to_keys_tapped()
    
    if ((keys_pressed_for_tap != 0) and not any_keys_pressed()):
# Some keys have been pressed but now everything is released!

        found_keybinding = False
        for keybinding in keybindings:
            if keybinding[0] == keys_pressed_for_tap:
                process_key(keybinding)
                found_keybinding = True
        
        if not found_keybinding:
            print("Missing keybinding: ", f"{keys_pressed_for_tap >> 4:04b} {keys_pressed_for_tap & 0x0F:04b}")
        keybow.set_all(0, 0, 0)
        keys_pressed_for_tap = 0
        


def process_key(keybinding):
    print(keybinding[2])
    #This looks a bit magical but basically it's taking all but the last and first items as the
    #keys to pass. Nifty!
    keys_to_send = keybinding[1:len(keybinding)-1]
    keyboard.send(*keys_to_send)

def add_to_keys_tapped():
    global keys_pressed_for_tap
    #mask = 0
    #OK - we reverse here because we want the most significant bit to start on the left
    for index, key_number in enumerate(reversed(Ardux_Keys)):
        if keybow.keys[key_number].pressed:
            keys_pressed_for_tap |= (1 << index)
            keybow.keys[key_number].set_led(255, 255, 255)

def any_keys_pressed():
    
    for index, key_number in enumerate(reversed(Ardux_Keys)):
        if keybow.keys[key_number].pressed:
            return True
    return False

def get_current_mask():
    mask = 0
    #OK - we reverse here because we want the most significant bit to start on the left
    for index, key_number in enumerate(reversed(Ardux_Keys)):
        if keybow.keys[key_number].pressed:
            #bitshift something what now?
            #print(mask)
            mask |= (1 << index)
            #print(mask)
    
    
    return mask











#If not an import, run on your own. Be free!
if __name__ == '__main__':

    keybow = PMK(Hardware())
    setup(keybow)

    while True:
        keybow.update()
        update()

