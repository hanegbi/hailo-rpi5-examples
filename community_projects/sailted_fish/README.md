# Sailted Fish

## Overview

Sailted Fish 🐟 is a Red Light 🔴 Green Light 🟢 game that that uses advanced AI-driven pose estimation to track player movements. If a player moves during "Red Light," they are flagged as "Salted Fish" 🐟 and eliminated from the round. The last player who stays still through "Red Light" is the winner 🏆.

## Video

🎥 Watch the demo:

[Insert Demo URL Here]

## Versions

🛠️ Tested and verified on:

- Python 3.11
- GTK 3.0
- GStreamer 1.0
- Raspberry Pi 5

## Setup Instructions

📦 To set up Sailted Fish, follow these steps:

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the program:
   ```bash
   python sailted_fish.py --input rpi --level easy
   ```

## Usage

🚀 You can customise the gameplay difficulty levels:
- `easy`
- `medium`
- `hard`

### Example Commands:

Run the game with a video file and medium difficulty:
```bash
python sailted_fish.py --input rpi --level medium
```


## License

📜 Sailted Fish is licensed under the MIT License. See the LICENSE file for full details.