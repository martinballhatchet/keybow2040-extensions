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



#Left handed Ardux ... mostly. I can't see why Shift is so complicated, so I've changed it.

#These are the Keybow keys I'm using.
Ardux_Keys = [1, 5, 9, 13, 0, 4, 8, 12]


"""
Some unused keys
1100 0010
0100 1010
0100 0010
0010 0100
0100 1000
0100 0010
0100 0001
0101 0000
0010 1000
0010 0010 -> will be shift lock

"""




class Mode:
    Normal = 0
    Mouse = 1
    Navigation = 2
    Hold = 3

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
leaving_hold = False
current_hue = 0.5

directions_held = []

direction_left = 0
direction_right = 1
direction_up = 2
direction_down = 3
direction_scroll_up = 4
direction_scroll_down = 5

held_keys = 0


keys_pressed_for_tap = 0
key_modifiers_active = 0b0000

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

holdable_combos = [
    #Bitmask of hold key, Bitmask of taps, key to press, debug print
    #First - numbers - now, I'm using a different method here, it's
    #called BINARY
    (0b10000000, (0b00001000, Keycode.ZERO, "0")),
    (0b10000000, (0b00010000, Keycode.ONE, "1")),
    (0b10000000, (0b00100000, Keycode.TWO, "2")),
    (0b10000000, (0b00110000, Keycode.THREE, "3")),
    (0b10000000, (0b01000000, Keycode.FOUR, "4")),
    (0b10000000, (0b01010000, Keycode.FIVE, "5")),
    (0b10000000, (0b01100000, Keycode.SIX, "6")),
    (0b10000000, (0b01110000, Keycode.SEVEN, "7")),
    (0b10000000, (0b00000001, Keycode.EIGHT, "8")),
    (0b10000000, (0b00010001, Keycode.NINE, "9")),
    #Now Ardux Parantheticals
    (0b00010000, (0b10000000, Keycode.LEFT_BRACKET, Keycode.SHIFT, "{")),
    (0b00010000, (0b01000000, Keycode.NINE, Keycode.SHIFT, "(")),
    (0b00010000, (0b00100000, Keycode.ZERO, Keycode.SHIFT, ")")),
    (0b00010000, (0b00001000, Keycode.RIGHT_BRACKET, Keycode.SHIFT, "}")),
    (0b00010000, (0b00000100, Keycode.LEFT_BRACKET, "[")),
    (0b00010000, (0b00000010, Keycode.RIGHT_BRACKET, "]")),
    #Now symbols - but I'm going rogue again.
    #We already have exclamation mark as a global
    #and I am much more likely to use double-quote " than ` backtick
    #Oh - UK layout means this will break for others, I am sorry
    (0b00000001, (0b10000000, Keycode.TWO, Keycode.SHIFT, "\"")),
    (0b00000001, (0b01000000, Keycode.SEMICOLON, ";")),
    (0b00000001, (0b00100000, Keycode.KEYPAD_BACKSLASH,"\\")),
    (0b00000001, (0b00010000, Keycode.POUND, "#")),
    (0b00000001, (0b00001000, Keycode.EQUALS, "=")),
    (0b00000001, (0b00000100, Keycode.MINUS, "-")),
    (0b00000001, (0b00000010, Keycode.FORWARD_SLASH, Keycode.SHIFT, "?")),

    
]

#DONE: Lock on modifiers. I think One shot by default, but hold maybe later for lock? Maybe they are just key_held at that point?
    


#DONE: Arrow layer
navigation_binding = 0b00100101


#DONE: Mouse layer
mouse_binding = 0b01010010

#TODO: Finish Hold-tap layers
#TODO: Fix: When coming out of hold tap, modifiers aren't reapplied
#TODO: Commands... Copy, Paste, Cut, Undo, Redo - not the ones that Ardux wants
#TODO: Make some of this easier using the unused codes
#TODO: Look for things I need that aren't there - e.g. ~
#TODO: Function keys?
#TODO: Shift Lock?
#TODO: When Shift (etc) active, pass them through to the Navigation and Mouse mode. Might be as simple as pressing
# them before the navigation
#TODO: Sort out exclamation mark
#TODO: Get return working in nav modes
#TODO: FIX: Getting out of navigation mode activates Page Up
#TODO: Add Autocomplete mode - type then <space> puts word, but pressing <undo> deletes all characters except ones
#      typed

def setup(this_keybow):
    global keys, keybow
    keybow = this_keybow
    keys = keybow.keys
    keybow.led_sleep_enabled = True
    keybow.led_sleep_time = 30
    tools.resetKeys(keybow)


def update():
    global keys_pressed_for_tap, current_mode, leaving_hold
    
    check_timers()

    if current_mode == Mode.Hold:
        check_for_hold_taps()
        
    else:

        if leaving_hold:
            #Don't want to process the rest of everything, but we
            #can now clear held keys.
            #Also clear tapped keys so we start from a clean slate
            for key in keys_from_bitmask(held_keys):
                key.set_led(0, 0, 0)
                
            set_held_keys(0)
            keys_pressed_for_tap = 0 
            leaving_hold = False
        else:

            add_to_keys_tapped()
            if ((keys_pressed_for_tap != 0) and not any_keys_pressed()):
        # Some keys have been pressed but now everything is released!
        #(Note: will need a special minimal version of this for Hold mode. "Everything else is released" or something)

        # Main checks for key presses

                found_keybinding = False

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

                elif current_mode == Mode.Navigation:
                    found_keybinding = True
                    
                else: #Mouse mode!
                    found_keybinding = True

                if not found_keybinding:
                    print("Missing keybinding: ", f"{keys_pressed_for_tap >> 4:04b} {keys_pressed_for_tap & 0x0F:04b}")
                keybow.set_all(0, 0, 0)
                keys_pressed_for_tap = 0
                set_key_lights_when_unpressed()

        if current_mode == Mode.Mouse:
            move_mouse()
            
    set_colours()

def int_as_binary(value):
    return f"{value >> 4:04b} {value & 0x0F:04b}"


    

def check_for_hold_taps():
    global keys_pressed_for_tap
    #Only come into this when we are in hold mode
    if not current_mode == Mode.Hold:
        raise Exception("We are trying to check for hold taps, but not in Hold Mode!")
        
    #print("Checking for hold taps!")

    #Am going to use the add_to_keys_tapped() function 
    add_to_keys_tapped(exclude_bitmask = held_keys)
            
#    if (keys_pressed_for_tap) > 0:
#        print("Held keys: ", int_as_binary(held_keys), ", Tapped keys: ", int_as_binary(keys_pressed_for_tap), "... now process them!")
        #print(tapped_keys, ":", held_keys, ":", keys_pressed_for_tap)
#    print(held_keys, ":", keys_pressed_for_tap)
#    print(any_keys_pressed(held_keys))

    if (keys_pressed_for_tap > 0) and not any_keys_pressed(held_keys):
#        print("hi")
        #We have some tapped keys, and now everything is released. 
        # Let's see if we can find a combo for this!
        found_combo = False
        for holdable_combo in holdable_combos:
            if (holdable_combo[0] == held_keys) and (holdable_combo[1][0] == keys_pressed_for_tap):
#                print("Found hold-tap combo: ", f"{held_keys >> 4:04b} {held_keys & 0x0F:04b}", ":", f"{keys_pressed_for_tap >> 4:04b} {keys_pressed_for_tap & 0x0F:04b}")
                process_key(holdable_combo[1])
                found_combo = True

        if not found_combo:
            print("Missing hold-tap combo: ", int_as_binary(held_keys), ":", int_as_binary(keys_pressed_for_tap))
        
        #Clear the tapped keys now - we are done with them.
        for key in keys_from_bitmask(keys_pressed_for_tap):
            key.set_led(0, 0, 0)
        keys_pressed_for_tap = 0
        
    #TODO: clear colours
    #No, non, no ... we need holdables!
    #holdable_keys
    #holdable_consumer_controls
    #define some combos that can be held. Anything above these gets put into tapped.
    #nah - we have to go with first key held to activate combo I think. If we need cleverer combos later, do them later.
    #Sigh.
    #We should then have holdable + tapped = key_press
    #First holdables should be the normal layers. Can think about whether other holdables make sense - but beware! If there are overlaps

def check_timers():
    global current_mode
    #so...
    # if we have started a timer
    # .... if nothing pressed, clear the timer
    # ... if something pressed and passed the hold timer then
    # ...... we are in hold mode! Stand by for more code
    # if no timer, but a holdable key is pressed then start the timer :)
    
    #First key held is the on that will activate upon release
    global timer_started
    global leaving_hold
    global keys_pressed_for_tap

    if not any_holdable_keys_pressed():
        if (current_mode == Mode.Hold):
            #We were in hold mode - let's not clear held keys just yet
            # ... main loop needs to know we are coming out of hold
            leaving_hold = True
        else:
            #We weren't holding, so let's clear held_keys
            if held_keys >0 : set_held_keys(0)
        
 #       if timer_started: print("timer stopped")
        timer_started = False
        current_mode = Mode.Normal

    else:
        if timer_started:
#            print(time.monotonic() - time_press_started)
            if (time.monotonic() - time_press_started) > hold_delay:
                #We are locked in. We are in Hold Mode Team!
                print("Hold mode")
                current_mode = Mode.Hold
                timer_started = False

                #Reset these now - we are in hold mode, so we don't want to process any taps that were pressed before the hold was activated
                keys_pressed_for_tap = 0
        else:            
        #Timer not started. If we are already in hold mode, no need to start timer.
            if not current_mode == Mode.Hold:
#                print("timer started!")
                start_timer()
                store_held_keys()
                
def get_holdable_bitmasks():
    holdables = []
    for item in holdable_combos:
        if not item[0] in holdables:
            holdables.append(item[0])
    return holdables


def store_held_keys():
    set_held_keys(get_held_holdables())


def any_holdable_keys_pressed():
    return get_held_holdables() > 0


def get_held_holdables():
    held_holdables = 0
    holdable_bitmasks = get_holdable_bitmasks() 
    for index, key_number in enumerate(reversed(Ardux_Keys)):
        if keybow.keys[key_number].pressed and check_bits(holdable_bitmasks, index):
            held_holdables = set_bit(held_keys, index)
    return held_holdables


def set_held_keys(value):
    global held_keys
    #print("Setting held keys:", int_as_binary(value), ", from:", source, ", leaving hold:", leaving_hold)
    held_keys = value








def ardux_key_pressed(index):
    return ardux_key_by_index(index).pressed

def ardux_key_by_index(index):
    return keys[Ardux_Keys[7 - index]]

def keys_from_bitmask(bitmask):
    return_keys = []
    for index in range(8):
        if (check_bit(bitmask, index)):
            return_keys.append(ardux_key_by_index(index))
    
    return return_keys

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

def set_bit(value, bit_index):
    return value | (1 << bit_index)

def clear_bit(value, bit_index):
    return value & ~(1 << bit_index)

def get_bit(value, bit_index):
    return value & (1 << bit_index)

def check_bit(value, bit_index):
    return get_bit(value, bit_index) > 0

def check_bits(list_of_values, bit_index):    
    for value in list_of_values:
        if check_bit(value, bit_index): return True
    return False

            
def modifier_active(key_position):
    return key_modifier_is_active(global_key_modifiers[key_position])


def process_key(keybinding):
    print(keybinding[len(keybinding)-1])
    #This looks a bit magical but basically it's taking all but the last and first items as the
    #keys to pass. Nifty!
    keys_to_send = keybinding[1:len(keybinding)-1]
    keys_to_send = add_modifiers(keys_to_send)
    #print(keys_to_send)
    keyboard.send(*keys_to_send)
    
def process_key_modifier(key_modifier):
    global key_modifiers_active
    print(key_modifier[len(key_modifier)-1])
    #Add modifier to current modifiers or take it off
    key_modifiers_active ^= key_modifier[1]
    print(key_modifiers_active)
    

def add_to_keys_tapped(exclude_bitmask = 0):
    global keys_pressed_for_tap
    for index in range(8):
        if not check_bit(exclude_bitmask, index):
            if ardux_key_pressed(index):
#                print("Adding key to tapped: ", index, "exclude:", int_as_binary(exclude_bitmask))
                keys_pressed_for_tap |= (1 << index)
                ardux_key_by_index(index).set_led(255, 255, 255)
 


def any_keys_pressed(exclude_bitmask = 0):
    for index, key_number in (enumerate(reversed(Ardux_Keys))):
        if keybow.keys[key_number].pressed and not check_bit(exclude_bitmask, index):
            return True
    return False

def get_current_mask():
    mask = 0
    #OK - we reverse here because we want the most significant bit to start on the left
    for index in range(8):
        if ardux_key_pressed(index):
            #bitshift
            mask |= (1 << index)    
    return mask

def add_modifiers(keys_to_send):
    for modifier in global_key_modifiers:
        if key_modifier_is_active(modifier):
            keys_to_send += (modifier[2],)
    return keys_to_send        
           

def key_modifier_is_active(modifier):
    return (key_modifiers_active & modifier[1]) > 0

def key_number_is_in_keys_integer(key_number, keys_integer):
    return ((1 << key_number) & keys_integer) > 0

def setup_mouse():
    if (current_mode == Mode.Mouse):
        set_mouse_move(keybow, keys[Ardux_Keys[4]], direction_left, x=-8)
        set_mouse_move(keybow, keys[Ardux_Keys[5]], direction_down, y=8)
        set_mouse_move(keybow, keys[Ardux_Keys[6]], direction_right, x=8)
        set_mouse_move(keybow, keys[Ardux_Keys[1]], direction_up, y=-8)
        tools.setMouseButtonEmulation(keybow, mouse, keys[Ardux_Keys[0]], Mouse.LEFT_BUTTON)
        tools.setMouseButtonEmulation(keybow, mouse, keys[Ardux_Keys[2]], Mouse.RIGHT_BUTTON)
        
        set_mouse_move(keybow, keys[Ardux_Keys[3]], direction_scroll_up, wheel=1)
        set_mouse_move(keybow, keys[Ardux_Keys[7]], direction_scroll_down, wheel=-1)
    else:
        tools.resetKeys(keybow)
        
def setup_navigation():
    if (current_mode == Mode.Navigation):
        
        #Nah, can't do this - will have to treat as taps and holds - separately
        #Maybe we can at least use the built in hold functionality? Dunno
        
        
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


def set_mouse_move(keybow, key_to_set, direction, x: int = 0, y: int = 0, wheel: int = 0):
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

def set_colours():
    global current_hue
    from pmk import hsv_to_rgb
    # Hue wraps around
    current_hue = (current_hue + 0.0005) % 1.0
    r, g, b = hsv_to_rgb(current_hue, 1.0, 0.5)
    keys[15].set_led(r, g, b)

#If not an import, run on your own. Be free!
if __name__ == '__main__':

    keybow = PMK(Hardware())
    setup(keybow)

    while True:
        keybow.update()
        update()

