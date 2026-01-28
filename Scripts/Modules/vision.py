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
from matplotlib.pyplot import box
import numpy as np
from ultralytics import YOLO
import torch

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

def open_mp4(mp4_path):
    """Open a video capture from the specified MP4 file path."""
    cap = cv2.VideoCapture(mp4_path)
    if not cap.isOpened():
        raise ValueError(f"MP4 file at path {mp4_path} could not be opened.")
    return cap

def close_mp4(cap):
    """Release the video capture object for MP4 files."""
    cap.release()
    cv2.destroyAllWindows()

def open_feed_window(cap):
    """
    Open a window displaying the camera feed and return a reference to that window.
    This allows real-time monitoring of the dice during testing.
    """
    window_name = 'Die Tester - Camera Feed'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    # I'm returning cam, since I'm returning 2 args from open_mp4_feed
    return window_name

def show_frame_in_window(window_name, frame):
    """
    Display a single frame in the specified camera feed window.
    This function will be called repeatedly to update the display with new frames.
    """
    
    # Display initial frame to verify camera is working
    cv2.imshow(window_name, frame)
    cv2.waitKey(1)  # Brief pause to ensure window displays
    print(f"Camera feed window '{window_name}' opened successfully")

def close_feed_window(window_name):
    """
    Close the camera feed window.
    This should be called when we are finished testing to clean up the display resources.
    """
    cv2.destroyWindow(window_name)
    print(f"Camera feed window '{window_name}' closed successfully")
    return None

def capture_frame(cap):
    """
    Capture a single frame from the camera.
    This frame will be used for die detection and analysis.
    """
    ret, frame = cap.read()
    if not ret:
        return ret, None
    return ret, frame

def analyze_frame(frame):
    results = model(frame)
    return results[0]

def count_pips_from_detections(detections):
    """
    Analyze the detection results to count the number of pips on each detected die.
    This function will extract pip counts from the model's output.
    """
    classes = detections.boxes.cls
    return int(torch.sum(classes).item())

def get_bounding_box_index(detections):
    # Class = 0 => die
    # Class = 1 => pip
    # There should only be 1 instance of a die in the frame
    class_mask = (detections.boxes.cls == 0) # Class of 0 is die, 1 is pip
    box_index = class_mask.nonzero()
    if box_index.numel() == 0:
        return None  # No die detected
    return box_index

def add_bounding_box_to_frame(frame, detections):
    box_index = get_bounding_box_index(detections)
    if box_index is None:
        return frame  # No die detected, return original frame
    x1, y1, x2, y2 = detections.boxes.xyxy[box_index].cpu().numpy().astype(int)[0][0]
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return frame

def add_border_details_to_frame(frame, border_size=400, dice_state='unknown', pips=0):
    """
    Add a padding border to the left side of the image frame.
    This border can be used to display additional information related to the frame.
    """
    height, width, channels = frame.shape
    new_width = width + border_size
    bordered_frame = np.zeros((height, new_width, channels), dtype=frame.dtype)
    bordered_frame[:, border_size:] = frame
    cv2.putText(bordered_frame, f'State: {dice_state}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(bordered_frame, f'Pips: {pips}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    return bordered_frame
class Dice:
    """
    Maintains the last n iterations of coordinates and provides analysis methods.
    """
    def __init__(self, buffer_size=10):
        self.buffer_size = buffer_size
        self.coordinates = []
        self.current_index = None
        self.stuck_counter = 0
    
    def add_coordinate(self, detections):
        """Add a new coordinate and drop the oldest if buffer exceeds size."""
        box_index = get_bounding_box_index(detections)
        if box_index is None:
            self.current_index = None
            self.stuck_counter += 1
            return  # No die detected, do not add coordinate
        self.stuck_counter = 0
        x, y, w, h = detections.boxes.xywh[box_index].cpu().numpy().astype(int)[0][0]
        self.coordinates.append((x, y))
        self.current_index = box_index.item()
        print(f'box_index: {self.current_index}')
        if len(self.coordinates) > self.buffer_size:
            self.coordinates.pop(0)
    
    def get_coordinates(self):
        """Return all stored coordinates."""
        return self.coordinates
    
    def get_average_position(self):
        """Calculate the average position of all coordinates in buffer."""
        if not self.coordinates:
            return None
        avg_x = np.mean([coord[0] for coord in self.coordinates])
        avg_y = np.mean([coord[1] for coord in self.coordinates])
        return (avg_x, avg_y)
    
    def get_movement_magnitude(self):
        """Calculate total movement magnitude between first and last coordinate."""
        if len(self.coordinates) < 2:
            return 0
        x1, y1 = self.coordinates[0]
        x2, y2 = self.coordinates[-1]
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def is_stable(self, threshold=5):
        """Determine if the die is stable based on movement magnitude."""
        return self.get_movement_magnitude() < threshold
    
    def is_stuck(self, threshold=50):
        """Determine if the die has been stuck (not detected) for more than some number of frames."""
        return self.stuck_counter > threshold
    
    def dice_state(self, threshold=5):
        """Return 'stable' or 'in motion' based on movement magnitude."""
        if self.current_index is None:
            return 'unknown'
        elif self.is_stable(threshold):
            return 'stable'
        else:
            return 'in motion'

