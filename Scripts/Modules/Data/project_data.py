# Parallel processing related imports
from multiprocessing import Queue as mpQueue
from threading import Thread
from queue import Queue, Empty

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

class Command(Enum):
    EXIT = auto()
    FRAME = auto()

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
            main_queue: mpQueue,
            logging: bool = False,
            model_path: Path | None = None
        ) -> None:

        self.main_queue = main_queue # Pass data back to the main process.
        self.logging = logging # Log to console if True, otherwise be silent.
        self.model_path = model_path # Path to the model weights file, if applicable.

        # Stores frame data
        self.frames: list[MatLike] = [] # List to hold captured frames.
        self.results: list[Results] = [] # List to hold results from the model.
        
        # Threading and queue for processing data in the background.
        self.data_q = Queue()
        self.data_thread = Thread(target=self._data_control_loop, daemon=True)
        self.data_thread.start()

    def _new_frame(self, frame: MatLike) -> None:
        """Adds a new frame to the data queue for processing."""
        if self.logging:
            print(f"New frame added to data queue")
        self.frames.append(frame) # Add the new frame to the list of frames.
        if self.model_path is not None:
            if self.logging:
                print(f"Analyzing frame")
            model = YOLO(self.model_path) # Load the model.
            results = model(frame)[0] # Analyze the frame with the model.
            self.results.append(results) # Store the results.
            if self.logging:
                print(f"Frame analysis complete")
            # TODO: Add code here to create an annotated frame based on the results, and send that back to the main process instead of the original frame.
            annotated_frame = results.plot() # This is the easiest way to show the annotated frame, but I'm not sure if it's how I want to do it in the future.
            self.main_queue.put(QueueData(cmd=QuCmd.FRAME_READY, data=annotated_frame)) # Send the annotated frame back to the main process.
            return
        self.main_queue.put(QueueData(cmd=QuCmd.FRAME_READY, data=frame)) # If no model, just send the original frame back to the main process.

    def _data_control_loop(self) -> None:
        if self.logging:
            print("Starting data control loop...")

        while True:
            try:
                item = self.data_q.get(timeout=1) # Wait for a data item to process.
                match item.cmd:
                    case Command.EXIT:
                        if self.logging:
                            print("Exiting data control loop")
                        break
                    case Command.FRAME:
                        self._new_frame(item.data)
                    case _:
                        if self.logging:
                            print(f"Received unrecognized command in data control loop: {item}")
            except Empty:
                # This case handles the timeout exception, which we expect.
                continue
            except Exception as e:
                if self.logging:
                    print(f"Error in data control loop: {e}")
                break
        
        if self.logging:
            print("Data control thread exiting.")

    def new_frame(self, frame: MatLike) -> None:
        """Adds a new frame to the data queue for processing."""
        if self.logging:
            print(f"Adding new frame to data queue...")
        self.data_q.put(DataItem(cmd=Command.FRAME, data=frame))

    