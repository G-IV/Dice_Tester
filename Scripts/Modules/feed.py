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
import time
import cv2
from matplotlib.pyplot import box
import numpy as np
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
            show_window: bool = True,
            show_adjustment_window: bool = False,
            show_annotations: bool = True,
            save_annotations: bool = False
        ):
        """
        Docstring for __init__
        
        :param self: Class for managing instance of camera/video/image feed
        :param feed_type: This can be camera, video, or img source.
        :param source: Camera index or file path for video or image feeds.
        :param logging: Flag to enable or disable logging.
        :param model_path: Path to the YOLO model file.
        :param show_annotations: Whether to display annotated frames/images.
        :param save_annotations: Whether to save annotated frames/images.
        :param images: Store all captured images in array for saving to .mp4 later
        :param annotated: Store all annotated images in array for saving to .mp4 later
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
        self.logging = logging
        self.frame = None
        self.out = None
        self.annotated_frame = None
        self.save_annotations = save_annotations
        self.show_annotations = show_annotations
        self.images = []
        self.annotated = []
        self.adjustment_window = None
        self.window = None

        self.open_source(source)

        if self.feed_type == self.FeedType.CAMERA:
            self.set_cam_defaults()
            # Grab initial feed before any chance of opening a window or recorder.
            self.capture_frame()

        if show_window:
            self.window = self.open_window()
        if show_adjustment_window:
            self.adjustment_window = self.open_cam_adjust_window()

    def open_source(self, source: Union[int, Path]):
        """Open the feed source based on the feed type."""
        self.source = source
        if self.feed_type == self.FeedType.CAMERA:
            self.cap = cv2.VideoCapture(self.source, cv2.CAP_AVFOUNDATION)
        else:
            self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open source: {self.source}")

    def open_cam_adjust_window(self):
        self.adjustment_window = "Camera Adjustments"
        self.get_cam_defaults()
        cv2.namedWindow(self.adjustment_window, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.adjustment_window, 640, 50)
        cv2.createTrackbar("Focus", self.adjustment_window, 0, 255, lambda x: self.adjust_cam_setting("focus", x))
        cv2.createTrackbar("Exposure", self.adjustment_window, 0, 255, lambda x: self.adjust_cam_setting("exposure", x))
        cv2.createTrackbar("Brightness", self.adjustment_window, 0, 255, lambda x: self.adjust_cam_setting("brightness", x))
        cv2.createTrackbar("Contrast", self.adjustment_window, 0, 255, lambda x: self.adjust_cam_setting("contrast", x))
        cv2.createTrackbar("Saturation", self.adjustment_window, 0, 255, lambda x: self.adjust_cam_setting("saturation", x))
        cv2.createTrackbar("Gain", self.adjustment_window, 0, 255, lambda x: self.adjust_cam_setting("gain", x))
        cv2.createTrackbar("Hue", self.adjustment_window, 0, 255, lambda x: self.adjust_cam_setting("hue", x))
        cv2.createTrackbar("Sharpness", self.adjustment_window, 0, 255, lambda x: self.adjust_cam_setting("sharpness", x))
        cv2.createTrackbar("White Balance", self.adjustment_window, 0, 255, lambda x: self.adjust_cam_setting("white_balance", x))
        cv2.waitKey(1)  # Brief pause to ensure window is ready

    def get_cam_defaults(self):
        self.focus_default = self.cap.get(cv2.CAP_PROP_FOCUS)
        self.exposure_default = self.cap.get(cv2.CAP_PROP_EXPOSURE)
        self.brightness_default = self.cap.get(cv2.CAP_PROP_BRIGHTNESS)
        self.contrast_default = self.cap.get(cv2.CAP_PROP_CONTRAST)
        self.saturation_default = self.cap.get(cv2.CAP_PROP_SATURATION)
        self.hue_default = self.cap.get(cv2.CAP_PROP_HUE)
        self.sharpness_default = self.cap.get(cv2.CAP_PROP_SHARPNESS)
        self.gain_default = self.cap.get(cv2.CAP_PROP_GAIN)
        self.white_balance_default = self.cap.get(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U)
        self.focus = self.cap.get(cv2.CAP_PROP_FOCUS)
        self.exposure = self.cap.get(cv2.CAP_PROP_EXPOSURE)
        self.brightness = self.cap.get(cv2.CAP_PROP_BRIGHTNESS)
        self.contrast = self.cap.get(cv2.CAP_PROP_CONTRAST)
        self.saturation = self.cap.get(cv2.CAP_PROP_SATURATION)
        self.hue = self.cap.get(cv2.CAP_PROP_HUE)
        self.sharpness = self.cap.get(cv2.CAP_PROP_SHARPNESS)
        self.gain = self.cap.get(cv2.CAP_PROP_GAIN)
        self.white_balance = self.cap.get(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U)
        #print a statement showing me the value for each of these now
        print(f"Focus: {self.focus_default}")
        print(f"Exposure: {self.exposure_default}")
        print(f"Brightness: {self.brightness_default}")
        print(f"Contrast: {self.contrast_default}")
        print(f"Saturation: {self.saturation_default}")
        print(f"Hue: {self.hue_default}")
        print(f"Sharpness: {self.sharpness_default}")
        print(f"Gain: {self.gain_default}")
        print(f"White Balance: {self.white_balance_default}")

    def adjust_cam_setting(self, setting: str, value: int):
        """Adjust a camera setting."""
        if self.cap:
            if setting == "focus":
                if value is None:
                    self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
                else:
                    self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
                    self.cap.set(cv2.CAP_PROP_FOCUS, value)
                    print(f"Focus set to: {self.cap.get(cv2.CAP_PROP_FOCUS)}")
            elif setting == "exposure":
                if value is None:
                    self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
                else:
                    self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
                    self.cap.set(cv2.CAP_PROP_EXPOSURE, value)
            elif setting == "brightness":
                if value is None:
                    self.cap.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
                else:
                    self.cap.set(cv2.CAP_PROP_BRIGHTNESS, value)
            elif setting == "contrast":
                if value is None:
                    self.cap.set(cv2.CAP_PROP_CONTRAST, self.contrast)
                else:
                    self.cap.set(cv2.CAP_PROP_CONTRAST, value)
            elif setting == "saturation":
                if value is None:
                    self.cap.set(cv2.CAP_PROP_SATURATION, self.saturation)
                else:
                    self.cap.set(cv2.CAP_PROP_SATURATION, value)
            elif setting == "gain":
                print('Setting gain is currently disabled')
                # self.cap.set(cv2.CAP_PROP_GAIN, value)
            elif setting == "hue":
                if value is None:
                    self.cap.set(cv2.CAP_PROP_HUE, self.hue)
                else:
                    self.cap.set(cv2.CAP_PROP_HUE, value)
            elif setting == "sharpness":
                if value is None:
                    self.cap.set(cv2.CAP_PROP_SHARPNESS, self.sharpness)
                else:
                    self.cap.set(cv2.CAP_PROP_SHARPNESS, value)
            elif setting == "white_balance":
                if value is None:
                    self.cap.set(cv2.CAP_PROP_AUTO_WB, 1.0)
                else:
                    self.cap.set(cv2.CAP_PROP_AUTO_WB, 0)
                    self.cap.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, value)
            time.sleep(0.5)

    def set_cam_defaults(self):
        """Set the camera to its default settings."""
        if self.cap:
            self.brightness = self.cap.get(cv2.CAP_PROP_BRIGHTNESS)
            self.contrast = self.cap.get(cv2.CAP_PROP_CONTRAST)
            self.saturation = self.cap.get(cv2.CAP_PROP_SATURATION)
            self.hue = self.cap.get(cv2.CAP_PROP_HUE)
            self.sharpness = self.cap.get(cv2.CAP_PROP_SHARPNESS)
            self.white_balance = self.cap.get(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U)

    def close_adjustment_window(self):
        """Close the camera adjustment window."""
        if self.adjustment_window:
            cv2.destroyWindow(self.adjustment_window)
            cv2.waitKey(1)  # Brief pause to ensure window closes
            self.adjustment_window = None

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
    
    def show_frame(self):
        """Display the frame in the feed window."""
        if self.show_annotations:
            frame = self.annotated_frame
        else:
            frame = self.frame
        
        cv2.imshow(self.window, frame)
        cv2.waitKey(1)  # Brief pause to ensure window displays

    def close_window(self):
        """Close the feed window."""
        if self.window:
            cv2.destroyWindow(self.window)
            cv2.waitKey(1)  # Brief pause to ensure window closes
            self.window = None

    def open_video_writer(self, video_path: Path, fps=30.0):
        """Start recording video to the specified file path."""
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        self.out = cv2.VideoWriter(str(video_path), fourcc, fps, (self.frame.shape[1], self.frame.shape[0]))

    def write_video_frame(self):
        """Write the current frame to the video file."""
        if self.out is not None:
            if self.save_annotations:
                frame = self.annotated_frame
            else:
                frame = self.frame
            self.out.write(frame)

    def close_video_writer(self):
        """Stop recording video."""
        if self.out is not None:
            self.out.release()
            self.out = None

    def save_video(self, video_path: Path, fps: float):
        """Save the recorded video to the specified file path."""
        # print(f"Number of frames: {len(self.images)}")
        if len(self.images) > 0:
            self.open_video_writer(video_path, fps)
            for frame in self.images:
                self.out.write(frame)
            self.close_video_writer()
            self.images = []
            self.annotated = []

    def destroy(self):
        """Clean up resources."""
        if self.window is not None:
            self.close_window()
        if self.cap is not None:
            self.close_source()
        if self.out is not None:
            self.close_video_writer()

    def capture_frame(self):
        """Capture a single frame from the feed."""
        ret, frame = self.cap.read()
        if not ret:
            self.frame = None
            self.annotated_frame = None
            return ret, None
        self.frame = frame.copy()
        self.annotated_frame = frame.copy()
        self.images.append(self.frame)
        return ret, self.frame
    
    def append_annotated_frame(self):
        """Append the current annotated frame to the annotated frames list."""
        self.annotated.append(self.annotated_frame)

    def add_bounding_box(self, bounding_box, color=(0, 255, 0), thickness=2):
        """Add a bounding box to the frame."""
        if bounding_box is None:
            return self.annotated_frame
        (x1, y1, x2, y2), confidence = bounding_box
        cv2.rectangle(self.annotated_frame, (x1, y1), (x2, y2), color, thickness)
        cv2.rectangle(self.annotated_frame, (x1, y1), (x2, y2), color, thickness)
        # Add confidence score with background
        text = f'{confidence:.2f}'
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        font_thickness = 1
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        text_x, text_y = x1, y1 - 10
        cv2.rectangle(self.annotated_frame, (text_x, text_y - text_size[1] - 5), (text_x + text_size[0] + 5, text_y + 5), color, -1)
        cv2.putText(self.annotated_frame, text, (text_x + 2, text_y - 2), font, font_scale, (255, 255, 255), font_thickness)
        return self.annotated_frame
    
    def add_dice_bounding_box(self, bounding_box):
        color = (0, 255, 0)  # Green for dice
        thickness = 2
        self.annotated_frame = self.add_bounding_box(bounding_box, color, thickness)
        return self.annotated_frame
    
    def add_pip_bounding_boxes(self, pip_bounding_boxes):
        color = (255, 0, 0)  # Blue for pips
        thickness = 2
        for box in pip_bounding_boxes:
            self.annotated_frame = self.add_bounding_box(box, color, thickness)
        return self.annotated_frame

    def add_border_details(self, dice: Dice, pips: int, border_size=400):
        """
        Add a padding border to the left side of the image frame.
        This border can be used to display additional information related to the frame.
        """
        height, width, channels = self.annotated_frame.shape
        new_width = width + border_size
        bordered_frame = np.zeros((height, new_width, channels), dtype=self.annotated_frame.dtype)
        bordered_frame[:, border_size:] = self.annotated_frame

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

        self.annotated_frame = bordered_frame
        return self.annotated_frame

    def wait(self, wait_ms=0):
        """Wait for a specified delay in milliseconds."""
        return cv2.waitKey(wait_ms)

    def save_image(self, img_path):
        """Save the given image frame to the specified file path."""
        if self.save_annotations:
            frame = self.annotated_frame
        else:
            frame = self.frame

        path = f"{img_path}"
        cv2.imwrite(path, frame)
        if self.logging:
            print(f"Image saved to {path}")
        return path

