'''
This script will handle the vision processing tasks, utilizing Ultralyitic's YOLO model.
1) Monitor a video feed from a connected camera.
3) Detect and identify dice within the video frames.
4) Detect when dice are in motion after the motor has turned the tower.
5) Detect when dice have come to rest and capture their final positions.
6) Count the number of pips on the die and determine the bottom face value.
7) The user should see a window displaying the state of the dice (Not found, In Motion, At Rest).  When at rest, teh window should also display the detected bottom face value.  When dice are not found, the user should be prompted to adjust the camera or dice position.
'''
from Scripts.Modules.Data import project_data
from Scripts.Modules.Annotators import annotate
from abc import ABC, abstractmethod
import cv2
from cv2.typing import MatLike
from matplotlib.pyplot import box
import numpy as np
from enum import Enum
from pathlib import Path

class Feed(ABC):

    def __init__(
            self,
            annotator: annotate.Annotator,
            data: project_data.ProjectData,
            logging: bool = False
        ):
        """
        Docstring for __init__
        
        : param annotator: The annotator object responsible for drawing annotations on frames.
        : type annotator: Annotator
        : param data: The project data object containing all relevant data for the project, including model information and analysis results.
        : type data: ProjectData
        : param logging: Whether to print logging information to the console.
        : type logging: bool
        """
        self.annotator = annotator
        self.data = data
        self.logging = logging
        self.window = None

        # ================== START Video Writer Properties ==================
        self.out = None
        self.images = []
        self.annotated = []
        # ================== END Video Writer Properties ==================

        if self.logging:
            print(f"Initialized Feed")

    @abstractmethod
    def open_source(self):
        """Open the feed source based on the feed type."""
        print("Different sources are handled differently, child classes should implement this method.")
        pass

    @abstractmethod
    def capture_frame(self):
        """Capture a single frame from the feed."""
        pass
    
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
            cv2.waitKey(1)  # Brief pause to ensure window closes
            self.window = None
    
    def show_frame(self, delay: int = 1):
        """Display the frame in the feed window."""
        if self.window is None:
            self.window = self.open_window()
        
        if self.data.frame is None:
            raise ValueError("Frame is not set. Please capture a frame before trying to display it.")
        cv2.imshow(self.window, self.data.frame)
        cv2.waitKey(delay)  # Brief pause to ensure window displays

    @abstractmethod
    def show_annotated_frame(self, **args):
        """Display the annotated frame in the feed window."""
        pass

    def destroy(self):
        """Clean up resources"""
        if self.window is not None:
            self.close_window()


# ================== START Image Annotation Methods ==================
    # TODO: Maybe just have a single method that draws all the bounding boxes and details?
    # Or should I move annotations to dice-specific feed class since they are so specific to the dice testing use case?
    # TODO: Refactor to use new setup.
    # def add_bounding_box(self, bounding_box, color=(0, 255, 0), thickness=2):
    #     """Add a bounding box to the frame."""
    #     if bounding_box is None:
    #         return self.annotated_frame
    #     (x1, y1, x2, y2), confidence = bounding_box
    #     cv2.rectangle(self.annotated_frame, (x1, y1), (x2, y2), color, thickness)
    #     cv2.rectangle(self.annotated_frame, (x1, y1), (x2, y2), color, thickness)
    #     # Add confidence score with background
    #     text = f'{confidence:.2f}'
    #     font = cv2.FONT_HERSHEY_SIMPLEX
    #     font_scale = 0.6
    #     font_thickness = 1
    #     text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
    #     text_x, text_y = x1, y1 - 10
    #     cv2.rectangle(self.annotated_frame, (text_x, text_y - text_size[1] - 5), (text_x + text_size[0] + 5, text_y + 5), color, -1)
    #     cv2.putText(self.annotated_frame, text, (text_x + 2, text_y - 2), font, font_scale, (255, 255, 255), font_thickness)
    #     return self.annotated_frame
    '''
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
'''

# ================== END Image Annotation Methods ==================


    # TODO: Make a save_annated and save_image, instead of chosing between them here.
    # I'm not even sure why I would want to save the annoated version.
    # Hell, I'm only using this when I want to manually capture more images for making a model.
    def save_image(self, img_path):
        """Save the given image frame to the specified file path."""
        path = f"{img_path}"
        cv2.imwrite(path, self.frame)
        if self.logging:
            print(f"Image saved to {path}")
        return path
    
    def save_annotated_image(self, img_path):
        """Save the given annotated image frame to the specified file path."""
        path = f"{img_path}"
        cv2.imwrite(path, self.annotated_frame)
        if self.logging:
            print(f"Annotated image saved to {path}")
        return path

    def wait(self, wait_ms=0):
        """Wait for a specified delay in milliseconds."""
        return cv2.waitKey(wait_ms)


    # ================== START Video Writer Methods ==================
    # TODO: Move video writing to a different class that is called seperately
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

   # TODO: Why am I doing this?! -> Oh, this is for saving the frames to a video later
    def append_annotated_frame(self):
        """Append the current annotated frame to the annotated frames list."""
        self.annotated.append(self.annotated_frame) 

    # ================== END Video Writer Methods ==================

    
    
    

    



