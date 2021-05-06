# A testing script so that  i didn't have to open all the terminals and type in the start commands 3 times
# First runs the server file, and puts the cmd window on the right side
# Then runs 2 client files and puts them on the upper left and lower left of the screen

import os
import keyboard
import time
os.system('start cmd /c py server.py')
time.sleep(0.3)
keyboard.press_and_release('windows+right')
time.sleep(0.3)
keyboard.press_and_release('esc')
time.sleep(0.3)
os.system('start cmd /c py client.py')
time.sleep(0.3)
keyboard.press_and_release('windows+left')
time.sleep(0.3)
keyboard.press_and_release('windows+up')
time.sleep(0.3)
os.system('start cmd /c py client.py')
time.sleep(0.3)
keyboard.press_and_release('windows+left')
time.sleep(0.3)
keyboard.press_and_release('windows+down')
