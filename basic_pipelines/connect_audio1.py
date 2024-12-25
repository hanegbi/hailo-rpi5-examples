
#  pip install pybluez


import bluetooth

# Function to search for available Bluetooth devices
def discover_devices():
    print("Searching for Bluetooth devices...")
    nearby_devices = bluetooth.discover_devices(lookup_names=True, lookup_uuids=True)
    print("Found devices:")
    for addr, name in nearby_devices:
        print(f"  {name} - {addr}")
    return nearby_devices

# Function to connect to the Bluetooth speaker
def connect_to_device(device_address):
    port = 1  # Bluetooth port for A2DP profile (Audio)
    try:
        # Create Bluetooth socket and connect to the speaker
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((device_address, port))
        print(f"Successfully connected to {device_address}")
        return sock
    except bluetooth.BluetoothError as e:
        print(f"Failed to connect: {e}")
        return None

# Discover Bluetooth devices
devices = discover_devices()

# Choose the Bluetooth address of your speaker
if devices:
    device_address = devices[0][0]  # Here, I'm selecting the first device
    sock = connect_to_device(device_address)

    if sock:
        # Now you can stream audio or send data via this socket
        # Example: Sending a basic command to the speaker (depends on your device)
        sock.send("Hello Bluetooth Speaker")
        sock.close()
else:
    print("No devices found.")













