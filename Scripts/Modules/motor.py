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


from threading import Thread
from queue import Queue
import time
import enum

class MotorCommand(enum.Enum):
    MOVE_TO_POSITION = 1
    FLIP = 2
    CLOSE = 3

class Motor:

    FREQUENCY = 333
    POS_90 = 14 # Duty cycle 14% for +90 degrees
    POS_90N = 84 # Duty cycle 84% for -90 degrees
    CENTER_POS = int((POS_90 + POS_90N) / 2)
    POS_UNCAP = POS_90 # Duty cycle 14% for uncap position
    STARTING_POS = POS_UNCAP # Duty cycle 14% for starting position

    class data:
        '''Just using what the documentation suggests'''
        handle = ctypes.c_int()
        name = ""

    def __init__(
            self, 
            logging: bool = False
        ):
        self.data = self.data()
        self.logging = logging
        self.position = None

        self.stop_thread = False # Flag to signal the motor manager thread to stop

        self.motor_queue = Queue()
        self.motor_thread = Thread(target=self._motor_manager)
        self.motor_thread.daemon = True
        self.motor_thread.start()

        self._open()

    def _open(self):
        device_handle = ctypes.c_int()
        dwf.FDwfDeviceOpen(ctypes.c_int(-1), ctypes.byref(device_handle))
        self.data.handle = device_handle

        self._cmd("MOVE_TO_POSITION", self.STARTING_POS)  # Move to starting position on initialization
        self._wait(2)  # Wait for 2 seconds to ensure the motor has time to move to the starting position
        if self.logging:
            print(f"Motor opened with handle: {self.data.handle}")

    def _close(self):
        self.stop_thread = True  # Signal the motor manager thread to stop
        dwf.FDwfAnalogOutReset(self.data.handle)
        dwf.FDwfDeviceClose(self.data.handle)
        self.data = None

    def _motor_manager(self) -> None:
        while not self.stop_thread:
            try:
                queue_data = self.motor_queue.get(timeout=1)
                if queue_data['action'] == MotorCommand.CLOSE:
                    self._close()
                elif queue_data['action'] == MotorCommand.MOVE_TO_POSITION:
                    position = queue_data['data']
                    self._setPWM(symmetry=self.POS_UNCAP)  # Move to uncap position first to ensure consistent movement
                    self.position = position
                    if self.logging:
                        print(f"Motor moved to position with duty cycle: {position}%")
                elif queue_data['action'] == MotorCommand.FLIP:
                    shake = queue_data['data']  # Using 'data' field to pass shake boolean for simplicity
                    position = self.POS_90 if self.position != self.POS_90 else self.POS_90N
                    if shake:
                        self._shake()
                    self._setPWM(symmetry=position)
                    if self.logging:
                        print(f"Motor flipped to position with duty cycle: {position}%")
                    
            except Exception as e:
                continue  # Timeout occurred, loop back and check for new commands 

    def _cmd(self, action: MotorCommand, data=None) -> None:
        if action == MotorCommand.MOVE_TO_POSITION and data is None:
            raise ValueError("Position must be provided when action is MOVE_TO_POSITION.")
        self.motor_queue.put({'action': action, 'data': data})

    def _setPWM(self, symmetry=50):
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

        self.position = symmetry
    
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
     
    def _shake(self) -> None:
        """Flip the cup with a shaking motion to ensure the pip is dislodged."""
        offset = 10  # Amount to shake in either direction from the center position
        if self.position == self.POS_90:
            shake_to = self.CENTER_POS + offset
            shake_from = self.CENTER_POS - offset
        else:
            shake_to = self.CENTER_POS + offset
            shake_from = self.CENTER_POS - offset

        shake_wait_time_seconds = 0.25
        num_seconds_to_shake = 2
        shakes = int(num_seconds_to_shake / (shake_wait_time_seconds * 2))
        for _ in range(shakes):
            self._setPWM(shake_to)
            self._wait(shake_wait_time_seconds)
            self._setPWM(shake_from)
            self._wait(shake_wait_time_seconds)

    def _wait(self, seconds: float = 0.5) -> None:
        """Wait for the specified number of seconds while keeping the motor responsive to new commands."""
        time.sleep(seconds)

    """
    Note to myself: I went back and forth on whether to have Motor.cmd as the public method, or to wrap it in more easily readable methods.
    I guess you can see which way I went.  I suppose either way would have been fine, but I prefered easier to read.
    """

    def flip(self, shake: bool = False) -> None:
        """Flip the cup by moving to the uncap position, then optionally shaking."""
        self._cmd(action=MotorCommand.FLIP, data=shake)  # Using 'data' field to pass shake boolean for simplicity

    def move_to_position(self, position: int) -> None:
        """Move the motor to the specified position."""
        self._cmd(action=MotorCommand.MOVE_TO_POSITION, data=position)

    def close(self) -> None:
        """Close the motor connection and stop the motor manager thread."""
        self._cmd(action=MotorCommand.CLOSE)