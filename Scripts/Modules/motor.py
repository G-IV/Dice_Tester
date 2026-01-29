'''
The motor is a stepper motor with 180° range of motion.
We'll be controlling the stepper motor positioning using an old Digilent Analog Discovery 2 board as a signal generator.
Digilent published an SDK I can use to communicate with the board:
https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual
'''

import ctypes
from sys import platform, path
from os import sep

print("Running on platform: " + platform)
lib_path = sep + "Library" + sep + "Frameworks" + sep + "dwf.framework" + sep + "dwf"
print("Loading library from path: " + lib_path)
dwf = ctypes.cdll.LoadLibrary(lib_path)
constants_path = sep + "Applications" + sep + "WaveForms.app" + sep + "Contents" + sep + "Resources" + sep + "SDK" + sep + "samples" + sep + "py"

path.append(constants_path)
import dwfconstants as constants

RUN_MOTOR = True

FREQUENCY = 333
POS_90 = 14 # Duty cycle 14% for +90 degrees
POS_90N = 84 # Duty cycle 84% for -90 degrees
STARTING_POS = POS_90 # Duty cycle 14% for center position
CENTER_POS = POS_90 + (POS_90N - POS_90) / 2

class data:
    handle = ctypes.c_int()
    name = ""

def open():
    device_handle = ctypes.c_int()
    dwf.FDwfDeviceOpen(ctypes.c_int(-1), ctypes.byref(device_handle))
    data.handle = device_handle
    return data

def close(device_data):
    dwf.FDwfAnalogOutReset(device_data.handle)
    dwf.FDwfDeviceClose(device_data.handle)
    return

'''
Generate the PWM signal.  I'm going to leave much of this hardcoded, since I'll only be changing the symmetry (duty cycle)
This is the sample function provided by the documention.  Works just fine!
'''
def generate(device_data, symmetry=50):
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
    # Constants that can be parameters, but are hardcoded for our use case
    channel=1 # 1 of 2 output channels for wave generation
    function=constants.funcPulse # PWM output
    offset=0 # no offset voltage
    frequency=333 # 333Hz for servo motor control
    amplitude=5 # 5V amplitude for servo motor control
    wait=0 # no wait time before starting the signal
    run_time=0 # infinite run time
    repeat=0 # infinite repeat count
    data=[] # no custom data, since we're not using the custom function
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

def move_to_default_position(device_data):
    generate(device_data, STARTING_POS)
    return STARTING_POS

def move_to_position(device_data, position):
    generate(device_data, position)
    return position

def flip_position(current_position):
    position = get_next_position(current_position)
    generate(data, position)
    return position

def get_next_position(current_position):
    if current_position == POS_90:
        return POS_90N
    else:
        return POS_90
