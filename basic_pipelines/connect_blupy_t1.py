
#  pip install bluepy


from bluepy.btle import Scanner, Peripheral

# Function to discover nearby Bluetooth devices
def discover_devices():
    print("Searching for nearby Bluetooth devices...")
    scanner = Scanner()
    devices = scanner.scan(10.0)  # Scan for 10 seconds
    found_devices = []
    
    for dev in devices:
        print(f"Device {dev.addr}, RSSI={dev.rssi} dB, Name={dev.getValueText(9)}")
        found_devices.append(dev)
    
    return found_devices

# Function to connect to a Bluetooth device by its MAC address
def connect_to_device(device_address):
    try:
        # Connect to the device using its MAC address
        print(f"Connecting to {device_address}...")
        peripheral = Peripheral(device_address)
        print(f"Successfully connected to {device_address}")
        
        # You can now interact with the peripheral, e.g., read/write characteristics.
        return peripheral
    except Exception as e:
        print(f"Failed to connect to {device_address}: {e}")
        return None

# Discover Bluetooth devices
devices = discover_devices()

# If devices are found, choose one to connect to
if devices:
    # Example: Pick the first device from the list
    device_address = devices[0].addr  # Get the MAC address of the first device
    peripheral = connect_to_device(device_address)

    if peripheral:
        # You can now interact with the device, such as reading or writing characteristics
        peripheral.disconnect()  # Disconnect after use
else:
    print("No Bluetooth devices found.")


