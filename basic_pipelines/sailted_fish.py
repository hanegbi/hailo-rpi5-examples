import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import os
import numpy as np
import cv2
import hailo
import time
import threading

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
colour_frame_red = False  # Flag to indicate if the frame should be coloured red
movement_threshold = 1500  # Threshold for significant movement

# -----------------------------------------------------------------------------------------------
# Game Loop for Red Light, Green Light
# -----------------------------------------------------------------------------------------------
def game_loop():
    global game_state, colour_frame_red
    while True:
        # Green Light phase
        game_state = "Green Light"
        colour_frame_red = False
        print("Green Light! Players can move.")
        time.sleep(10)  # Duration for Green Light (10 seconds)

        # Red Light phase
        game_state = "Red Light"
        print("Red Light! Players must stop.")
        time.sleep(30)  # Duration for Red Light (30 seconds)

# -----------------------------------------------------------------------------------------------
# User-defined callback function
# -----------------------------------------------------------------------------------------------
def app_callback(pad, info, user_data):
    global game_state, frame_history, colour_frame_red

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

    # Reset red frame flag for this cycle
    colour_frame_red = False

    # Process detections
    for detection in detections:
        if detection.get_label() == "person":
            # Get bounding box and landmarks
            bbox = detection.get_bbox()
            landmarks = detection.get_objects_typed(hailo.HAILO_LANDMARKS)
            if landmarks:
                person_id = hash(detection)  # Unique ID for each detection
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
                if game_state == "Red Light" and len(frame_history[person_id]) > 1:
                    prev_coords = frame_history[person_id][-2]
                    curr_coords = frame_history[person_id][-1]

                    # Calculate movement by summing the distance between keypoints
                    movement = sum(np.linalg.norm(np.array(curr) - np.array(prev))
                                   for prev, curr in zip(prev_coords, curr_coords))
                    if movement > movement_threshold:  # Threshold for significant movement
                        print(f"Player {person_id} moved during Red Light!")
                        colour_frame_red = True

    # Modify frame colour based on game state and movement
    if frame is not None:
        if colour_frame_red:
            # Colour the frame red
            frame[:, :, 0] = 0  # Zero out blue channel
            frame[:, :, 1] = 0  # Zero out green channel
        else:
            # Colour the frame green
            frame[:, :, 2] = 0  # Zero out red channel
            frame[:, :, 0] = 0  # Zero out blue channel

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
    # Create an instance of the user app callback class
    user_data = user_app_callback_class()

    # Start the game loop in a separate thread
    game_thread = threading.Thread(target=game_loop, daemon=True)
    game_thread.start()

    # Run the GStreamer application
    app = GStreamerPoseEstimationApp(app_callback, user_data)
    app.run()
