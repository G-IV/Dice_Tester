# Project module imports
from Scripts.Modules.Data.project_data import ProjectData

# Class suport imports
from abc import ABC, abstractmethod
from dataclasses import dataclass

# Image processing imports
import cv2

class CVConfig(frozen=True):
    """Configuration parameters for image markups."""
    box_color: tuple = (0, 255, 0)  # Green color for bounding boxes
    text_color: tuple = (255, 255, 255)  # White color for text
    fontface: int = cv2.FONT_HERSHEY_SIMPLEX
    font_scale: float = 0.6
    thickness: int = 2

class Annotator(ABC):
    """Abstract base class for annotators."""
    def __init__(
            self, 
            data: ProjectData,
            logging: bool = False,
        ) -> None:
        self.data: ProjectData = data
        self.logging: bool = logging
