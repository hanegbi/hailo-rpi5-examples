import gi
import subprocess
import os
import signal

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class MainGUI(Gtk.Window):
    def __init__(self):
        super().__init__(title="Raspberry Pi Touch GUI")
        self.set_default_size(400, 200)

        # Create a vertical box layout
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(self.box)

        # Add a label to the GUI
        self.label = Gtk.Label(label="Welcome to the Raspberry Pi Hailo Kit!")
        self.box.pack_start(self.label, False, False, 10)

        # Add the Start button
        self.start_button = Gtk.Button(label="Start")
        self.start_button.connect("clicked", self.on_start_button_clicked)
        self.box.pack_start(self.start_button, False, False, 10)

        # Add the Stop button
        self.stop_button = Gtk.Button(label="Stop")
        self.stop_button.connect("clicked", self.on_stop_button_clicked)
        self.box.pack_start(self.stop_button, False, False, 10)

    def on_start_button_clicked(self, widget):
        """Callback for the Start button."""
        try:
            # Launch the secondary script
            script_path = os.path.join(os.path.dirname(__file__), "sailted_fish.py")
            subprocess.Popen(["python3", script_path, "--input", "rpi"])
            self.label.set_text("Game started!")
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
                self.label.set_text("Game stopped!")
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
