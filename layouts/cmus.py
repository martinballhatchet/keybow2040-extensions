from pmk import PMK
from pmk.platform.keybow2040 import Keybow2040 as Hardware
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import usb_hid
import layouts.key_tools as tools

keyboard = Keyboard(usb_hid.devices)

red_bright = (255, 0, 0)
red_faded = (32, 0, 0)
black = (0, 0, 0)
yellow = (255,255,0)

cmus_extra_active = False


def setup(keybow):
    #mouse = Mouse(usb_hid.devices)
    keybow.led_sleep_Time = 30
    keys = keybow.keys
    consumer_control = ConsumerControl(usb_hid.devices)
    keybow.set_all(*black)

    tools.resetKeys(keybow)

    # Arrows
    keys[0].set_led(*yellow)
    keys[4].set_led(*yellow)
    keys[5].set_led(*yellow)
    keys[8].set_led(*yellow)


    tools.setKeyEmulation(keybow, keys[0], Keycode.LEFT_ARROW)
    tools.setKeyEmulation(keybow, keys[4], Keycode.DOWN_ARROW)
    tools.setKeyEmulation(keybow, keys[5], Keycode.UP_ARROW)
    tools.setKeyEmulation(keybow, keys[8], Keycode.RIGHT_ARROW)

    # Tab
    keys[1].set_led(68, 68, 68)
    @keybow.on_press(keys[1])
    def press_handler(key):
        keyboard.send(Keycode.TAB)


    # Enter/Return
    keys[9].set_led(255,100,100)
    @keybow.on_press(keys[9])
    def press_handler(key):
        keyboard.send(Keycode.RETURN)

    # CMUS Pause = remote
    keys[12].set_led(0,255,0)
    @keybow.on_press(keys[12])
    def press_handler(key):
        consumer_control.send(ConsumerControlCode.PLAY_PAUSE)
        
    # CMUS Previous view = i
    keys[6].set_led(0,255,125)
    @keybow.on_press(keys[6])
    def press_handler(key):
        keyboard.send(Keycode.I)
    
    # CMUS Previous view = o
    keys[10].set_led(0,128,255)
    @keybow.on_press(keys[10])
    def press_handler(key):
        keyboard.send(Keycode.O)
        
    # CMUS something = e
    keys[7].set_led(0,255,50)
    @keybow.on_press(keys[7])
    def press_handler(key):
        keyboard.send(Keycode.E)


    # CMUS Volume Down = -
    keys[13].set_led(0,128,255)
    @keybow.on_press(keys[13])
    def press_handler(key):
        keyboard.send(Keycode.KEYPAD_MINUS)

    # CMUS Volume Up = +
    keys[14].set_led(128,0,255)
    @keybow.on_press(keys[14])
    def press_handler(key):
        keyboard.send(Keycode.KEYPAD_PLUS)

    # Screen on F1
    keys[11].set_led(128,128,255)
    @keybow.on_press(keys[11])
    def press_handler(key):
        keyboard.send(Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, Keycode.GUI, 
                      Keycode.F1)
        
    # Screen off F2
    keys[15].set_led(128,128,220)
    @keybow.on_press(keys[15])
    def press_handler(key):
        keyboard.send(Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, Keycode.GUI,
                      Keycode.F2)


    keys[2].set_led(*red_bright)
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


