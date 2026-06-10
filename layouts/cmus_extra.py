from pmk import PMK
from pmk.platform.keybow2040 import Keybow2040 as Hardware
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import usb_hid
import layouts.cmus as cmus
import layouts.key_tools as tools


keyboard = Keyboard(usb_hid.devices)


def setup(this_keybow):
    #mouse = Mouse(usb_hid.devices)
    global keybow
    keybow = this_keybow
    keybow.led_sleep_Time = 30
    keybow.set_all(0, 0, 0)

    keys=keybow.keys
    tools.resetKeys(keybow)

    keys[0].set_led(255,255,0)
    keys[12].set_led(255,255,0)
    keys[15].set_led(255,255,0)

# Audio Bluetooth
    keys[7].set_led(255,255,128)
    @keybow.on_press(keys[7])
    def press_handler(key):
        keyboard.send(Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, Keycode.GUI,
                      Keycode.F3)

# Audio 3.5mm
    keys[11].set_led(255,220,128)
    @keybow.on_press(keys[11])
    def press_handler(key):
        keyboard.send(Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, Keycode.GUI,
                      Keycode.F4)

# Quit CMUS
    keys[6].set_led(128,220,128)
    @keybow.on_press(keys[6])
    def press_handler(key):
        keyboard.send(Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, Keycode.GUI,
                      Keycode.F5)

# Start CMUS
    keys[10].set_led(220,128,128)
    @keybow.on_press(keys[10])
    def press_handler(key):
        keyboard.send(Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, Keycode.GUI,
                      Keycode.F6)

# Reconfiure
    keys[7].set_led(0,175,200)
    @keybow.on_press(keys[7])
    def press_handler(key):
        keyboard.send(Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, Keycode.GUI,
                      Keycode.F7)
        
        
# Back to main
    keys[2].set_led(255, 0, 0)
    @keybow.on_press(keys[2])
    def press_handler(key):
        cmus.setup(keybow)

# F8 - F13
    @keybow.on_press(keys[1])
    def press_handler(key):
        keyboard.send(Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, Keycode.GUI,
                      Keycode.F8)
    
    @keybow.on_press(keys[5])
    def press_handler(key):
        keyboard.send(Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, Keycode.GUI,
                      Keycode.F9)
        
    @keybow.on_press(keys[9])
    def press_handler(key):
        keyboard.send(Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, Keycode.GUI,
                      Keycode.F10)
        
    @keybow.on_press(keys[13])
    def press_handler(key):
        keyboard.send(Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, Keycode.GUI,
                      Keycode.F11)

    @keybow.on_press(keys[4])
    def press_handler(key):
        keyboard.send(Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, Keycode.GUI,
                     Keycode.ONE)

    @keybow.on_press(keys[8])
    def press_handler(key):
        keyboard.send(Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, Keycode.GUI,
                     Keycode.TWO)



def update():
    keys=keybow.keys
    if keys[0].pressed and keys[12].pressed and keys[15].pressed:
        keyboard.send(Keycode.CONTROL, Keycode.ALT, Keycode.SHIFT, Keycode.GUI,
                      Keycode.F12)


#If not an import, run on your own. Be free!
if __name__ == '__main__':

    keybow = PMK(Hardware())
    setup(keybow)

    while True:
        keybow.update()
        update()

