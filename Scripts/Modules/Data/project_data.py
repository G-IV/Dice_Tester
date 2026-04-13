# Parallel processing related imports
from multiprocessing import Queue as mpQueue

# Class support imports
from abc import ABC, abstractmethod
from enum import Enum, auto

# Data type imports
from cv2.typing import MatLike
from ultralytics.engine.results import Results
from pathlib import Path

# Image processing imports
from ultralytics import YOLO

# Project module imports
from Scripts.Modules.queue_data import QueueData, Command as QuCmd

# File saving imports
from datetime import datetime
import cv2

class Command(Enum):
    EXIT = auto()
    FRAME = auto()
    SAVE = auto()

class DataItem:
    """
    A simple data class to hold information about data items.
    Format:

        "cmd": "Command value",
        "data": "Associated data"

    The data can be just about anything, so I don't need to do any type enforcement.
    """
    def __init__(self, cmd: Command, data) -> None:
        self.cmd = cmd
        self.data = data

    def __repr__(self) -> str:
        return f"Data item: (cmd={self.cmd}, data={self.data})"

class ProjectData(ABC):

    def __init__(self,
            logging: bool = False,
            model_path: Path | None = None
        ) -> None:

        self.logging = logging # Log to console if True, otherwise be silent.
        self.model_path = model_path # Path to the model weights file, if applicable.

        self.fps: int | None = None # Store the frames per second of the camera feed, if applicable.
        
        # Stores frame data
        self.frames: list[MatLike] = [] # List to hold captured frames.
        self.results: list[Results] = [] # List to hold results from the model.

    def clear_frames(self) -> None:
        """Clear the stored frames and results."""
        self.frames.clear()
        self.results.clear()

    def process_new_frame(self, frame: MatLike) -> MatLike | None:
        """Add a new frame to the stored frames."""
        self.frames.append(frame)
        if self.model_path is not None:
            model = YOLO(self.model_path)
            results = model(frame, verbose=False)[0]
            self.results.append(results)
            return results.plot()
        return frame