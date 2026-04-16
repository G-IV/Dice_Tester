'''
The motor is a stepper motor with 180° range of motion.
We'll be controlling the stepper motor positioning using an old Digilent Analog Discovery 2 board as a signal generator.
Digilent published an SDK I can use to communicate with the board:
https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual
'''

# To use the SDK, we have to do a song and dance:
from ctypes import *
import sys

dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")

def get_devices() -> None:
    """
    Returns a list of connected AD2 devices.
    """
    version = create_string_buffer(32)
    cDev = c_int()
    myAD2 = c_int()
    name = create_string_buffer(64)
    no_name = create_string_buffer(64)

    dwf.FDwfGetVersion(version)
    print("\nDWF Version: "+str(version.value)+"\n")
    dwf.FDwfEnum(c_int(0), byref(cDev))
    print("Devices: "+str(cDev.value))

    dwf.FDwfDeviceOpen(c_int(-1), byref(myAD2))
    print("Handle: "+str(myAD2.value))

    dwf.FDwfEnumDeviceName(c_int(myAD2.value), name)
    print("Name: "+name.value.decode('utf-8'))

    dwf.FDwfEnumDeviceName(c_int(3), no_name)
    print("Name: "+no_name.value.decode('utf-8'))

    dwf.FDwfDeviceClose(myAD2)


get_devices()