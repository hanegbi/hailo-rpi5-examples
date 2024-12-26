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
def run_gui(pipe):import gi
import subprocess
import os
import signal

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class MainGUI(Gtk.Window):
    def __init__(self):
        super().__init__(title="Sailted Fish Controller")
        self.set_default_size(600, 450)

        # Apply custom CSS for styling
        provider = Gtk.CssProvider()
        provider.load_from_data(b"""
            window {
                background-color: #1e1e2f;
            }
            label {
                font-size: 26px;
                font-weight: bold;
                color: #e0e0e0;
            }
            button {
                font-size: 18px;
                padding: 15px;
                color: #ffffff;
                background-color: #007acc;
                border-radius: 10px;
                border: none;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #005bb5;
            }
            .status {
                font-size: 20px;
                color: #d1d1d1;
                margin-top: 15px;
            }
        """)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Create a vertical box layout
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.box.set_margin_top(40)
        self.box.set_margin_bottom(40)
        self.box.set_margin_start(40)
        self.box.set_margin_end(40)
        self.add(self.box)

        # Add a header label
        self.label = Gtk.Label(label="Sailted Fish Controller <*)))><")
        self.label.set_xalign(0.5)
        self.box.pack_start(self.label, False, False, 20)

        # Add level selection buttons
        self.level_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.box.pack_start(self.level_buttons, False, False, 10)

        for level in ["easy", "medium", "hard"]:
            button = Gtk.Button(label=level.capitalize())
            button.connect("clicked", self.on_level_button_clicked, level)
            self.level_buttons.pack_start(button, True, True, 10)

        # Add the Stop button
        self.stop_button = Gtk.Button(label="Stop")
        self.stop_button.connect("clicked", self.on_stop_button_clicked)
        self.box.pack_start(self.stop_button, False, False, 10)

        # Add a status display area
        self.status_label = Gtk.Label(label="Status: Ready")
        self.status_label.set_xalign(0.5)
        self.status_label.get_style_context().add_class("status")
        self.box.pack_start(self.status_label, False, False, 20)

    def on_level_button_clicked(self, widget, level):
        """Callback for level selection buttons."""
        try:
            script_path = os.path.join(os.path.dirname(__file__), "sailted_fish.py")
            subprocess.Popen(["python3", script_path, "--level", level, "--input", "rpi"])
            self.status_label.set_text(f"Status: Game started with {level.capitalize()} level!")
        except Exception as e:
            self.status_label.set_text(f"Status: Error: {e}")

    def on_stop_button_clicked(self, widget):
        """Callback for the Stop button."""
        try:
            result = subprocess.run(["pgrep", "-f", "sailted_fish.py"], stdout=subprocess.PIPE, text=True)
            if result.stdout:
                for pid in result.stdout.split():
                    os.kill(int(pid), signal.SIGTERM)
                self.status_label.set_text("Status: Game stopped!")
            else:
                self.status_label.set_text("Status: No running game process found.")
        except Exception as e:
            self.status_label.set_text(f"Status: Error: {e}")

if __name__ == "__main__":
    win = MainGUI()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

    gui_process(pipe)
