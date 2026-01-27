import ctypes
from sys import platform, path
from os import sep
import time

print("Running on platform: " + platform)
lib_path = sep + "Library" + sep + "Frameworks" + sep + "dwf.framework" + sep + "dwf"
print("Loading library from path: " + lib_path)
dwf = ctypes.cdll.LoadLibrary(lib_path)
constants_path = sep + "Applications" + sep + "WaveForms.app" + sep + "Contents" + sep + "Resources" + sep + "SDK" + sep + "samples" + sep + "py"

path.append(constants_path)
import dwfconstants as constants


RUN_MOTOR = True

POS_90 = .0025
POS_45 = .0020
POS_0 = .0015
POS_45N = .0010
POS_90N = .0005

FREQUENCY = 333

class data:
    handle = ctypes.c_int()
    name = ""

def open():
    device_handle = ctypes.c_int()
    dwf.FDwfDeviceOpen(ctypes.c_int(-1), ctypes.byref(device_handle))
    data.handle = device_handle
    return data