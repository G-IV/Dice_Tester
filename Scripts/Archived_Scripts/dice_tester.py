'''
The purpose of this script is to manage a Die Tester device, which includes controlling a motor and a camera. 
The script will handle the
 - Motor control
 - Machine vision
 - Error handling to ensure that any issues with the device are properly managed and logged.

The motor is a servo motor, which takes a 333Hz pulse signal with a duty cycle of:
 - 0.5ms (off) for -90 degrees
 - 1.5ms (off) for 0 degrees
 - 2.5ms (off) for +90 degrees

Because the duty cycle is the percentage of the period that the signal is on, we can calculate the duty cycle for any position between -90 and +90 degrees using the following formula:
duty_cycle = 100 * ((period - position) / period)

We will use the AD2's analog output to generate the pulse signal for the servo motor. 
The script will include functions to 
 - Open the device
 - Generate the pulse signal
 - Close the device when finished
 - Handle any errors that may occur during the operation of the device

For machine vision, we will use a custom model trained in Label Studio and exported to Ultralytic's YOLO to monitor the dice.  This will be a multi-step process that includes:
 - Train model in Label Studio, using the images captured by the camera.
 - The first training set should include images of the dice in motion and as the dice come to a stop, with the goal of being able to identify when the dice have come to a stop.
 - The second training set should include images of the dice at rest, with the goal of being able to identify the number on the top face of the dice.
 - Once we have both models trained and tested, we'll use Ultralytics' to run the models in real-time on the MacBook, using the Logitech camera feed to monitor the dice and provide feedback on their position and the number on the top face.

Datalogging will be done using sqlite, which is supposed to be natively supported in Python.  We'll create a database to store the results of each roll, including:
 - the position of the motor
 - the number on the bottom face of the dice
 - any errors that may occur during the operation of the device
 - a timestamp for each entry
 - an assigned ID for each dice that is tested.

Once a dice has come to a stop and the number on the top face has been identified, the script will log the result and rotate the motor in the opposite direction 180° to roll the dice again.  So if the motor is at 90°, rotate to -90°, and if the motor is at -90°, rotate to 90°.  This will allow us to continuously test the dice and log the results.
'''

'''
        ####################### MOTOR CONTROL #######################
'''

'''
Imports
'''
import ctypes
from sys import path
from os import sep

'''
This section add the path to the AD2's API to the system path, which allows us to import the constants from the API and use them in our code.  The path to the API may need to be updated depending on where it is installed on your system.
'''
lib_path = sep + "Library" + sep + "Frameworks" + sep + "dwf.framework" + sep + "dwf"
dwf = ctypes.cdll.LoadLibrary(lib_path)
constants_path = sep + "Applications" + sep + "WaveForms.app" + sep + "Contents" + sep + "Resources" + sep + "SDK" + sep + "samples" + sep + "py"
path.append(constants_path)

# Import the constants from the AD2's API
import dwfconstants as constants
import time

# Constants
FREQUENCY = 333
POS_90 = .0025
POS_45 = .0020
POS_0 = .0015
POS_45N = .0010
POS_90N = .0005
STARTING_POSITION = POS_90 #TODO: confirm which position is the correct starting position, and update the constant and function call accordingly

# This class is used to store the handle for the AD2 device.
class data:
    handle = ctypes.c_int()
    name = ""

# Open the connection to the AD2
def open_AD2():
    device_handle = ctypes.c_int()
    dwf.FDwfDeviceOpen(ctypes.c_int(-1), ctypes.byref(device_handle))
    data.handle = device_handle
    return data

# Close the connection to the AD2
def close_AD2(device_data):
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

# This function gets the correct duty cycle for a given position in the range of -90 to 90 degrees, which is the range of motion for the servo motor.  The duty cycle is calculated using the formula mentioned above, which converts the position to a percentage of the period that the signal is on.
def get_duty_cycle_from_position(position):
    """
        Converts a position defined to a range of 5-25 ms, where 5 ms corresponds to -90 degrees, 15 ms corresponds to 0 degrees, and 25 ms corresponds to +90 degrees.  The duty cycle is calculated as a percentage of the period that the signal is on and the position value is given as the period the signal is off, so the formula is:

        duty_cycle = 100 * ((period - position) / period)
    """
    period = 1 / 333 # period of the signal at 333Hz
    if position < -90 or position > 90:
        raise ValueError("Position must be between -90 and 90 degrees")
    duty_cycle = 100 * ((period - position) / period)
    return duty_cycle

# Set the motor to the initial position.  I'm not certain which position this will be (90 or -90), but it should be one of the two extremes.  This will be the starting point for testing the motor control and machine vision, and will allow us to ensure that the motor is functioning correctly before we start testing the dice.
def set_motor_to_default_position(device_data):
    """
        Set the motor to the initial position.  I'm not certain which position this will be (90 or -90), but it should be one of the two extremes.  This will be the starting point for testing the motor control and machine vision, and will allow us to ensure that the motor is functioning correctly before we start testing the dice.
    """
    symmetry = get_duty_cycle_from_position(STARTING_POSITION)
    print(f"Initializing motor position to 90 degrees with duty cycle: {symmetry}")
    generate(device_data, symmetry=symmetry)
    wait_for_motor_update() # wait for the motor to update to the new position before proceeding with testing
    print("Motor initialized to starting position")
    return STARTING_POSITION

# Reverse the position of the motor by rotating it 180 degrees.  This will allow us to continuously test the dice by rolling them back and forth between the two positions, and will also allow us to test the motor control by ensuring that it can accurately rotate to both positions.
def reverse_motor_position(device_data, current_position):
    """
        Reverse the position of the motor by rotating it 180 degrees.  This will allow us to continuously test the dice by rolling them back and forth between the two positions, and will also allow us to test the motor control by ensuring that it can accurately rotate to both positions.
    """
    if current_position == POS_90:
        new_position = POS_90N
    else:
        new_position = POS_90
    symmetry = get_duty_cycle_from_position(new_position)
    print(f"Reversing motor position to {new_position} degrees with duty cycle: {symmetry}")
    generate(device_data, symmetry=symmetry)
    wait_for_motor_update() # wait for the motor to update to the new position before proceeding with testing
    print("Motor position reversed")
    return new_position

# I need a function to wait for the motor to update.  I think a second should be enough time for the motor to update to the new position, but this may need to be adjusted based on testing.  This will allow us to ensure that the motor has reached the desired position before we start testing the dice and using the machine vision to monitor their movement.
def wait_for_motor_update():
    """
        Wait for the motor to update to the new position.  I think a second should be enough time for the motor to update to the new position, but this may need to be adjusted based on testing.  This will allow us to ensure that the motor has reached the desired position before we start testing the dice and using the machine vision to monitor their movement.
    """
    print("Waiting for motor to update to new position...")
    time.sleep(1) # wait for 1 second, adjust as needed based on testing
    print("Motor update complete")

'''
        ####################### MACHINE VISION #######################
'''

# Imports
from ultralytics import YOLO
import cv2
import random # TODO: remove this import once we have the machine vision model set up and can use it to identify the number on the top face of the dice, this is just a placeholder for testing the flow of the program until we have the model set up and can replace the random number generation with the actual predictions from the model.

# Constants
MODEL_PATH = '/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/5 - Tower Rolls/runs/training/weights/best.pt'

def open_camera():
    """
        Placeholder function for opening the camera feed.  This will involve using OpenCV or a similar library to access the Logitech camera and display the feed in a window on the MacBook, which will allow us to monitor the dice in real-time and provide feedback on their position and the number on the top face.
    """
    cam = cv2.VideoCapture(0)  # 0 for default camera, adjust if needed
    if not cam.isOpened():
        raise RuntimeError("Failed to open camera")
    print("Camera opened successfully")
    return cam

def close_camera(cam):
    """
        Placeholder function for closing the camera feed.  This will involve releasing the camera resource and closing any windows that were opened to display the feed, which will ensure that we properly clean up the resources used by the camera when we are finished testing.
    """
    if cam:
        cam.release()
        cv2.destroyAllWindows()
        print("Camera closed successfully")
    else:
        print("Warning: Attempted to close camera, but it was not open")
    return None

def open_camera_feed(cam):
    """
    Open a window displaying the camera feed and return a reference to that window.
    This allows real-time monitoring of the dice during testing.
    """
    window_name = 'Die Tester - Camera Feed'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    # Display initial frame to verify camera is working
    ret, frame = cam.read()
    if ret:
        cv2.imshow(window_name, frame)
        cv2.waitKey(1)  # Brief pause to ensure window displays
        print(f"Camera feed window '{window_name}' opened successfully")
    else:
        print("Warning: Failed to read initial frame from camera")
    
    return window_name
    
def close_camera_feed(window_name):
    """
    Close the camera feed window.
    This should be called when we are finished testing to clean up the display resources.
    """
    cv2.destroyWindow(window_name)
    print(f"Camera feed window '{window_name}' closed successfully")
    return None

def wait_for_dice_to_stop(cam):
    """
        Placeholder function for waiting for the dice to come to a stop.  This will likely involve monitoring the camera feed and using the machine vision model to detect when the dice have come to a stop, which may be indicated by a lack of movement or a specific pattern in the images.
    """
    print("Waiting for dice to stop moving...")
        
    # Load the motion detection model
    motion_model = YOLO('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/1 - Images/runs/detect/training10/weights/best.pt')
    
    # Variables to track dice stability
    previous_boxes = []
    stability_threshold = 5  # Number of consecutive stable frames needed
    stable_frames = 0
    position_tolerance = 10  # Pixels
    size_tolerance = 10  # Pixels
    
    cv2.namedWindow('Dice Motion Detection', cv2.WINDOW_NORMAL)
    
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to read frame from camera")
            break
        
        # Run inference
        results = motion_model(frame, verbose=False)
        
        # Draw bounding boxes and check stability
        current_boxes = []
        annotated_frame = frame.copy()
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = box.conf[0].cpu().numpy()
                
                # Draw bounding box
                cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(annotated_frame, f'{conf:.2f}', (int(x1), int(y1)-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                
                current_boxes.append((x1, y1, x2, y2))
        
        # Check if dice position is stable
        if len(current_boxes) > 0 and len(previous_boxes) > 0:
            is_stable = True
            for curr_box in current_boxes:
                cx1, cy1, cx2, cy2 = curr_box
                curr_width = cx2 - cx1
                curr_height = cy2 - cy1
                
                # Check against previous boxes
                for prev_box in previous_boxes:
                    px1, py1, px2, py2 = prev_box
                    prev_width = px2 - px1
                    prev_height = py2 - py1
                    
                    # Check position and size changes
                    if (abs(cx1 - px1) > position_tolerance or 
                        abs(cy1 - py1) > position_tolerance or
                        abs(curr_width - prev_width) > size_tolerance or
                        abs(curr_height - prev_height) > size_tolerance):
                        is_stable = False
                        break
                
                if not is_stable:
                    break
            
            if is_stable:
                stable_frames += 1
            else:
                stable_frames = 0
        else:
            stable_frames = 0
        
        # Display stability status
        status_text = f'Stable frames: {stable_frames}/{stability_threshold}'
        cv2.putText(annotated_frame, status_text, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        cv2.imshow('Dice Motion Detection', annotated_frame)
        
        # Check if dice have stabilized
        if stable_frames >= stability_threshold:
            print("Dice have stopped moving!")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_name = f'dice_snapshot_{timestamp}.jpg'
            cv2.imwrite(snapshot_name, frame)
            print(f"Snapshot saved as: {snapshot_name}")
            cv2.destroyWindow('Dice Motion Detection')
            previous_boxes = current_boxes
            return snapshot_name
        
        previous_boxes = current_boxes
        
        # Allow early exit with 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Motion detection interrupted by user")
            cv2.destroyWindow('Dice Motion Detection')
            break
    
    cv2.destroyWindow('Dice Motion Detection')
    return None

def identify_dice_result(img_path):
    """
        Placeholder function for identifying the number on the top face of the dice using the machine vision model.  This will involve processing the images from the camera feed and using the trained model to predict the number on the top face of the dice, which will then be logged to the database along with the motor position and any errors that may occur during testing.
    """
    print(f"Identifying dice result from image: {img_path}")
    # Load the dice face identification model
    dice_model = YOLO('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/4 - Single Side/runs/training/weights/best.pt')
    
    # Run inference on the captured image
    results = dice_model(img_path, verbose=False)
    
    # Extract the prediction with highest confidence
    if len(results) > 0 and len(results[0].boxes) > 0:
        # Get the first detection (assuming one die in frame)
        box = results[0].boxes[0]
        class_id = int(box.cls[0].cpu().numpy())
        confidence = float(box.conf[0].cpu().numpy())
        
        # Class ID should correspond to dice face (1-6)
        dice_face = class_id + 1  # Adjust if your model classes are 0-5
        
        print(f"Detected dice face: {dice_face} with confidence: {confidence:.2f}")
        return dice_face, confidence
    else:
        print("Warning: No dice face detected in image")
    # return random.randint(1, 6), random.randint(1, 100) # Placeholder return value, replace with actual prediction from the machine vision model


'''
        ####################### DATA LOGGING #######################
'''
# Imports
import sqlite3
from datetime import datetime

# Constants
DATABASE_PATH = 'die_tester_results.db' # TODO: update with the desired path for the database

# This function initializes the database and creates the necessary table if it doesn't already exist.  The table will include columns for the ID, timestamp, motor position, dice result, and any errors that may occur during testing.
def initialize_database():
    """
        Initializes the database and creates the necessary table if it doesn't already exist.  The table will include columns for the ID, timestamp, motor position, dice result, and any errors that may occur during testing.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            motor_position REAL NOT NULL,
            dice_result INTEGER NOT NULL,
            confidence FLOAT NOT NULL,
            PRIMARY KEY (timestamp, id)
        )
    ''')
    conn.commit()
    conn.close()

# Get the most recent id for a given dice, then return that id incremented by 1 for a new dice.  This will allow us to keep track of multiple dice and their results in the database, and allows users to not have to manually input an ID for each dice that is tested.
def get_next_dice_id():
    """
        Get the most recent id for a given dice, then return that id incremented by 1 for a new dice.  This will allow us to keep track of multiple dice and their results in the database, and allows users to not have to manually input an ID for each dice that is tested.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(id) FROM test_results')
    result = cursor.fetchone()
    conn.close()
    if result[0] is not None:
        return result[0] + 1
    else:
        return 1

# This function logs the results of each test to the database, including the motor position, the result of the dice roll, and any errors that may occur during testing.  The timestamp is automatically generated when the entry is created.
def log_test_result(id, motor_position, dice_result, confidence):
    """
        Logs the results of each test to the database, including the motor position, the result of the dice roll, and any errors that may occur during testing.  The timestamp is automatically generated when the entry is created.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    print(f"Logging test result to database: ID={id}, Timestamp={timestamp}, Motor Position={motor_position}, Dice Result={dice_result}, Confidence={confidence}")
    cursor.execute('''
        INSERT INTO test_results (timestamp, id, motor_position, dice_result, confidence)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, id, motor_position, dice_result, confidence))
    conn.commit()
    conn.close()


'''
        ####################### ERROR HANDLING #######################
'''

'''
        ####################### MAIN LOOP #######################
'''
if __name__ == "__main__":
    print("Die Tester Control System")
    print("Commands: 'start [dice_id] [samples]' - Begin testing | 'stop' - Stop testing | 'exit' - Quit program")
    
    AD2 = None
    running = False
    current_dice_id = None
    max_samples = None
    sample_count = 0
    position = STARTING_POSITION
    cam = None
    cam_window = None
    
    try:
        while True:
            command = input("\nEnter command: ").strip().lower()
            parts = command.split()
            
            if parts[0] == "start":
                if not running:
                    try:
                        # Initialize the database if it DNE
                        initialize_database()

                        # Get the dice_id, either from arguments or by generating the next ID in the database
                        dice_id = parts[1] if len(parts) > 1 else get_next_dice_id()
                        current_dice_id = dice_id
                        
                        # Get the max_samples, either from arguments or set default to 100
                        max_samples = int(parts[2]) if len(parts) > 2 else 100
                        sample_count = 0
                        
                        print(f"Starting die tester for dice ID: {current_dice_id} with {max_samples} samples")

                        # Open the AD2 and initialize the motor position
                        AD2 = open_AD2()
                        set_motor_to_default_position(AD2)
                        print("Analog Discovery 2 opened successfully and motor set to default position")

                        cam = open_camera()
                        cam_window = open_camera_feed(cam)
                        running = True
                        print("Die tester started. Use 'stop' to pause or 'exit' to quit.")
                    except Exception as e:
                        print(f"Error starting device: {e}")
                else:
                    print("Die tester is already running")
            
            elif parts[0] == "stop":
                if running:
                    try:
                        print("Stopping die tester...")
                        set_motor_to_default_position(AD2)
                        if AD2:
                            close_AD2(AD2)
                            AD2 = None
                        if cam_window:
                            cam_window = close_camera_feed(cam_window)
                        if cam:
                            cam = close_camera(cam)
                        running = False
                        current_dice_id = None
                        max_samples = None
                        sample_count = 0
                        print("Die tester stopped")
                    except Exception as e:
                        print(f"Error stopping device: {e}")
                else:
                    print("Die tester is not running")
            
            elif parts[0] == "exit":
                if running:
                    print("Shutting down die tester...")
                    set_motor_to_default_position(AD2)
                    if AD2:
                        close_AD2(AD2)
                    if cam_window:
                        cam_window = close_camera_feed(cam_window)
                    if cam:
                        cam = close_camera(cam)
                print("Exiting program")
                break
            
            else:
                print("Invalid command. Use 'start [dice_id] [samples]', 'stop', or 'exit'")

            '''
            Now that we have initialized the AD2, got the motor in the starting position, and set up the database, we can start the main testing loop.  This will involve:
                1) Rotate the dice tower by 180 degrees to roll the dice
                2) Monitor the camera feed to detect when the dice have come to a stop
                3) Once the dice have come to a stop, use the machine vision model to identify the number on the top face of the dice
                4) Log the result to the database, including the motor position, the result of the dice roll, and any errors that may occur during testing
                5) Repeat the process until we have reached the max_samples for the current
            '''
            while running and sample_count < max_samples:
                # We are assuming that the motor is in the correct starting position, we simply rotate it 180 degrees and wait for the camera to detect that the dice have come to a stop, then we use the machine vision model to identify the number on the top face of the dice, log the result to the database, and repeat the process until we have reached the max_samples for the current dice.  This will allow us to continuously test the dice and log the results without having to manually start and stop the tester for each dice.
                position = reverse_motor_position(AD2, position)
                img_path = wait_for_dice_to_stop(cam) # TODO This maybe a spot where the program could get hung up if the camera feed or machine vision model is not working correctly, so we may want to add a timeout or some error handling here to ensure that the program doesn't get stuck waiting indefinitely, along with some error handling to potentially quit the program or skip to the next test if there is an issue with the camera feed or machine vision model.
                dice_result, confidence = identify_dice_result(img_path=img_path)
                log_test_result(current_dice_id, position, dice_result, confidence)
                sample_count += 1
                print(f"Sample {sample_count}/{max_samples} logged for dice ID: {current_dice_id}")

                # Check if we've reached the max samples and auto-stop
            if running and sample_count >= max_samples:
                print(f"\nReached maximum samples ({max_samples}). Stopping die tester...")
                position = set_motor_to_default_position(AD2)
                if AD2:
                    close_AD2(AD2)
                    AD2 = None
                if cam_window:
                    cam_window = close_camera_feed(cam_window)
                if cam:
                    cam = close_camera(cam)
                running = False
                current_dice_id = None
                max_samples = None
                sample_count = 0
                print("Die tester stopped automatically")
    except Exception as e:
        print(f"An error occurred: {e}")
        if AD2:
            print("Stopping die tester...")
            set_motor_to_default_position(AD2)
            close_AD2(AD2)
        if cam_window:
            cam_window = close_camera_feed(cam_window)
        if cam:
            cam = close_camera(cam)
        print("Die tester stopped due to error")