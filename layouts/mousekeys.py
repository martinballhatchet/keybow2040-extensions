from pmk import PMK
from pmk.platform.keybow2040 import Keybow2040 as Hardware
import usb_hid
from adafruit_hid.mouse import Mouse
from adafruit_hid.keycode import Keycode
import layouts.key_tools as tools

red_bright = (255, 0, 0)
black = (0, 0, 0)
white = (255,255,255)

directions_held = []

direction_left = 0
direction_right = 1
direction_up = 2
direction_down = 3
direction_scroll_up = 4
direction_scroll_down = 5

mouse = Mouse(usb_hid.devices)

def setup(keybow):
    keys = keybow.keys
    keybow.led_sleep_enabled = True
    keybow.led_sleep_Time = 30
    tools.resetKeys(keybow)


    tools.setModifierKeyEmulation(keybow, keys[0], Keycode.LEFT_CONTROL)
    setMouseMove(keybow, keys[1], direction_left, x=-8)
    tools.setKeyEmulation(keybow, keys[2], Keycode.ESCAPE)
    setMouseMove(keybow, keys[4], direction_down, y=8)
    tools.setMouseButtonEmulation(keybow, mouse, keys[5], Mouse.LEFT_BUTTON)
    setMouseMove(keybow, keys[6], direction_up, y=-8)
    tools.setMouseButtonEmulation(keybow, mouse, keys[7], Mouse.RIGHT_BUTTON)
    tools.setModifierKeyEmulation(keybow, keys[8], Keycode.LEFT_SHIFT)
    setMouseMove(keybow, keys[9], direction_right, x=8)
    #Nothing for 10
    tools.setMouseButtonEmulation(keybow, mouse, keys[11], Mouse.MIDDLE_BUTTON)
    setMouseMove(keybow, keys[12], direction_scroll_down, wheel=-1)
    setMouseMove(keybow, keys[13], direction_scroll_up, wheel=1)

    keys[5].set_led(50,50,255)



def setMouseMove(keybow, key_to_set, direction, x: int = 0, y: int = 0, wheel: int = 0):
    # Mouse move left
    key_to_set.set_led(*white)
    @keybow.on_press(key_to_set)
    def press_handler(key):
        mouse.move(x, y, wheel)

    @keybow.on_hold(key_to_set)
    def hold_handler(key):
        key_to_set.set_led(*red_bright)
        directions_held.append(direction)


    @keybow.on_release(key_to_set)
    def release_handler(key):
        key_to_set.set_led(*white)
        if direction in directions_held:
            directions_held.remove(direction)

def update():

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
