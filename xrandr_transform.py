#!/usr/bin/env python
from Xlib import display, X
import Xlib
import subprocess
import re

# get root window (if 2 monitors, spans both of them)
root = display.Display().screen().root
# setup listener to get mouse presses
root.grab_button(X.AnyButton, X.AnyModifier, True, X.ButtonPressMask , X.GrabModeAsync, X.GrabModeAsync,0, 0)

## find screens
# parse lines from xrandr like
#   LVDS-1 connected primary 1366x768+1920+0 ...
#   HDMI-1 connected 1280x720...
# prompt for which to use
# TODO: use Xlib and first button click to get monitor instead of this
outputs = []
for l in subprocess.check_output(["xrandr"]).decode('ascii').split("\n"):
    m = re.search('^([0-9A-Z-]+) connected.* (\d+)x(\d+)',l)
    if m:
        outputs.append({'w':int(m.group(2)), 'h': int(m.group(3)), 'm': m.group(1)})

i=0
if(len(outputs)>1):
    for i,v in enumerate(outputs): print("%d: %s" % (i,v))
    i=int(input('which input number (must be set as left display!)? '))
output=outputs[i]

## get x and y
print("""
1.click top left corner of what is visible
2.click bottom right corner of what is visible
""")
i = 0
pos=[]
while i < 2:
    event = root.display.next_event()
    pos.append( {'x':event.root_x,'y': event.root_y} )
    print(pos[i])
    i+=1

## calculate transfrom
def calc_trans(expect, border_low, border_high):
    actual = border_high - border_low 
    ratio = expect/actual
    adjust = -border_low * ratio
    return({'r':ratio,'t':adjust})

x = calc_trans(output['w'],pos[0]['x'],pos[1]['x'])
y = calc_trans(output['h'],pos[0]['y'],pos[1]['y'])
print(x)
print(y)
transform = "--transform %.02f,0,%d,0,%.02f,%d,0,0,1" % (x['r'], x['t'], y['r'],y['t'])

print(("xrandr --output %(m)s" +
      " --mode %(w)dx%(h)d " +
      transform + 
      " --panning %(w)dx%(h)d"+
      " --pos 0x0" ) % output )

