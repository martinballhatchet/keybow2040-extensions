from pmk import PMK
from pmk.platform.keybow2040 import Keybow2040 as Hardware

# Here we import the layouts we want to use.
import layouts.cmus as cmus
import layouts.mousekeys as mousekeys
import layouts.rainbow_arc as rainbow_arc

keybow = PMK(Hardware())
keys = keybow.keys


layers = [cmus, mousekeys, rainbow_arc]

layer_index = 0
layers[layer_index].setup(keybow)


#switch layout! Using "top-left" key for this.
@keybow.on_press(keys[3])
def press_handler(key):
    
    global layer_index
    
    layer_index += 1
    
    if layer_index >= len(layers):
        layer_index = 0
    
    layers[layer_index].setup(keybow)
    

while True:
    
    keybow.update()
    layers[layer_index].update()
