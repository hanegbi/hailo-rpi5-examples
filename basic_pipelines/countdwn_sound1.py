import time
import pygame

def countdown_and_play_sound(seconds, sound_file):
    """Counts down and plays a loud sound."""
    print(f"Counting down: {seconds} seconds")
    for i in range(seconds, 0, -1):
        print(i)
        time.sleep(1)
    print("Playing sound!")

# Initialize the mixer module in pygame
    pygame.mixer.init()
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()
    
    # Wait for the sound to finish playing
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)


   
# Usage
SPEAKER_NAME = "Your_Speaker_Name"
SOUND_FILE = "trumpet_sound.mp3"  # Replace with the path to your sound file

# Connect to the speaker
speaker_address = connect_to_bluetooth_speaker(SPEAKER_NAME)
if speaker_address:
    # Play sound after a countdown
    countdown_and_play_sound(10, SOUND_FILE)
    
         
