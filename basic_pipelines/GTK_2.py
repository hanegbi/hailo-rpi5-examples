import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, GLib, Gtk
import os
import numpy as np
import cv2
import hailo
import time
import threading
import argparse  # For parsing command-line arguments
import sys
from hailo_apps_infra.hailo_rpi_common import (
    get_caps_from_pad,
    get_numpy_from_buffer,
    app_callback_class,
)
from hailo_apps_infra.pose_estimation_pipeline import GStreamerPoseEstimationApp

# -----------------------------------------------------------------------------------------------
# User-defined class to be used in the callback function
# -----------------------------------------------------------------------------------------------
class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()

# -----------------------------------------------------------------------------------------------
# Globals for Game Logic
# -----------------------------------------------------------------------------------------------
game_state = "Green Light"  # Initial state of the game
frame_history = {}  # Dictionary to store pose keypoints for movement detection
moved_players = set()  # Set to store players who moved during "Red Light"
all_players = set()  # Set to store all detected players

# -----------------------------------------------------------------------------------------------
# Levels Definition
# -----------------------------------------------------------------------------------------------
level_thresholds = {
    "easy": 1500,
    "medium": 1000,
    "hard": 500,
}

def set_level(level):
    """Set the threshold based on the chosen level."""
    global threshold
    if level in level_thresholds:
        threshold = level_thresholds[level]
        print(f"Game level set to {level.capitalize()}. Movement threshold: {threshold}")
    else:
        print(f"Invalid level: {level}. Defaulting to 'easy'.")
        threshold = level_thresholds["easy"]

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


    # Function to run the GUI
def run_gui():
    gui.connect("destroy", Gtk.main_quit)
    gui.show_all()
    Gtk.main()

# -----------------------------------------------------------------------------------------------
# Game Loop for Red Light, Green Light
# -----------------------------------------------------------------------------------------------
def game_loop(gui):
    global game_state, moved_players, all_players
    while True:
        # Green Light phase
        game_state = "Green Light"
        GLib.idle_add(gui.update_game_state, "Green Light")
        print("Green Light! Players can move.")
        moved_players.clear() # Reset moved players for the new round
        all_players.clear()
        time.sleep(10)  # Duration for Green Light

        # Red Light phase
        game_state = "Red Light"
        GLib.idle_add(gui.update_game_state, "Red Light")
        print("\033[30;45mRed Light! Players must stop!!\033[0m")
        time.sleep(20)  # Duration for Red Light

        # Determine winner during Red Light
        if len(all_players) > 1:
            non_moved_players = all_players - moved_players
            if len(non_moved_players) == 1:
                winner = non_moved_players.pop()
                print(f"\033[100mPlayer {winner} is the winner!\033[0m")
            elif len(non_moved_players) > 1:
                print("\033[30;47mMultiple players didn't move. No winner this round.\033[0m")
            else:
                print("\033[30;47mNo winner. All players moved during Red Light!\033[0m")
#        elif len(all_players) == 1:
#            winner = list(all_players)[0]
#            print(f"\033[42mPlayer {winner} is the winner!\033[0m")  # Green background

        print("\033[30;47mPausing for 10 seconds before the next round...\033[0m")
        time.sleep(5)
        print("\033[30;47mGet ready! staring in 5 seconds...\033[0m")
        time.sleep(5)

# -----------------------------------------------------------------------------------------------
# User-defined callback function
# -----------------------------------------------------------------------------------------------
def app_callback(pad, info, user_data):
    global game_state, frame_history, moved_players, threshold, all_players

    # Get the GstBuffer from the probe info
    buffer = info.get_buffer()
    if buffer is None:
        return Gst.PadProbeReturn.OK

    # Get video frame
    format, width, height = get_caps_from_pad(pad)
    frame = None
    if user_data.use_frame and format and width and height:
        frame = get_numpy_from_buffer(buffer, format, width, height)

    # Get the detections from the buffer
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    # Keypoints for COCO body parts
    keypoints = get_keypoints()

    # Process detections
    for detection in detections:
        if detection.get_label() == "person":
            track_id = 0
            track = detection.get_objects_typed(hailo.HAILO_UNIQUE_ID)
            if len(track) == 1:
                track_id = track[0].get_id()

            person_id = track_id  # Unique ID for each detection
            all_players.add(person_id)  # Add to the set of all players

            # Get bounding box and landmarks
            bbox = detection.get_bbox()
            landmarks = detection.get_objects_typed(hailo.HAILO_LANDMARKS)
            if landmarks:
                points = landmarks[0].get_points()
                if person_id not in frame_history:
                    frame_history[person_id] = []

                # Extract keypoint coordinates
                keypoint_coords = [
                    (int((point.x() * bbox.width() + bbox.xmin()) * width),
                     int((point.y() * bbox.height() + bbox.ymin()) * height))
                    for point in points
                ]

                frame_history[person_id].append(keypoint_coords)

                # Detect movement during "Red Light"
                if game_state == "Red Light" and person_id not in moved_players:
                    if len(frame_history[person_id]) > 1:
                        prev_coords = frame_history[person_id][-2]
                        curr_coords = frame_history[person_id][-1]

                        # Calculate movement by summing the distance between keypoints
                        movement = sum(np.linalg.norm(np.array(curr) - np.array(prev))
                                       for prev, curr in zip(prev_coords, curr_coords))
                        if movement > threshold:
                            moved_players.add(person_id)
                            print(f"\033[41mPlayer {person_id} moved during Red Light!\033[0m")  # Red background

    # Draw keypoints on the frame (optional visualisation)
    if user_data.use_frame and frame is not None:
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        for person_id, keypoints in frame_history.items():
            if keypoints:
                for point in keypoints[-1]:  # Draw the most recent keypoints
                    cv2.circle(frame, point, 5, (0, 255, 0), -1)
        user_data.set_frame(frame)

    return Gst.PadProbeReturn.OK

# -----------------------------------------------------------------------------------------------
# Keypoints Mapping
# -----------------------------------------------------------------------------------------------
def get_keypoints():
    """Get the COCO keypoints and their left/right flip correspondence map."""
    return {
        'nose': 0,
        'left_eye': 1,
        'right_eye': 2,
        'left_ear': 3,
        'right_ear': 4,
        'left_shoulder': 5,
        'right_shoulder': 6,
        'left_elbow': 7,
        'right_elbow': 8,
        'left_wrist': 9,
        'right_wrist': 10,
        'left_hip': 11,
        'right_hip': 12,
        'left_knee': 13,
        'right_knee': 14,
        'left_ankle': 15,
        'right_ankle': 16,
    }

# -----------------------------------------------------------------------------------------------
# Main Function
# -----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Red Light Green Light Game")
    parser.add_argument(
        "--level",
        type=str,
        choices=["easy", "medium", "hard"],
        default="easy",
        help="Set the game difficulty level (default: easy)",
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Specify the input source (e.g., rpi or a video file path)",
    )
    args = parser.parse_args()

    # Set the level based on the argument
    set_level(args.level)
    if "--level" in sys.argv:
        index = sys.argv.index("--level")
        del sys.argv[index:index + 2]  # Remove both --level and its value

    # Print the input source
    print(f"Input source: {args.input}")

    # Create an instance of the user app callback class
    user_data = user_app_callback_class()

    # Create the GUI window
    gui = RedLightGreenLightGUI()


    # Start the GUI in a separate thread
    gui_thread = threading.Thread(target=run_gui, daemon=True)
    gui_thread.start()

    # Start the game loop in a separate thread
    game_thread = threading.Thread(target=game_loop, args=(gui,), daemon=True)
    game_thread.start()

    # Run the GStreamer application in the main thread
    app = GStreamerPoseEstimationApp(app_callback, user_data)
    app.run()



