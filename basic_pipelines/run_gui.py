import gi
import multiprocessing
import os
import signal
import time
import json

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

# -----------------------------------------------------------------------------------------------
# GTK Game GUI Class
# -----------------------------------------------------------------------------------------------
class RedLightGreenLightGUI(Gtk.Window):
    def __init__(self):
        super().__init__(title="Red Light, Green Light")
        self.set_default_size(800, 600)

        # Initial Game State
        self.game_state = "Green Light"

        # Create a vertical box layout
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(self.box)

        # Add a label to display the game state
        self.state_label = Gtk.Label(label="Game State: Green Light")
        self.state_label.set_margin_top(10)
        self.box.pack_start(self.state_label, False, False, 0)

        # Add an image widget to display the doll
        self.doll_image = Gtk.Image.new_from_file("doll_away.png")
        self.box.pack_start(self.doll_image, True, True, 0)

    def update_game_state(self, state):
        """Update the game state label and doll image."""
        self.game_state = state
        self.state_label.set_text(f"Game State: {state}")
        if state == "Green Light":
            self.doll_image.set_from_file("doll_away.png")
        elif state == "Red Light":
            self.doll_image.set_from_file("doll_looking.png")

# -----------------------------------------------------------------------------------------------
# Function to run the GUI
# -----------------------------------------------------------------------------------------------
def gui_process(pipe):
    gui = RedLightGreenLightGUI()

    def listen_for_updates():
        while True:
            if pipe.poll():
                message = pipe.recv()
                if isinstance(message, str):
                    GLib.idle_add(gui.update_game_state, message)
                elif message == "QUIT":
                    Gtk.main_quit()
                    break

    listener_thread = multiprocessing.Process(target=listen_for_updates)
    listener_thread.start()

    gui.connect("destroy", Gtk.main_quit)
    gui.show_all()
    Gtk.main()

# -----------------------------------------------------------------------------------------------
# Main Function to Spawn GUI
# -----------------------------------------------------------------------------------------------
def run_gui(pipe):
    gui_process(pipe)
