import gi
import multiprocessing
import time
import argparse
import sys
from hailo_apps_infra.hailo_rpi_common import (
    get_caps_from_pad,
    get_numpy_from_buffer,
    app_callback_class,
)
from hailo_apps_infra.pose_estimation_pipeline import GStreamerPoseEstimationApp
from run_gui import run_gui  

gi.require_version('Gst', '1.0')
from gi.repository import Gst

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
# Game Loop for Red Light, Green Light
# -----------------------------------------------------------------------------------------------
def game_loop(pipe):
    global game_state, moved_players, all_players

    while True:
        # Green Light phase (start a new game)
        game_state = "Green Light"
        print("\033[30;42mGreen Light! Players can move. Starting a new game soon.\033[0m")
        pipe.send("Green Light")  # Send game state to the GUI
        moved_players.clear()  # Reset moved players for the new round
        all_players.clear()
        time.sleep(5)  # Duration for Green Light

        # Red Light phase
        game_state = "Red Light"
        print("\033[30;45m!!! 1 !!!\033[0m")
        time.sleep(1)
        print("\033[30;45m!!! 2 !!!\033[0m")
        time.sleep(1)
        print("\033[30;45m!!! 3 !!!\033[0m")
        time.sleep(1)
        print("\033[30;45mDON'T MOVE!\033[0m")
        pipe.send("Red Light")  # Send game state to the GUI
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

        print("\033[30;47mPausing for 10 seconds before the next round...\033[0m")
        time.sleep(5)
        print("\033[30;47mGet ready! starting in 5 seconds...\033[0m")
        time.sleep(5)

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

    # Create a multiprocessing pipe for GUI communication
    parent_pipe, child_pipe = multiprocessing.Pipe()

    # Start the GUI in a separate process
    gui_process = multiprocessing.Process(target=run_gui, args=(child_pipe,))
    gui_process.start()

    # Start the game loop in a separate thread
    game_thread = threading.Thread(target=game_loop, args=(parent_pipe,), daemon=True)
    game_thread.start()

    # Run the GStreamer application in the main thread
    app = GStreamerPoseEstimationApp(app_callback, user_data)

    try:
        app.run()
    except KeyboardInterrupt:
        print("Shutting down...")
        parent_pipe.send("QUIT")
        gui_process.join()
