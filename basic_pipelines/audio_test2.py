import bluetooth

def connect_to_bluetooth_speaker(target_name):
    """Connects to a Bluetooth speaker by its name."""
    print("Scanning for devices...")
    devices = bluetooth.discover_devices(duration=5, lookup_names=True)

    target_address = None
    for addr, name in devices:
        print(f"Found: {name} ({addr})")
        if target_name == name:
            target_address = addr
            break

    if target_address is None:
        print(f"Could not find device named {target_name}")
        return None

    print(f"Connecting to {target_name} at {target_address}...")
    # Connection logic for audio happens via system or PulseAudio, so return address
    return target_address

    