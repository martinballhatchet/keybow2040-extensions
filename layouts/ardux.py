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
#from enum import Enum

class Mode:
    Normal = 0
    Mouse = 1
    Navigation = 2

mouse = Mouse(usb_hid.devices)
consumer = ConsumerControl(usb_hid.devices)
consumer_control = ConsumerControl(usb_hid.devices)
keyboard = Keyboard(usb_hid.devices)
keybow = None
keys = None
timer_started = False
time_press_started = 0
hold_delay = 0.2
current_mode = Mode.Normal

directions_held = []

direction_left = 0
direction_right = 1
direction_up = 2
direction_down = 3
direction_scroll_up = 4
direction_scroll_down = 5

held_keys = []

#Left handed Ardux ... mostly. I can't see why Shift is so complicated, so I've changed it.
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
key_modifiers_active = 0b0000


# Keybow 2040 Hardware Index Tracking Map
# Top Row buttons:    Key 4 (A), Key 5 (R), Key 6 (T), Key 7 (S)
# Bottom Row buttons: Key 0 (E), Key 1 (Y), Key 2 (I), Key 3 (O)

#These are the Keybow keys I'm using. This is "upside down" because for me I'm trying it that way :)
Ardux_Keys = [14, 10, 6, 2, 15, 11, 7, 3]

#OK - got the idea of using a bitmask like this from Google (AI), and I like it. It shows easily which
#of the 8 keys need to be activated. 
default_layer_keybindings = [
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
    (0b00010110, Keycode.QUOTE, "'")
    ]
global_keybindings = [    
    (0b00001111, Keycode.SPACE, "<space>"),
    (0b00010001, Keycode.RETURN, "<return>"),
    (0b01111000, Keycode.TAB, "<tab>"),
    (0b00100001, Keycode.BACKSPACE, "<backspace>"),
    (0b00000000, Keycode.DELETE, "<delete>"),
#    (0b00100010, Keycode., "<shift lock>"), TODO
    (0b00011110, Keycode.CAPS_LOCK, "<caps lock>"),
    (0b00111000, Keycode.ESCAPE, "<escape>")
    ]

#DONE: Exclamation mark
global_key_modifiers = [
    #(Bitmask, mod_position, Keycode, debug print :D)
    #OK - this is NOT pure Ardux.
    (0b10001000, 0b0001, Keycode.SHIFT, "<shift>"),
    (0b10000100, 0b0010, Keycode.LEFT_CONTROL, "<left control>"),
    (0b10000010, 0b0100, Keycode.LEFT_GUI, "<left gui>"),
    (0b10000001, 0b1000, Keycode.LEFT_ALT, "<left alt>")
]


#DONE: Lock on modifiers. I think One shot by default, but hold maybe later for lock? Maybe they are just key_held at that point?
    
#TODO: Hold-tap layers

#DONE: Arrow layer
navigation_binding = 0b00100101


#DONE: Mouse layer
mouse_binding = 0b01010010


#TODO: Commands... Copy, Paste, Cut, Undo, Redo
#TODO: Make some of this easier using the unused codes
#TODO: Function keys?
#TODO: Shift Lock?
#TODO: When Shift (etc) active, pass them through to the Navigation and Mouse mode. Might be as simple as pressing
# them before the navigation
#TODO: Sort out exclamation mark


def setup(this_keybow):
    global keys, keybow
    keybow = this_keybow
    keys = keybow.keys
    keybow.led_sleep_enabled = True
    keybow.led_sleep_time = 30
    tools.resetKeys(keybow)



def update():
    global keys_pressed_for_tap
    global current_mode
    global held_keys
    

    add_to_keys_tapped()

    #Need to do this outside the below as there may not be any keys pressed right now :)
    #... but only if we are in Normal mode
    if current_mode == Mode.Normal:
        check_timers()

    if ((keys_pressed_for_tap != 0) and not any_keys_pressed()):
# Some keys have been pressed but now everything is released!

# Main checks for key presses

        found_keybinding = False
        held_keys.clear()


#Some of these are global
        if keys_pressed_for_tap == navigation_binding:
            print("Toggle Navigation mode")
            current_mode = Mode.Navigation if current_mode != Mode.Navigation else Mode.Normal
            setup_navigation()
            found_keybinding = True
            
        if keys_pressed_for_tap == mouse_binding:
            print("Toggle Mouse mode")
            current_mode = Mode.Mouse if current_mode != Mode.Mouse else Mode.Normal
            setup_mouse()
            found_keybinding = True 

        for key_modifier in global_key_modifiers:
            if key_modifier[0] == keys_pressed_for_tap:
                process_key_modifier(key_modifier)
                found_keybinding = True

        for keybinding in global_keybindings:
            if keybinding[0] == keys_pressed_for_tap:
                process_key(keybinding)
                found_keybinding = True
    
        if current_mode == Mode.Normal:
        
            for keybinding in default_layer_keybindings:
                if keybinding[0] == keys_pressed_for_tap:
                    process_key(keybinding)
                    found_keybinding = True

#I think I only need to run this within "normal mode".


        elif current_mode == Mode.Navigation:
            pass
            found_keybinding = True
            #if we tap the navigation press again, go back to normal
            
        else: #Mouse mode!

            found_keybinding = True
            #if we tap the navigation press again, go back to normal
            #clear the handlers!

        if not found_keybinding:
            print("Missing keybinding: ", f"{keys_pressed_for_tap >> 4:04b} {keys_pressed_for_tap & 0x0F:04b}")
        keybow.set_all(0, 0, 0)
        keys_pressed_for_tap = 0
        set_key_lights_when_unpressed()

    if current_mode == Mode.Mouse:
        move_mouse()
        

def check_timers():
    #so...
    # if we have started a timer
    # .... if nothing pressed, clear the timer
    # ... if something pressed and passed the hold timer then
    # ...... we are in hold mode! Stand by for more code
    # if no timer, but a key is pressed then start the timer :)
    global timer_started
    if timer_started:
        if not any_keys_pressed():
            timer_started = False
            held_keys=[]
        else:
            if (time.monotonic() - time_press_started) > hold_delay:
                store_held_keys()
    else:
        if any_keys_pressed():
            start_timer()

def store_held_keys():
    for index, key_number in enumerate(Ardux_Keys):
        if keybow.keys[key_number].pressed:
            if not index in held_keys:
                held_keys.append(index)
    print("held keys:", held_keys)


def start_timer():
    global time_press_started
    global timer_started
    time_press_started = time.monotonic()
    timer_started = True

def set_key_lights_when_unpressed():
    #OK. So - let's set the "top" row to be blank
    #And then the bottom row, one by one, will match whether or not the modifier is active
    for index, key_number in enumerate(Ardux_Keys):
        if (index < 4):
            keys[key_number].set_led(0,0,0)
        else:
            if modifier_active(index - 4):
                keys[key_number].set_led(255,0,0)
            
            
def modifier_active(key_position):
    return key_modifier_is_active(global_key_modifiers[key_position])

def process_key(keybinding):
    print(keybinding[len(keybinding)-1])
    #This looks a bit magical but basically it's taking all but the last and first items as the
    #keys to pass. Nifty!
    keys_to_send = keybinding[1:len(keybinding)-1]
    keys_to_send = add_modifiers(keys_to_send)
    print(keys_to_send)
    keyboard.send(*keys_to_send)
    
def process_key_modifier(key_modifier):
    global key_modifiers_active
    print(key_modifier[len(key_modifier)-1])
    #Add modifier to current modifiers or take it off
    key_modifiers_active ^= key_modifier[1]
    print(key_modifiers_active)
    

def add_to_keys_tapped():
    global keys_pressed_for_tap
    #OK - we reverse here because we want the most significant bit to start on the left
    for index, key_number in enumerate(reversed(Ardux_Keys)):
        if keys[key_number].pressed:
            keys_pressed_for_tap |= (1 << index)
            keys[key_number].set_led(255, 255, 255)

def any_keys_pressed():
    for index, key_number in enumerate(Ardux_Keys):
        if keybow.keys[key_number].pressed:
            return True
    return False

def get_current_mask():
    mask = 0
    #OK - we reverse here because we want the most significant bit to start on the left
    for index, key_number in enumerate(reversed(Ardux_Keys)):
        if keybow.keys[key_number].pressed:
            #bitshift something what now?
            mask |= (1 << index)    
    return mask

def add_modifiers(keys_to_send):
    for modifier in global_key_modifiers:
        if key_modifier_is_active(modifier):
            keys_to_send += (modifier[2],)
    return keys_to_send        
            

def key_modifier_is_active(modifier):
    return (key_modifiers_active & modifier[1]) > 0


def setup_mouse():
    if (current_mode == Mode.Mouse):
        setMouseMove(keybow, keys[Ardux_Keys[4]], direction_left, x=-8)
        setMouseMove(keybow, keys[Ardux_Keys[5]], direction_down, y=8)
        setMouseMove(keybow, keys[Ardux_Keys[6]], direction_right, x=8)
        setMouseMove(keybow, keys[Ardux_Keys[1]], direction_up, y=-8)
        tools.setMouseButtonEmulation(keybow, mouse, keys[Ardux_Keys[0]], Mouse.LEFT_BUTTON)
        tools.setMouseButtonEmulation(keybow, mouse, keys[Ardux_Keys[2]], Mouse.RIGHT_BUTTON)
        
        setMouseMove(keybow, keys[Ardux_Keys[3]], direction_scroll_up, wheel=1)
        setMouseMove(keybow, keys[Ardux_Keys[7]], direction_scroll_down, wheel=-1)
    else:
        tools.resetKeys(keybow)
        
def setup_navigation():
    if (current_mode == Mode.Navigation):
        tools.setKeyEmulation(keybow, keys[Ardux_Keys[4]], Keycode.LEFT_ARROW)
        tools.setKeyEmulation(keybow, keys[Ardux_Keys[5]], Keycode.DOWN_ARROW)
        tools.setKeyEmulation(keybow, keys[Ardux_Keys[6]], Keycode.RIGHT_ARROW)
        tools.setKeyEmulation(keybow, keys[Ardux_Keys[1]], Keycode.UP_ARROW)
        
        tools.setKeyEmulation(keybow, keys[Ardux_Keys[3]], Keycode.PAGE_UP)
        tools.setKeyEmulation(keybow, keys[Ardux_Keys[7]], Keycode.PAGE_DOWN)
        tools.setKeyEmulation(keybow, keys[Ardux_Keys[0]], Keycode.HOME)
        tools.setKeyEmulation(keybow, keys[Ardux_Keys[2]], Keycode.END)
    else:
        tools.resetKeys(keybow)


def setMouseMove(keybow, key_to_set, direction, x: int = 0, y: int = 0, wheel: int = 0):
    # Mouse move left
    #key_to_set.set_led(*white)
    @keybow.on_press(key_to_set)
    def press_handler(key):
        mouse.move(x, y, wheel)

    @keybow.on_hold(key_to_set)
    def hold_handler(key):
        #key_to_set.set_led(*red_bright)
        directions_held.append(direction)

    @keybow.on_release(key_to_set)
    def release_handler(key):
        #key_to_set.set_led(*white)
        if direction in directions_held:
            directions_held.remove(direction)

def move_mouse():
    if direction_up in directions_held:        
        mouse.move(y = -8)

    if direction_left in directions_held:
        mouse.move(x = -8)

    if direction_right in directions_held:
        mouse.move(x = 8)

    if direction_down in directions_held:
        mouse.move(y = 8)
        
    if direction_scroll_down in directions_held:
        mouse.move(wheel = -1)
        
    if direction_scroll_up in directions_held:
        mouse.move(wheel = 1)



#If not an import, run on your own. Be free!
if __name__ == '__main__':

    keybow = PMK(Hardware())
    setup(keybow)

    while True:
        keybow.update()
        update()

