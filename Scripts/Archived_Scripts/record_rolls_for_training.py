'''
The purpose of this python script is to record videos of dice rolls for training a machine learning model.

I have the Analogl Discovery 2 set up to control the motor.  The AD2 will generate a PWM signal of:
333Hz 
5V amplitude
15% and 84% duty cycles
0 Offset

There is a webcam connected to capture the video.

The order of operations is:
1. Start the motor at low speed (15% duty cycle).
2. The user hits the space bar, wich starts the video recording, changes the PWM to 84%, and waits for the user to type a digit (the result of the roll).
3. When the user types the digit, the recording stops, the video is saved with the digit + timestamp as the filename.
4. When the user hits the spacebar, the PWM changes to 15%, the video starts recording, the script waits for the user to type a digit, and the process repeats.

When the user hits 'q', the script stops the motor, releases the webcam, and exits.

We need to do this without using the keyboard module
We'll use the OpenCV library to capture keyboard input during video recording.
We'll use the Waveforms SDK to control the AD2.
'''
import ctypes
import os
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
import cv2
import numpy as np

RUN_MOTOR = True
POS_90 = 15
POS_90N = 84
FREQUENCY = 333

class data:
    handle = ctypes.c_int()
    name = ""

def open():
    device_handle = ctypes.c_int()
    dwf.FDwfDeviceOpen(ctypes.c_int(-1), ctypes.byref(device_handle))
    data.handle = device_handle
    return data

def generate(device_data, channel, function, offset, frequency=1e03, amplitude=1, symmetry=POS_90, wait=0, run_time=0, repeat=0, data=[]):
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

def main():
    # Initialize device and open connection
    device_data = open()
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        close(device_data)
        return
    
    # Set video properties
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 30
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Start motor at low speed (15% duty cycle)
    generate(device_data, 1, constants.funcPulse, 0, FREQUENCY, 5, POS_90)
    print("Motor started 0.15 duty cycle. Press SPACE to begin recording...")
    
    recording = False
    out = None
    
    try:
        while RUN_MOTOR:
            ret, frame = cap.read()
            if not ret:
                break
            
            if recording:
                out.write(frame)
            
            cv2.imshow('Die Roller', frame)
            
            # Capture keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("Exiting...")
                break
            elif key == ord(' '):  # Space bar
                if not recording:
                    # Start recording: change to high speed and begin video capture
                    generate(device_data, 1, constants.funcPulse, 0, FREQUENCY, 5, POS_90N)
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"roll_{timestamp}.mp4"
                    out = cv2.VideoWriter(filename, fourcc, fps, (frame_width, frame_height))
                    recording = True
                    print(f"Recording started: {filename}. Enter digit result (0-6):")
            elif recording and key != 255:  # A digit was pressed
                if ord('0') <= key <= ord('6'):
                    digit = chr(key)
                    # Stop recording
                    out.release()
                    recording = False
                    # Save with digit and timestamp
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    final_filename = f"5 - Tower Rolls/roll_{digit}_{timestamp}.mp4"
                    os.rename(filename, final_filename)
                    print(f"Recording saved as: {final_filename}. Press SPACE for next roll...")
                    # Return to low speed
                    generate(device_data, 1, constants.funcPulse, 0, FREQUENCY, 5, POS_90)
    
    finally:
        if recording and out:
            out.release()
        cap.release()
        cv2.destroyAllWindows()
        close(device_data)

if __name__ == "__main__":
    main()