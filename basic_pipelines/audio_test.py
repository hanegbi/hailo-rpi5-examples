import asyncio
from bleak import BleakScanner

# Connect to the Device: Use the device address to establish a connection.

async def discover_devices():
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"Name: {device.name}, Address: {device.address}")

asyncio.run(discover_devices())

# Replace with your speaker's BLE address
device_address = "XX:XX:XX:XX:XX:XX"
asyncio.run(connect_to_device(device_address))

# Interact with Services and Characteristics: BLE devices provide services and characteristics for interaction. You can read or write data to them.

async def interact_with_device(address):
    async with BleakClient(address) as client:
        services = await client.get_services()
        print("Available services:")
        for service in services:
            print(service)

asyncio.run(interact_with_device(device_address))


