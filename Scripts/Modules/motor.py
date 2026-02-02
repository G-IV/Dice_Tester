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

class Motor:
    
    FREQUENCY = 333
    POS_90 = 14 # Duty cycle 14% for +90 degrees
    POS_90N = 84 # Duty cycle 84% for -90 degrees
    CENTER_POS = (POS_90 + POS_90N) / 2
    STARTING_POS = CENTER_POS # Duty cycle 14% for center position

    class data:
        '''Just using what the documentation suggests'''
        handle = ctypes.c_int()
        name = ""

    def __init__(self):
        self.data = self.data()
        self.open()

    def open(self):
        device_handle = ctypes.c_int()
        dwf.FDwfDeviceOpen(ctypes.c_int(-1), ctypes.byref(device_handle))
        self.data.handle = device_handle

    def close(self):
        dwf.FDwfAnalogOutReset(self.data.handle)
        dwf.FDwfDeviceClose(self.data.handle)
        self.data = None

    def generate(self, symmetry=50):
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
        dwf.FDwfAnalogOutNodeEnableSet(self.data.handle, channel, constants.AnalogOutNodeCarrier, ctypes.c_bool(True))
    
        # set function type
        dwf.FDwfAnalogOutNodeFunctionSet(self.data.handle, channel, constants.AnalogOutNodeCarrier, function)
    
        # load data if the function type is custom
        if function == constants.funcCustom:
            data_length = len(data)
            buffer = (ctypes.c_double * data_length)()
            for index in range(0, len(buffer)):
                buffer[index] = ctypes.c_double(data[index])
            dwf.FDwfAnalogOutNodeDataSet(self.data.handle, channel, constants.AnalogOutNodeCarrier, buffer, ctypes.c_int(data_length))
    
        # set frequency
        dwf.FDwfAnalogOutNodeFrequencySet(self.data.handle, channel, constants.AnalogOutNodeCarrier, ctypes.c_double(frequency))
    
        # set amplitude or DC voltage
        dwf.FDwfAnalogOutNodeAmplitudeSet(self.data.handle, channel, constants.AnalogOutNodeCarrier, ctypes.c_double(amplitude))
    
        # set offset
        dwf.FDwfAnalogOutNodeOffsetSet(self.data.handle, channel, constants.AnalogOutNodeCarrier, ctypes.c_double(offset))
    
        # set symmetry
        dwf.FDwfAnalogOutNodeSymmetrySet(self.data.handle, channel, constants.AnalogOutNodeCarrier, ctypes.c_double(symmetry))
    
        # set running time limit
        dwf.FDwfAnalogOutRunSet(self.data.handle, channel, ctypes.c_double(run_time))
    
        # set wait time before start
        dwf.FDwfAnalogOutWaitSet(self.data.handle, channel, ctypes.c_double(wait))
    
        # set number of repeating cycles
        dwf.FDwfAnalogOutRepeatSet(self.data.handle, channel, ctypes.c_int(repeat))
    
        # start
        dwf.FDwfAnalogOutConfigure(self.data.handle, channel, ctypes.c_bool(True))
        return
    
    def move_to_default_position(self):
        self.position = self.STARTING_POS
        self.generate(self.STARTING_POS)
    
    def move_to_position(self, position):
        self.position = position
        self.generate(position)

    def flip_position(self):
        if self.position == self.POS_90:
            self.position = self.POS_90N
        else:
            self.position = self.POS_90
        self.generate(self.position)

    def wait(self, seconds = .5):
        import time
        time.sleep(seconds)

