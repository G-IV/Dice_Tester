from Scripts.Modules.Feed.feed import Feed
import cv2
import numpy as np
from cv2.typing import Matlike
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(frozen=True)
class CVConfig:
    """Configuration parameters for computer vision processing."""
    box_color: tuple = (0, 255, 0)  # Green color for bounding boxes
    text_color: tuple = (255, 255, 255)  # White color for text
    fontface: int = cv2.FONT_HERSHEY_SIMPLEX
    font_scale: float = 0.6
    thickness: int = 1

class Annotator(ABC):
    '''
    A class for annotating frames/images with detected dice and their values.
    '''
    def __init__(
            self, 
            logging: bool = False,
            feed: Feed = None
        ):
        self.logging = logging
        self.feed = feed
        self.annoated_frame: Matlike = None
        self.cv_config = CVConfig()

    def draw_bounding_box_and_label(self, box_coordinates: np.ndarray, label: str = None):
        """Draw a bounding box with a label on the annotated frame."""
        # Draw the bounding box
        x1, y1, x2, y2 = box_coordinates
        cv2.rectangle(
            self.annotated_frame, 
            (x1, y1), (x2, y2), 
            self.cv_config.box_color, 
            self.cv_config.thickness
        )

        if label is not None:
            # Draw a filled rectangle with the label text
            text_size = cv2.getTextSize(
                label, 
                self.cv_config.fontface, 
                self.cv_config.font_scale, 
                self.cv_config.thickness
            )[0]
            text_x, text_y = x1, y1 - 10
            cv2.rectangle(
                self.annotated_frame, 
                (text_x, text_y - text_size[1] - 5), 
                (text_x + text_size[0] + 5, text_y + 5), 
                self.cv_config.box_color, 
                cv2.FILLED
            )
            cv2.putText(
                self.annotated_frame, 
                label, 
                (text_x + 2, text_y - 2), 
                self.cv_config.fontface, 
                self.cv_config.font_scale, 
                self.cv_config.text_color, 
                self.cv_config.thickness
            )

    def append_details_area_to_frame(self):
        """I think this might vary dice type to dice type, so this may be another detail to add to dice."""
        if self.logging:
            print("Appending details area to annotated frame.")
        pass

    def annotate_die(self):
        """Place a single bounding box around a detected die and label it with the detected value."""
        if self.logging:
            print("Annotating frame with detected dice.")
        # Placeholder for annotation logic, which would use self.feed.data.analysis results to draw bounding boxes and labels on self.feed.frame
        pass

    def annotate_all_dice(self):
        """Place bounding boxes around all detected dice and label them with their detected values."""
        if self.logging:
            print("Annotating frame with all detected dice.")
        # Placeholder for annotation logic, which would use self.feed.data.analysis results to draw bounding boxes and labels on self.feed.frame
        pass