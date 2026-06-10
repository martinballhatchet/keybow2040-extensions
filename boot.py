import math
from pmk import PMK, number_to_xy, hsv_to_rgb
from pmk.platform.keybow2040 import Keybow2040 as Hardware # for Keybow 2040
import usb_cdc
import time
import storage

usb_cdc.enable(console=True, data=True)
keybow = PMK(Hardware())


def rainbow():

    # Set up Keybow
    keys = keybow.keys

    # Increment step to shift animation across keys.
    step = 0

    step += 1

    for i in range(16):
        # Convert the key number to an x/y coordinate to calculate the hue
        # in a matrix style-y.
        x, y = number_to_xy(i)

        # Calculate the hue.
        hue = (x + y + (step / 20)) / 8
        hue = hue - int(hue)
        hue = hue - math.floor(hue)

        # Convert the hue to RGB values.
        r, g, b = hsv_to_rgb(hue, 1, 1)

        # Display it on the key!
        keys[i].set_led(r, g, b)



def set_all_keys(colour):
    keybow.set_all(*colour)


def check_keys_before_boot():

    rainbow()

    button_pressed = False

    start_time = time.monotonic()

    # Wait for up to 1 second to check if the button is pressed
    while time.monotonic() - start_time < 1:

        for key in keybow.keys:
            if key.pressed:
                button_pressed = True
                break  # Exit the loop early if any button is pressed

        time.sleep(0.1)  # Small delay to reduce CPU usage

        if button_pressed:
            break # Exit early

        keybow.update()

    # If the button was not pressed during the 1-second window, disable the USB drive
    if not button_pressed:
        print("# - Button not pressed, USB drive disabled.")
        set_all_keys((255, 0, 0))

        storage.disable_usb_drive()
    else:
        set_all_keys((0, 255, 0))
        print("# - Button pressed, mounting USB drive next!")

print("Starting boot on MarvKeyBow...")

#check_keys_before_boot()

try:
    print("Checking keys...")
    check_keys_before_boot()
    print("Check keys was successful!!")
except Exception:
    print("Error checking keys. I don't know what to tell you")


print("Done booting")
