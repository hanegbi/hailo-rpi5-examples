import subprocess

# Function to set system volume
def set_volume(volume_percentage):
    # Ensure the volume is between 0 and 100
    volume_percentage = max(0, min(100, volume_percentage))

    # Use amixer to set the volume
    subprocess.run(["amixer", "set", "Master", f"{volume_percentage}%"])

# Example: Set volume to 50%
set_volume(50)

