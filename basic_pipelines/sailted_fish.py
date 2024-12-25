# Globals for Game Logic
game_state = "Green Light"  # Initial state of the game
frame_history = {}  # Dictionary to store pose keypoints for movement detection
moved_players = set()  # Set to store players who moved during "Red Light"
all_players = set()  # Set to store all detected players
winner_declared = False  # Flag to indicate if a winner has been declared

# -----------------------------------------------------------------------------------------------
# User-defined callback function
# -----------------------------------------------------------------------------------------------
def app_callback(pad, info, user_data):
    global game_state, frame_history, moved_players, threshold, all_players, winner_declared

    if winner_declared:
        return Gst.PadProbeReturn.OK  # Stop processing once a winner is declared

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
                if game_state == "Red Light" and len(frame_history[person_id]) > 1:
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
# Game Loop for Red Light, Green Light
# -----------------------------------------------------------------------------------------------
def game_loop():
    global game_state, moved_players, all_players, winner_declared

    while not winner_declared:
        # Green Light phase
        game_state = "Green Light"
        print("Green Light! Players can move.")
        time.sleep(10)  # Duration for Green Light

        # Red Light phase
        game_state = "Red Light"
        print("Red Light! Players must stop.")
        time.sleep(30)  # Duration for Red Light

        # Check for a winner at the end of "Red Light"
        if len(all_players) > 1:
            non_moved_players = all_players - moved_players
            if len(non_moved_players) == 1:
                winner = non_moved_players.pop()  # Identify the single winner
                print(f"\033[42mPlayer {winner} is the winner!\033[0m")  # Green background
                winner_declared = True
                break
            elif len(non_moved_players) > 1:
                print("Multiple players didn't move. Continuing...")
            else:
                print("No winner. All players moved during Red Light!")

        # Reset for the next round
        moved_players.clear()
        all_players.clear()

    print("Game over. A winner has been declared.")

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

    # Print the input source
    print(f"Input source: {args.input}")

    # Create an instance of the user app callback class
    user_data = user_app_callback_class()

    # Start the game loop in a separate thread
    game_thread = threading.Thread(target=game_loop, daemon=True)
    game_thread.start()

    # Run the GStreamer application
    app = GStreamerPoseEstimationApp(app_callback, user_data)
    app.run()
