
#  pip install pynput

from pynput.keyboard import Controller

keyboard = Controller()

# Function to press volume-up or volume-down keys
def change_volume_up():
    keyboard.press('volume up')
    keyboard.release('volume up')

def change_volume_down():
    keyboard.press('volume down')
    keyboard.release('volume down')

# Example: Increase volume by one step
change_volume_up()

