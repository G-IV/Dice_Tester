'''
This script will handle the vision processing tasks, utilizing Ultralyitic's YOLO model.
1) Monitor a video feed from a connected camera.
3) Detect and identify dice within the video frames.
4) Detect when dice are in motion after the motor has turned the tower.
5) Detect when dice have come to rest and capture their final positions.
6) Count the number of pips on the die and determine the bottom face value.
7) The user should see a window displaying the state of the dice (Not found, In Motion, At Rest).  When at rest, teh window should also display the detected bottom face value.  When dice are not found, the user should be prompted to adjust the camera or dice position.
'''
from __future__ import annotations
from email.mime import image
import cv2
from cv2.typing import MatLike
from matplotlib.pyplot import box
import numpy as np
from ultralytics import YOLO
import torch
from enum import Enum
from typing import Union
from pathlib import Path

class Feed:
    class FeedType(Enum): 
        CAMERA = 'camera'
        VIDEO = 'video'
        IMG = 'img'
        
    VALID_FILE_TYPES = ['mp4', 'jpg', 'png']

    def __init__(
            self,
            feed_type: FeedType = FeedType.CAMERA, 
            source: Union[int, Path] = 0,
            logging: bool = False,
            show_window: bool = True
        ):
        """
        Docstring for __init__
        
        :param self: Class for managing instance of camera/video/image feed
        :param feed_type: This can be camera, video, or img source.
        :param source: Camera index or file path for video or image feeds.
        :param logging: Flag to enable or disable logging.
        :param model_path: Path to the YOLO model file.
        """
        # Handle validation feed type checks
        if not isinstance(feed_type, self.FeedType):
            raise TypeError("TypeError: unsupported operand type(s) for 'in': 'str' and 'EnumMeta'")
        elif feed_type == self.FeedType.CAMERA:
            if not isinstance(source, int):
                raise ValueError("For CAMERA feed type, source must be an integer camera index.")
            elif source < 0:
                raise ValueError("For CAMERA feed type, source must be a non-negative integer.")
        elif feed_type in [self.FeedType.VIDEO, self.FeedType.IMG]:
            if not isinstance(source, Path):
                raise ValueError("For VIDEO or IMG feed type, source must be a Path object.")
            elif source.suffix.lower()[1:] not in self.VALID_FILE_TYPES:
                raise ValueError("For VIDEO or IMG feed type, source file must be of type: " + ", ".join(self.VALID_FILE_TYPES))
            elif not source.exists():
                raise FileNotFoundError("For VIDEO or IMG feed type, source file path does not exist.")
        
        self.feed_type = feed_type
        self.source = source
        self.logging = logging

        self.cap = self.open_source()
        if show_window:
            self.window = self.open_window()

    def open_source(self):
        """Open the feed source based on the feed type."""
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open source: {self.source}")
        return self.cap
    
    def reopen_source(self, new_source: Union[int, Path]):
        """Reopen the feed source with a new source."""
        self.close_source()
        self.source = new_source
        self.cap = self.open_source()

    def close_source(self):
        """Close the feed source."""
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def open_window(self):
        """Open a window to display the feed."""
        window_name = 'Die Tester - Camera Feed'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.waitKey(1)  # Brief pause to ensure window displays
        return window_name
    
    def close_window(self):
        """Close the feed window."""
        if self.window:
            cv2.destroyWindow(self.window)
            self.window = None

    def destroy(self):
        """Clean up resources."""
        self.close_source()
        self.close_window()

    def capture_frame(self):
        """Capture a single frame from the feed."""
        ret, frame = self.cap.read()
        if not ret:
            return ret, None
        return ret, frame
    
    def add_bounding_box(self, frame, bounding_box, color=(0, 255, 0), thickness=2):
        """Add a bounding box to the frame."""
        if bounding_box is None:
            return frame
        (x1, y1, x2, y2), confidence = bounding_box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
        # Add confidence score with background
        text = f'{confidence:.2f}'
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        font_thickness = 1
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        text_x, text_y = x1, y1 - 10
        cv2.rectangle(frame, (text_x, text_y - text_size[1] - 5), (text_x + text_size[0] + 5, text_y + 5), color, -1)
        cv2.putText(frame, text, (text_x + 2, text_y - 2), font, font_scale, (255, 255, 255), font_thickness)
        return frame
    
    def add_dice_bounding_box(self, frame, bounding_box):
        color = (0, 255, 0)  # Green for dice
        thickness = 2
        frame = self.add_bounding_box(frame, bounding_box, color, thickness)
        return frame
    
    def add_pip_bounding_boxes(self, frame, pip_bounding_boxes):
        color = (255, 0, 0)  # Blue for pips
        thickness = 2
        for box in pip_bounding_boxes:
            frame = self.add_bounding_box(frame, box, color, thickness)
        return frame

    def add_border_details(self, frame, dice: Dice, pips: int, border_size=400):
        """
        Add a padding border to the left side of the image frame.
        This border can be used to display additional information related to the frame.
        """
        height, width, channels = frame.shape
        new_width = width + border_size
        bordered_frame = np.zeros((height, new_width, channels), dtype=frame.dtype)
        bordered_frame[:, border_size:] = frame

        row = 30
        row_increment = 40

        cv2.putText(bordered_frame, f'State: {dice.dice_state()}', (10, row), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        row += row_increment

        cv2.putText(bordered_frame, f'Pips: {pips}', (10, row), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        row += row_increment

        if dice.buffer_size > 1:
            cv2.putText(bordered_frame, f'Roll History of {len(dice.previous_rolls)}:', (10, row), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            row += row_increment

            for value in range(1, 7):
                count = dice.previous_rolls.count(value)
                percentage = (count / len(dice.previous_rolls) * 100) if dice.previous_rolls else 0
                cv2.putText(bordered_frame, f'{value}: {percentage:.0f}%', (10, row), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                row += row_increment

            invalid_count = sum(1 for roll in dice.previous_rolls if roll > 6)
            invalid_percentage = (invalid_count / len(dice.previous_rolls) * 100) if dice.previous_rolls else 0
            cv2.putText(bordered_frame, f'Invalid (>6): {invalid_percentage:.0f}%', (10, row), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        return bordered_frame

    def show_frame(self, frame):
        """Display the frame in the feed window."""
        cv2.imshow(self.window, frame)
        cv2.waitKey(1)  # Brief pause to ensure window displays

    def wait(self, wait_ms=0):
        """Wait for a specified delay in milliseconds."""
        return cv2.waitKey(wait_ms)

    def save_image(self, frame, img_path):
        """Save the given image frame to the specified file path."""
        path = f"{img_path}"
        cv2.imwrite(path, frame)
        if self.logging:
            print(f"Image saved to {path}")
        return path

class Analyzer:
    """
    Analyze frames from the feed to detect dice and count pips.
    """
    
    def __init__(
            self, model: Path,
            logging: bool = False
            ):
        self.logging = logging
        self.model = self.open_model(model)
        self.frame = None
        self.img_analysis = None
        """
        See validations.py for box size statistics used to filter false positives.
        Dice Box Size Statistics: {'mean': 40596, 'stdev': 0, 'min_threshold': 40596, 'max_threshold': 40596}
        Pip Box Size Statistics: {'mean': 1666, 'stdev': 100.66280345788111, 'min_threshold': 1464.6743930842379, 'max_threshold': 1867.3256069157621}

        self.min_dice_box_area = 40596 * .88
        self.max_dice_box_area = 40596 * 1.12
        self.min_pip_box_area = 1460
        self.max_pip_box_area = 1870

        These numbers dropped sever true positives, manual min max's derived from watching those numbers. (max true: 2256. min true: 1295)
        """
        self.min_dice_box_area = 40596 * .88
        self.max_dice_box_area = 40596 * 1.12
        self.min_pip_box_area = 1200
        self.max_pip_box_area = 2300

    def open_model(self, model_path):
        """Load the YOLO model for dice detection."""
        self.model = YOLO(model_path)
        if self.logging:
            print(f"Model loaded from {model_path}")
        return self.model

    def load_image(self, frame: MatLike):
        self.frame = frame
        self.analyze_frame(self.frame)

    def analyze_frame(self, frame):
        self.img_analysis = self.model(frame)[0]
    
    def count_dice(self):
        """Count the number of dice detected in the frame."""
        dice_key = self.get_class_key_for_value('Dice')
        img_annotations = self.get_img_annotations()
        dice_count = img_annotations.count(dice_key)
        return dice_count

    def get_class_key_for_value(self, value: str):
        """
        Reviews the model's class names to find the key for a given class value.
        """
        image_classes = self.img_analysis.names
        dice_key = list(image_classes.keys())[list(image_classes.values()).index(value)]
        return dice_key
    
    def get_img_classes(self):
        """Return the class names from the image analysis."""
        return self.img_analysis.names
    
    def get_img_annotations(self):
        """Return the bounding box annotations from the image analysis."""
        return self.img_analysis.boxes.cls.to(int).tolist()

    def count_pips(self):
        """Count the number of dice detected in the frame."""
        return len(self.get_pip_bounding_boxes())
    
    def get_dice_bounding_box(self):
        """Get the bounding box of the detected die."""
        dice_key = self.get_class_key_for_value('Dice')
        class_mask = (self.img_analysis.boxes.cls == dice_key) # Class of 0 is die, 1 is pip
        box_index = class_mask.nonzero()
        if box_index.numel() != 1:
            return None  # No die detected
        x1, y1, x2, y2 = self.img_analysis.boxes.xyxy[box_index].cpu().numpy().astype(int)[0][0]
        confidence = self.img_analysis.boxes.conf[box_index].cpu().numpy().astype(float)[0][0]
        return (x1, y1, x2, y2), confidence

    def get_pip_bounding_boxes(self):
        """Get the bounding boxes of the detected pips."""
        pip_key = self.get_class_key_for_value('Pip')
        class_mask = (self.img_analysis.boxes.cls == pip_key) # Class of 0 is die, 1 is pip
        box_indices = class_mask.nonzero()
        if box_indices.numel() == 0:
            return []  # No pips detected
        bounding_boxes = []
        for index in box_indices:
            x1, y1, x2, y2 = self.img_analysis.boxes.xyxy[index].cpu().numpy().astype(int)[0]
            confidence = self.img_analysis.boxes.conf[index].cpu().numpy().astype(float)[0]
            area = (x2 - x1) * (y2 - y1)
            if area < self.min_pip_box_area or area > self.max_pip_box_area:
                print(f"Filtered out pip box with area {area}")
                continue  # Filter out false positives based on box area
            bounding_boxes.append(((x1, y1, x2, y2), confidence))
        return bounding_boxes

    def get_dice_center_coordinates(self):
        """Get the center coordinates of the detected die."""
        dice_key = self.get_class_key_for_value('Dice')
        class_mask = (self.img_analysis.boxes.cls == dice_key) # Class of 0 is die, 1 is pip
        box_index = class_mask.nonzero()
        if box_index.numel() != 1:
            return None  # No die detected
        x, y, _, _ = self.img_analysis.boxes.xywh[box_index].cpu().numpy().astype(int)[0][0]
        return (x, y)

class Dice:
    """
    Maintains the last n iterations of coordinates and provides analysis methods.
    """

    class DiceState(Enum):
        STABLE = 'stable'
        MOVING = 'moving'
        UNKNOWN = 'unknown'
        LOGGED = 'logged'

    """
    Initializes the Dice object to track state and positions.
    Attributes:
        buffer_size (int): The number of previous positions to store.  Set to 1 for single frame analysis.
        state (DiceState): The current state of the dice.
        logged (bool): Flag to indicate if the current state has been logged.
        center_positions (list): List to store the center positions of the dice.
        previous_rolls (list): List to store the history of previous rolls.
        movement_threshold (int): Threshold to determine if the dice is stable or moving, this is movement in pixels.
    """
    def __init__(
            self, 
            buffer_size=10, 
            movement_threshold=5
        ):
        self.buffer_size = buffer_size
        self.logged = False
        self.center_positions = []
        self.previous_rolls = []
        self.movement_threshold = movement_threshold  # Pixels

    def set_center_coordinates(self, position):
        """Add a new center position to the buffer."""
        self.center_positions.append(position)
        if len(self.center_positions) > self.buffer_size:
            self.center_positions.pop(0)
        return self.dice_state()

    def dice_state(self):
        if self.is_unknown():
            return self.DiceState.UNKNOWN
        elif self.is_stable():
            return self.DiceState.STABLE
        else:
            return self.DiceState.MOVING
    
    def get_movement_magnitude(self):
        """Calculate total movement magnitude between first and last coordinate."""
        if self.is_unknown():
            return 0
        x1, y1 = self.center_positions[0]
        x2, y2 = self.center_positions[-1]
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def is_stable(self):
        """
        Assume that the bounding box will have minor movements even when the die is still.
        If the total movement magnitude is below a certain threshold, consider it stable.
        If the buffer size is 1, we are analyzing a single frame, so consider it stable.
        """
        if self.buffer_size == 1:
            return True
        return self.get_movement_magnitude() < self.movement_threshold
    
    def is_unknown(self):
        """Determine if the die is stuck (not moving for a prolonged period)."""
        # Different scenarios where the dice position is unknown
        if len(self.center_positions) < self.buffer_size:
            return True
        elif self.center_positions[-1] == None:
            return True
        return False
    
