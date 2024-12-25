import gi
import subprocess
import os
import signal

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf

class MainGUI(Gtk.Window):
    def __init__(self):
        super().__init__(title="Sailted Fish Controller")
        self.set_default_size(500, 400)

        # Apply custom CSS for styling
        provider = Gtk.CssProvider()
        provider.load_from_data(b"""
            label {
                font-size: 24px;
                font-weight: bold;
                color: #ffffff;
            }
            button {
                font-size: 18px;
                padding: 12px;
                color: #ffffff;
                background-color: #007acc;
                border-radius: 8px;
                border: 2px solid #005bb5;
            }
            button:hover {
                background-color: #005bb5;
            }
        """
        )
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Create a vertical box layout
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.box.set_margin_top(30)
        self.box.set_margin_bottom(30)
        self.box.set_margin_start(30)
        self.box.set_margin_end(30)
        self.add(self.box)

        # Set background image
        bg_image_path = os.path.join(os.path.dirname(__file__), "_04eb49c6-68da-487e-a862-303013e25f82.jpeg")
        bg_pixbuf = GdkPixbuf.Pixbuf.new_from_file(bg_image_path)
        bg_image = Gtk.Image.new_from_pixbuf(bg_pixbuf)
        self.box.pack_start(bg_image, True, True, 0)

        # Add a header label
        self.label = Gtk.Label(label="Welcome to Sailted Fish Controller!")
        self.label.set_xalign(0.5)
        self.box.pack_start(self.label, False, False, 20)

        # Add the Start button
        self.start_button = Gtk.Button(label="Start Game")
        self.start_button.connect("clicked", self.on_start_button_clicked)
        self.box.pack_start(self.start_button, False, False, 10)

        # Add the Stop button
        self.stop_button = Gtk.Button(label="Stop Game")
        self.stop_button.connect("clicked", self.on_stop_button_clicked)
        self.box.pack_start(self.stop_button, False, False, 10)

        # Add a status display area
        self.status_label = Gtk.Label(label="Status: Ready")
        self.status_label.set_xalign(0.5)
        self.status_label.get_style_context().add_class("status")
        self.box.pack_start(self.status_label, False, False, 20)

    def on_start_button_clicked(self, widget):
        """Callback for the Start button."""
        try:
            script_path = os.path.join(os.path.dirname(__file__), "sailted_fish.py")
            subprocess.Popen(["python3", script_path, "--input", "rpi"])
            self.status_label.set_text("Status: Game started!")
        except Exception as e:
            self.status_label.set_text(f"Status: Error: {e}")

    def on_stop_button_clicked(self, widget):
        """Callback for the Stop button."""
        try:
            result = subprocess.run(["pgrep", "-f", "Hailo Pose"], stdout=subprocess.PIPE, text=True)
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
