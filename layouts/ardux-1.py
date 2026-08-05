import time
import board
import usb_hid
from pmk import PMK
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from pmk.platform.keybow2040 import Keybow2040

# Initialize Hardware and HID Devices
keybow = PMK(Keybow2040())
keys = keybow.keys
keyboard = Keyboard(usb_hid.devices)
mouse = Mouse(usb_hid.devices)
consumer_control = ConsumerControl(usb_hid.devices)

# Layers Definitions
BASE = 0
PAREN = 1
NUMBER = 2
CUSTOM = 3
SYMBOL = 4
MOUSE = 5
NAV = 6

current_layer = BASE

# Mapping of the 8 Ardux positions to Keybow 2040 indices
# C1, C2, C3, C4 on Row 1 (S, T, R, A)
# C1, C2, C3, C4 on Row 2 (O, I, Y, E)
ARDUX_KEYS = [0, 1, 2, 3, 4, 5, 6, 7]

# State Tracking
key_states = [False] * 8
last_mask = 0
combo_active = False
press_time = 0.0
hold_triggered = False

# Layer RGB Color Palettes
LAYER_COLORS = {
    BASE: (0, 255, 255),      # Cyan
    PAREN: (255, 0, 255),     # Magenta
    NUMBER: (255, 255, 0),    # Yellow
    CUSTOM: (0, 0, 255),      # Blue
    SYMBOL: (255, 128, 0),    # Orange
    MOUSE: (0, 255, 0),       # Green
    NAV: (255, 0, 0)          # Red
}

def update_leds():
    color = LAYER_COLORS.get(current_layer, (255, 255, 255))
    for idx in ARDUX_KEYS:
        keys[idx].set_led(*color)
    # Status/Reset key mapping visual indicator
    keys[8].set_led(50, 50, 50)
    for idx in range(9, 16):
        keys[idx].set_led(0, 0, 0)

# Helper execution functions for multi-type targets
def send_key(code):
    if isinstance(code, tuple):
        for k in code: keyboard.press(k)
        for k in code: keyboard.release(k)
    else:
        keyboard.send(code)

def press_key(code):
    if isinstance(code, tuple):
        for k in code: keyboard.press(k)
    else:
        keyboard.press(code)

def release_key(code):
    if isinstance(code, tuple):
        for k in code: keyboard.release(k)
    else:
        keyboard.release(code)

def send_cc(code):
    consumer_control.send(code)

def send_mouse(action):
    if action == "M_UP": mouse.move(y=-5)
    elif action == "M_DOWN": mouse.move(y=5)
    elif action == "M_LEFT": mouse.move(x=-5)
    elif action == "M_RIGHT": mouse.move(x=5)
    elif action == "W_UP": mouse.move(wheel=1)
    elif action == "W_DOWN": mouse.move(wheel=-1)
    elif action == "B1_CLK": mouse.click(Mouse.LEFT_BUTTON)
    elif action == "B2_CLK": mouse.click(Mouse.RIGHT_BUTTON)

# Core Map Matrices
BASE_MAP = {
    0b10000000: (send_key, Keycode.S),
    0b01000000: (send_key, Keycode.T),
    0b00100000: (send_key, Keycode.R),
    0b00010000: (send_key, Keycode.A),
    0b00001000: (send_key, Keycode.O),
    0b00000100: (send_key, Keycode.I),
    0b00000010: (send_key, Keycode.Y),
    0b00000001: (send_key, Keycode.E),
    # Combos
    0b11000000: (send_key, Keycode.J),
    0b01100000: (send_key, Keycode.G),
    0b00110000: (send_key, Keycode.F),
    0b00001100: (send_key, Keycode.N),
    0b00000110: (send_key, Keycode.U),
    0b00000011: (send_key, Keycode.C),
    0b10100000: (send_key, Keycode.V),
    0b00001010: (send_key, Keycode.K),
    0b00000101: (send_key, Keycode.H),
    0b10010000: (send_key, Keycode.W),
    0b00001001: (send_key, Keycode.B),
    0b11100000: (send_key, Keycode.X),
    0b01110000: (send_key, Keycode.D),
    0b00001110: (send_key, Keycode.M),
    0b00000111: (send_key, Keycode.L),
    0b11010000: (send_key, Keycode.Q),
    0b00001101: (send_key, Keycode.P),
    0b11110000: (send_key, Keycode.Z),
    0b01000100: (send_key, Keycode.ONE), # !
    0b00011000: (send_key, Keycode.FORWARD_SLASH),
    0b00010010: (send_key, Keycode.PERIOD),
    0b00010100: (send_key, Keycode.COMMA),
    0b00010110: (send_key, Keycode.QUOTE),
    # Global Combos
    0b11111111: (send_key, Keycode.SPACE),
    0b00010001: (send_key, Keycode.ENTER),
    0b01111000: (send_key, Keycode.TAB),
    0b00100001: (send_key, Keycode.BACKSPACE),
    0b00100100: (send_key, Keycode.DELETE),
    0b11100001: (press_key, Keycode.SHIFT), # Handled as permanent/toggle via sequence context
    0b00100010: (send_key, Keycode.CAPS_LOCK),
    0b00011110: (send_key, Keycode.CAPS_LOCK),
    0b10000001: (press_key, Keycode.CONTROL),
    0b10000100: (press_key, Keycode.ALT),
    0b10000010: (press_key, Keycode.GUI),
    0b00111000: (send_key, Keycode.ESCAPE),
}

PAREN_MAP = {
    0b10000000: (send_key, Keycode.LEFT_BRACKET),
    0b01000000: (send_key, Keycode.LEFT_BRACKET),
    0b00100000: (send_key, Keycode.RIGHT_BRACKET),
    c0b00001000: (send_key, Keycode.RIGHT_BRACKET),
    0b00000100: (send_key, Keycode.LEFT_BRACKET),
    0b00000010: (send_key, Keycode.RIGHT_BRACKET),
}

NUMBER_MAP = {
    0b00010000: (send_key, Keycode.ONE),
    0b00100000: (send_key, Keycode.TWO),
    0b01000000: (send_key, Keycode.THREE),
    0b00000001: (send_key, Keycode.FOUR),
    0b00000010: (send_key, Keycode.FIVE),
    0b00000100: (send_key, Keycode.SIX),
    0b00110000: (send_key, Keycode.SEVEN),
    0b01100000: (send_key, Keycode.EIGHT),
    0b00000011: (send_key, Keycode.NINE),
    0b00000110: (send_key, Keycode.ZERO),
}

CUSTOM_MAP = {
    0b01000000: (send_cc, ConsumerControlCode.VOLUME_INCREMENT),
    0b00100000: (send_key, Keycode.INSERT),
    0b00010000: (send_cc, ConsumerControlCode.MUTE),
    0b00000100: (send_cc, ConsumerControlCode.VOLUME_DECREMENT),
    0b00000010: (send_key, Keycode.PRINT_SCREEN),
    0b00000001: (press_key, Keycode.RIGHT_SHIFT),
}

SYMBOL_MAP = {
    0b10000000: (send_key, Keycode.GRAVE_ACCENT),
    0b01000000: (send_key, Keycode.SEMICOLON),
    0b00100000: (send_key, Keycode.BACKSLASH),
    0b00010000: (send_key, Keycode.ONE), # Keycode.ONE with shift is !
    0b00001000: (send_key, Keycode.EQUALS),
    0b00000100: (send_key, Keycode.MINUS),
    0b00000010: (send_key, Keycode.FORWARD_SLASH), # combined with shift handles ?
}

MOUSE_MAP = {
    0b10000000: (send_mouse, "W_UP"),
    0b01000000: (send_mouse, "B2_CLK"),
    0b00100000: (send_mouse, "M_UP"),
    0b00010000: (send_mouse, "B1_CLK"),
    0b00001000: (send_mouse, "W_DOWN"),
    0b00000100: (send_mouse, "M_LEFT"),
    0b00000010: (send_mouse, "M_DOWN"),
    0b00000001: (send_mouse, "M_RIGHT"),
}

NAV_MAP = {
    0b10000000: (send_key, Keycode.PAGE_UP),
    0b01000000: (send_key, Keycode.HOME),
    0b00100000: (send_key, Keycode.UP_ARROW),
    0b00010000: (send_key, Keycode.END),
    0b00001000: (send_key, Keycode.PAGE_DOWN),
    0b00000100: (send_key, Keycode.LEFT_ARROW),
    0b00000010: (send_key, Keycode.DOWN_ARROW),
    0b00000001: (send_key, Keycode.RIGHT_ARROW),
}

LAYER_MAPS = {
    BASE: BASE_MAP,
    PAREN: PAREN_MAP,
    NUMBER: NUMBER_MAP,
    CUSTOM: CUSTOM_MAP,
    SYMBOL: SYMBOL_MAP,
    MOUSE: MOUSE_MAP,
    NAV: NAV_MAP,
}

# Explicit layer sticky release cleanup tracker
active_modifiers = []

def release_all_modifiers():
    global active_modifiers
    for k in active_modifiers:
        keyboard.release(k)
    active_modifiers = []

update_leds()

while True:
    keybow.update()
    
    # Emergency state reset on Keybow button 8
    if keys[8].pressed:
        current_layer = BASE
        release_all_modifiers()
        update_leds()
        time.sleep(0.3)
        continue

    # Sample current 8-key chord footprint
    changed = False
    for i, idx in enumerate(ARDUX_KEYS):
        p = keys[idx].pressed
        if p != key_states[i]:
            key_states[i] = p
            changed = True

    if changed:
        current_mask = 0
        for i in range(8):
            if key_states[i]:
                current_mask |= (1 << (7 - i))
        
        if current_mask != 0:
            if last_mask == 0:
                press_time = time.monotonic()
                hold_triggered = False
            last_mask |= current_mask
            combo_active = True
        else:
            # Chord released completely, parse resolve phase
            if combo_active and not hold_triggered:
                # Layer toggle checking first (Multi-tap style sequences)
                if last_mask == 0b01000011: # T, Y, A sequence chorded
                    current_layer = BASE if current_layer == MOUSE else MOUSE
                elif last_mask == 0b00100101: # R, I, E sequence chorded
                    current_layer = BASE if current_layer == NAV else NAV
                else:
                    # Execute base mapping actions
                    current_map = LAYER_MAPS.get(current_layer, BASE_MAP)
                    action_tuple = current_map.get(last_mask)
                    
                    # Fall back to base map if combo omitted in functional layers
                    if not action_tuple and current_layer != BASE:
                        action_tuple = BASE_MAP.get(last_mask)
                        
                    if action_tuple:
                        func, val = action_tuple
                        if func in (press_key,):
                            func(val)
                            if val not in active_modifiers:
                                active_modifiers.append(val)
                        else:
                            # Contextual shifts for missing explicit key codes
                            if current_layer == SYMBOL and last_mask == 0b00010000: # !
                                keyboard.press(Keycode.SHIFT)
                                func(val)
                                keyboard.release(Keycode.SHIFT)
                            elif current_layer == SYMBOL and last_mask == 0b00000010: # ?
                                keyboard.press(Keycode.SHIFT)
                                func(val)
                                keyboard.release(Keycode.SHIFT)
                            else:
                                func(val)
                                
                # Auto teardown clean sticky modifiers on base structural keys
                                # Auto teardown clean sticky modifiers on base structural keys
                if last_mask not in [0b11100001, 0b10000001, 0b10000100, 0b10000010]:
                    release_all_modifiers()

            # Tear down operational states
            last_mask = 0
            combo_active = False
            hold_triggered = False
            update_leds()

    # Dynamic temporal evaluation for Hold-Tap Actions
    if combo_active and not hold_triggered:
        if (time.monotonic() - press_time) > 0.250: # 250ms hold trigger threshold
            # S hold triggers Number Layer
            if last_mask == 0b10000000 and current_layer == BASE:
                current_layer = NUMBER
                hold_triggered = True
                update_leds()
            # A hold triggers Parentheticals Layer
            elif last_mask == 0b00010000 and current_layer == BASE:
                current_layer = PAREN
                hold_triggered = True
                update_leds()
            # O hold triggers Custom Layer
            elif last_mask == 0b00001000 and current_layer == BASE:
                current_layer = CUSTOM
                hold_triggered = True
                update_leds()
            # E hold triggers Symbol Layer
            elif last_mask == 0b00000001 and current_layer == BASE:
                current_layer = SYMBOL
                hold_triggered = True
                update_leds()

    # Prevent polling saturation issues
    time.sleep(0.01)

