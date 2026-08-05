from pmk import PMK
from pmk.platform.keybow2040 import Keybow2040 as Hardware
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import usb_hid
import layouts.key_tools as tools
from layouts.key_tools import Colours

keyboard = Keyboard(usb_hid.devices)

cmus_extra_active = False

colour_map = [
    Colours.white,
    Colours.orange,
    Colours.red,
    Colours.black,
    Colours.white,
    Colours.white,
    Colours.pale_yellow,
    Colours.pink,
    Colours.white,
    Colours.indigo,
    Colours.yellow,
    Colours.pale_blue,
    Colours.violet,
    Colours.pale_green,
    Colours.green,
    Colours.blue]


def setup(keybow):
    #mouse = Mouse(usb_hid.devices)
    keybow.led_sleep_enabled = True
    keybow.led_sleep_time = 30
    keys = keybow.keys
    consumer_control = ConsumerControl(usb_hid.devices)

    tools.resetKeys(keybow)

    tools.colour_by_map(keybow, colour_map)


    tools.setKeyEmulation(keybow, keys[0], Keycode.LEFT_ARROW)
    tools.setKeyEmulation(keybow, keys[4], Keycode.DOWN_ARROW)
    tools.setKeyEmulation(keybow, keys[5], Keycode.UP_ARROW)
    tools.setKeyEmulation(keybow, keys[8], Keycode.RIGHT_ARROW)

    # Tab
    @keybow.on_press(keys[1])
    def press_handler(key):
        keyboard.send(Keycode.TAB)
        
    # Enter/Return
    @keybow.on_press(keys[9])
    def press_handler(key):
        keyboard.send(Keycode.RETURN)

    # CMUS Pause = remote
    @keybow.on_press(keys[12])
    def press_handler(key):
        consumer_control.send(ConsumerControlCode.PLAY_PAUSE)
        
    # CMUS Previous view = i
    @keybow.on_press(keys[6])
    def press_handler(key):
        keyboard.send(Keycode.I)
    
    # CMUS Previous view = o
    @keybow.on_press(keys[10])
    def press_handler(key):
        keyboard.send(Keycode.O)
        
    # CMUS something = e
    @keybow.on_press(keys[7])
    def press_handler(key):
        keyboard.send(Keycode.E)


    # CMUS Volume Down = -
    @keybow.on_press(keys[13])
    def press_handler(key):
        consumer_control.send(ConsumerControlCode.VOLUME_DECREMENT)
#        keyboard.send(Keycode.KEYPAD_MINUS)

    # CMUS Volume Up = +
    @keybow.on_press(keys[14])
    def press_handler(key):
        consumer_control.send(ConsumerControlCode.VOLUME_INCREMENT)
#        keyboard.send(Keycode.KEYPAD_PLUS)

    # Screen on F1
    @keybow.on_press(keys[11])
    def press_handler(key):
        keyboard.send(Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, Keycode.GUI, 
                      Keycode.F1)
        
    # Screen off F2
    @keybow.on_press(keys[15])
    def press_handler(key):
        keyboard.send(Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, Keycode.GUI,
                      Keycode.F2)


    @keybow.on_press(keys[2])
    def press_handler(key):
        import layouts.cmus_extra as cmus_extra
        global cmus_extra_active
        cmus_extra_active = True
        cmus_extra.setup(keybow)

def update():
    if cmus_extra_active:
        import layouts.cmus_extra as cmus_extra
        cmus_extra.update()

#If not an import, run on your own. Be free!
if __name__ == '__main__':

    keybow = PMK(Hardware())
    setup(keybow)

    while True:
        keybow.update()
        update()



