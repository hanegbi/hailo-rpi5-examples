import gi
import subprocess
import os
import signal

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class MainGUI(Gtk.Window):
    def __init__(self):
        super().__init__(title="Sailted Fish Controller")
        self.set_default_size(400, 300)

        # Set a background colour
        provider = Gtk.CssProvider()
        provider.load_from_data(b"""
            window {
                background-color: #f5f5f5;
            }
            label {
                font-size: 18px;
                font-weight: bold;
            }
            button {
                font-size: 16px;
                padding: 10px;
            }
        """.encode())
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Create a vertical box layout
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.box.set_margin_top(20)
        self.box.set_margin_bottom(20)
        self.box.set_margin_start(20)
        self.box.set_margin_end(20)
        self.add(self.box)

        # Add a label to the GUI
        self.label = Gtk.Label(label="Welcome to the Sailted Fish Controller! 🐟")
        self.label.set_xalign(0.5)
        self.box.pack_start(self.label, False, False, 10)

        # Add the Start button
        self.start_button = Gtk.Button(label="Start Game")
        self.start_button.connect("clicked", self.on_start_button_clicked)
        self.box.pack_start(self.start_button, False, False, 10)

        # Add the Stop button
        self.stop_button = Gtk.Button(label="Stop Game")
        self.stop_button.connect("clicked", self.on_stop_button_clicked)
        self.box.pack_start(self.stop_button, False, False, 10)

    def on_start_button_clicked(self, widget):
        """Callback for the Start button."""
        try:
            # Launch the secondary script
            script_path = os.path.join(os.path.dirname(__file__), "sailted_fish.py")
            subprocess.Popen(["python3", script_path, "--input", "rpi"])
            self.label.set_text("Game started! 🟢")
        except Exception as e:
            self.label.set_text(f"Error: {e}")

    def on_stop_button_clicked(self, widget):
        """Callback for the Stop button."""
        try:
            # Find and terminate processes containing "Hailo Pose"
            result = subprocess.run(["pgrep", "-f", "Hailo Pose"], stdout=subprocess.PIPE, text=True)
            if result.stdout:
                for pid in result.stdout.split():
                    os.kill(int(pid), signal.SIGTERM)
                self.label.set_text("Game stopped! ⛔")
            else:
                self.label.set_text("No Hailo Pose process found.")
        except Exception as e:
            self.label.set_text(f"Error: {e}")

if __name__ == "__main__":
    # Create and run the GUI
    win = MainGUI()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
