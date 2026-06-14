from pmk import PMK, hsv_to_rgb
from pmk.platform.keybow2040 import Keybow2040 as Hardware

#TODO - set a sleep time

loopMax = 200
bandGap = 45 / 360 #This means that the colours are 45 degrees apart
loopCount = 0

keys_inner = [0]
keys_band1 = [4, 1, 5]
keys_band2 = [8, 2, 9, 6, 10]
keys_band3 = [12, 3, 13, 7, 14, 11, 15]

def setBand(key_list, colour):
    for key in key_list:
         keybow.keys[key].set_led(*colour)

def setup(this_keybow):

    global keybow
    keybow = this_keybow
    #keybow.led_sleep_enabled = True
    #keybow.led_sleep_time = 1

def setColours(hue, saturation, value):
    
    setBand_hsv(keys_inner, constrainValue(hue), saturation, value)
    setBand_hsv(keys_band1, constrainValue(hue + bandGap), saturation, value)
    setBand_hsv(keys_band2, constrainValue(hue + 2 * bandGap), saturation, value)
    setBand_hsv(keys_band3, constrainValue(hue + 3 * bandGap), saturation, value)


# Divide by loopMax
def normaliseValue(value):
    value = value/loopMax
    return value

# Always between 0 and 1
def constrainValue(value):
    if value < -1:
        raise Exception("Somehow value is less than -1")
    if value > 2:
        raise Exception("somehow value is greater than 2")
    if value > 1:
        value -= 1
    if value < 0:
        value += 1
    return value
                
def setBand_hsv(band, hue, saturation, value):
    r, g, b = hsv_to_rgb(hue, saturation, value)
    setBand(band, (r, g, b))

def update():

    keys = keybow.keys
    
    global loopCount
    
    loopCount += 1
    if loopCount >= loopMax:
        loopCount = 0
        
    saturation = 1
    value = 1
    hue = 1 - normaliseValue(loopCount) #So we go forwards through the rainbow

    setColours(hue, saturation, value)
                    
    for key in keybow.get_pressed():
        print (keys[key].rgb)
            
#If not an import, run on your own. Be free!
if __name__ == '__main__':

    keybow = PMK(Hardware())
    setup(keybow)

    while True:
        keybow.update()
        update()

