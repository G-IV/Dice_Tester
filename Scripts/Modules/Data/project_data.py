# Parallel processing related imports
from multiprocessing import Queue

# Class support imports
from abc import ABC, abstractmethod

# Data type imports
from cv2.typing import MatLike
from ultralytics.engine.results import Results
from pathlib import Path

# Image processing imports
from ultralytics import YOLO

# Project module imports
from Scripts.Modules.queue_data import QueueData, Command as QuCmd

class ProjectData(ABC):

    def __init__(self,
            process_queue: Queue,
            logging: bool = False,
            model_path: Path | None = None
        ) -> None:

        self.logging = logging # Log to console if True, otherwise be silent.
        self.model_path = model_path # Path to the model weights file, if applicable.
        self.process_queue = process_queue # External queue for processing commands, if applicable.

        self.fps: int | None = None # Store the frames per second of the camera feed, if applicable.
        
        # Stores frame data
        self.frames: list[MatLike] = [] # List to hold captured frames.
        self.results: list[Results] = [] # List to hold results from the model.

    def clear_frames(self) -> None:
        """Clear the stored frames and results."""
        if self.logging:
            print("project_data.py clear_frames() Clearing frames and results.")
        self.frames.clear()
        self.results.clear()
        if self.logging:
            print("  -> Frames and results cleared.")

    def new_frame(self, frame: MatLike) -> None:
        """Add a new frame to the stored frames."""
        if self.logging:
            print("project_data.py new_frame() Adding new frame.")
        self.frames.append(frame)
        if self.logging:
            print("  -> New frame added.")

    def new_result(self, result: Results) -> None:
        """Add a new result to the stored results."""
        if self.logging:
            print("project_data.py new_result() Adding new result.")
        self.results.append(result)
        if self.logging:
            print("  -> New result added.")
