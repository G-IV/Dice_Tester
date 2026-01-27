'''
This script will handle the vision processing tasks, utilizing Ultralyitic's YOLO model.
1) Monitor a video feed from a connected camera.
3) Detect and identify dice within the video frames.
4) Detect when dice are in motion after the motor has turned the tower.
5) Detect when dice have come to rest and capture their final positions.
6) Count the number of pips on the die and determine the bottom face value.
7) The user should see a window displaying the state of the dice (Not found, In Motion, At Rest).  When at rest, teh window should also display the detected bottom face value.  When dice are not found, the user should be prompted to adjust the camera or dice position.
'''
import cv2
import numpy as np
from ultralytics import YOLO

# Load the pre-trained YOLO model for dice detection
model = YOLO('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Cross_Bars/3_YOLO/runs/training/weights/best.pt')

def open_camera(camera_index=0):
    """Open a video capture from the specified camera index."""
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise ValueError(f"Camera with index {camera_index} could not be opened.")
    return cap

def close_camera(cap):
    """Release the video capture object."""
    cap.release()
    cv2.destroyAllWindows()

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

def capture_frame(cam):
    """
    Capture a single frame from the camera.
    This frame will be used for die detection and analysis.
    """
    ret, frame = cam.read()
    if not ret:
        raise RuntimeError("Failed to capture frame from camera")
    return frame

def detect_dice(frame):
    """
    Use the YOLO model to detect dice in the provided frame.
    Returns detection results including bounding boxes and confidence scores.
    """
    results = model(frame)
    print("Detection results:", results)
    return results