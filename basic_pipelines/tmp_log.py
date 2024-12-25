~/workspace/hailo-rpi5-examples $ python basic_pipelines/connect_blupy_t1.py 
Searching for nearby Bluetooth devices...
Traceback (most recent call last):
  File "/home/hailo/workspace/hailo-rpi5-examples/basic_pipelines/connect_blupy_t1.py", line 35, in <module>
    devices = discover_devices()
              ^^^^^^^^^^^^^^^^^^
  File "/home/hailo/workspace/hailo-rpi5-examples/basic_pipelines/connect_blupy_t1.py", line 11, in discover_devices
    devices = scanner.scan(10.0)  # Scan for 10 seconds
              ^^^^^^^^^^^^^^^^^^
  File "/home/hailo/workspace/hailo-rpi5-examples/venv_hailo_rpi5_examples/lib/python3.11/site-packages/bluepy/btle.py", line 852, in scan
    self.start(passive=passive)
  File "/home/hailo/workspace/hailo-rpi5-examples/venv_hailo_rpi5_examples/lib/python3.11/site-packages/bluepy/btle.py", line 790, in start
    self._mgmtCmd("le on")
  File "/home/hailo/workspace/hailo-rpi5-examples/venv_hailo_rpi5_examples/lib/python3.11/site-packages/bluepy/btle.py", line 312, in _mgmtCmd
    raise BTLEManagementError("Failed to execute management command '%s'" % (cmd), rsp)
bluepy.btle.BTLEManagementError: Failed to execute management command 'le on' (code: 20, error: Permission Denied)
