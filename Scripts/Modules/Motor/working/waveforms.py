from Scripts.Modules.Motor.WF_SDK import device, wavegen
import time

device_data = device.open()
wavegen.generate(
    device_data, 
    channel=0, 
    function=wavegen.function.pulse,
    frequency=333, 
    amplitude=5.0, 
    offset=0.0, 
    symmetry=84, 
    run_time=10.0, 
    wait=1.0, 
    repeat=1)

time.sleep(5)

wavegen.close(device_data)
device.close(device_data)