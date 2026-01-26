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

def generate(device_data, channel, function, offset, frequency=1e03, amplitude=1, symmetry=50, wait=0, run_time=0, repeat=0, data=[]):
    """
        generate an analog signal
        parameters: - device data
                    - the selected wavegen channel (1-2)
                    - function - possible: custom, sine, square, triangle, noise, ds, pulse, trapezium, sine_power, ramp_up, ramp_down
                    - offset voltage in Volts
                    - frequency in Hz, default is 1KHz
                    - amplitude in Volts, default is 1V
                    - signal symmetry in percentage, default is 50%
                    - wait time in seconds, default is 0s
                    - run time in seconds, default is infinite (0)
                    - repeat count, default is infinite (0)
                    - data - list of voltages, used only if function=custom, default is empty
    """
    # enable channel
    channel = ctypes.c_int(channel - 1)
    dwf.FDwfAnalogOutNodeEnableSet(device_data.handle, channel, constants.AnalogOutNodeCarrier, ctypes.c_bool(True))
 
    # set function type
    dwf.FDwfAnalogOutNodeFunctionSet(device_data.handle, channel, constants.AnalogOutNodeCarrier, function)
 
    # load data if the function type is custom
    if function == constants.funcCustom:
        data_length = len(data)
        buffer = (ctypes.c_double * data_length)()
        for index in range(0, len(buffer)):
            buffer[index] = ctypes.c_double(data[index])
        dwf.FDwfAnalogOutNodeDataSet(device_data.handle, channel, constants.AnalogOutNodeCarrier, buffer, ctypes.c_int(data_length))
 
    # set frequency
    dwf.FDwfAnalogOutNodeFrequencySet(device_data.handle, channel, constants.AnalogOutNodeCarrier, ctypes.c_double(frequency))
 
    # set amplitude or DC voltage
    dwf.FDwfAnalogOutNodeAmplitudeSet(device_data.handle, channel, constants.AnalogOutNodeCarrier, ctypes.c_double(amplitude))
 
    # set offset
    dwf.FDwfAnalogOutNodeOffsetSet(device_data.handle, channel, constants.AnalogOutNodeCarrier, ctypes.c_double(offset))
 
    # set symmetry
    dwf.FDwfAnalogOutNodeSymmetrySet(device_data.handle, channel, constants.AnalogOutNodeCarrier, ctypes.c_double(symmetry))
 
    # set running time limit
    dwf.FDwfAnalogOutRunSet(device_data.handle, channel, ctypes.c_double(run_time))
 
    # set wait time before start
    dwf.FDwfAnalogOutWaitSet(device_data.handle, channel, ctypes.c_double(wait))
 
    # set number of repeating cycles
    dwf.FDwfAnalogOutRepeatSet(device_data.handle, channel, ctypes.c_int(repeat))
 
    # start
    dwf.FDwfAnalogOutConfigure(device_data.handle, channel, ctypes.c_bool(True))
    return

def close(device_data):
    """
        reset a wavegen channel, or all channels (channel=0)
    """
    dwf.FDwfAnalogOutReset(device_data.handle)
    dwf.FDwfDeviceClose(device_data.handle)
    return

def get_duty_cycle_from_position(position):
    """
        convert a position in the range of 0-180 degrees to a duty cycle in the range of 0.5-2.5 ms
    """
    period = 1 / FREQUENCY
    if position < -90 or position > 90:
        raise ValueError("Position must be between -90 and 90 degrees")
    duty_cycle = 100 *  ((period - position) / period)
    return duty_cycle


# while RUN_MOTOR:
device_data = open()
symmetry = get_duty_cycle_from_position(POS_90)
print(f"Updating position: {symmetry}")
generate(device_data, channel=1, function=constants.funcPulse, offset=0, frequency=333, amplitude=5, symmetry=symmetry, wait=0, run_time=0, repeat=0)
print("Position updated, waiting for 1 seconds")
time.sleep(1)
print("End sleep")
close(device_data)
print("Motor control test completed")