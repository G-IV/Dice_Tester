"""
This should be the one stop shop for project data
There is a chance that the Dice class will be subsumed by this?

https://docs.ultralytics.com/reference/engine/results/#ultralytics.engine.results.BaseTensor.to

To gain more insight into the results object, you can run 'breakdown_model_results.py' found in the Shorties folder.
"""

from abc import ABC, abstractmethod
import numpy as np
from numpy.typing import NDArray
from cv2.typing import MatLike
from ultralytics.engine.results import Results
from multiprocessing.queues import Queue as MPQueue
from queue import Queue
from threading import Thread

class ProjectData(ABC):
    """
    A class to manage all project data, including dice information, analysis results, and database interactions.
    """
    def __init__(
            self,
            logging: bool = False,
            main_queue: MPQueue | None = None
        ):
        self.analysis = {}
        self.categories = None
        self.found_classes = None
        self.frame: MatLike | None = None
        self.frame_buffer: list[MatLike] = []
        self.dice_center_coordinates_buffer: list[NDArray] = []
        self.annotated_frame: MatLike | None = None
        self.logging = logging
        self.summary = None
        # frame monitoring thread setup
        self.stop_frame_thread = False # Flag to signal the thread to stop
        self.frame_queue = Queue(maxsize=5) # Create a queue to hold captured frames
        self.frame_monitor_thread = Thread(target=self.frame_monitoring)
        self.frame_monitor_thread.start()
        # Frame to communicate with main
        self.main_queue = main_queue
        if self.logging:
            print(f"Initialized ProjectData")

    def add_analysis_results(self, analysis_results: list[Results]):
        """Add analysis results to the project data."""
        if self.logging:
            print("Adding analysis results to project data.")
        self.analysis = analysis_results[0]
        self.summary = analysis_results[0].summary()
        self.categories = analysis_results[0].names
        self.found_classes = analysis_results[0].boxes.cls.numpy()
        self.set_annotated_frame(self.frame.copy())
        self.append_dice_position_to_buffer()

    def set_frame(self, frame: MatLike):
        """Sets the most recent frame in the project & appends it to the frame buffer."""
        self.frame = frame
        self.frame_buffer.append(frame)

    def append_frame_to_buffer(self, frame: MatLike):
        """Append a frame to the frame buffer.  Should be used in Feed classes when a new frame is captured."""
        self.frame_buffer.append(frame)

    def append_dice_position_to_buffer(self):
        """Append the center position of the detected dice to the buffer in the Dice class."""
        # There can be frames with no dice, in that scenario, there aren't any found_classes.
        if self.found_classes is not None and self.categories is not None:
            dice_id = self.class_key_lookup_by_value('Dice')
            # TODO: Figure out how to handle multiple dice being found - there should only be one, but sometimes the model finds more than one.
            if dice_id is not None and np.count_nonzero(self.found_classes == dice_id) == 1:
                boxes = self.analysis.boxes
                target_boxes = boxes[boxes.cls == dice_id]
                center_coordinates = target_boxes.xywh.cpu().numpy()[:2]  # Retrieve the first 2 values return by xywh
                if self.logging:
                    print(f"Appending center coordinates {center_coordinates} to buffer.")
                # Here you would append the center coordinates to the Dice class buffer.  This is a bit of a band-aid solution, but it should work for now.  In the future, we can implement a more robust solution that can handle multiple dice and track them across frames.
                self.dice_center_coordinates_buffer.append(center_coordinates)
            else:
                if self.logging:
                    print(f"Found {np.count_nonzero(self.found_classes == dice_id)} dice. Unable to determine center coordinates with certainty.")
        else:
            if self.logging:
                print("No classes found in analysis results. Unable to determine center coordinates.")

    def set_annotated_frame(self, annotated_frame: MatLike):
        """Set the current annotated frame in the project data."""
        self.annotated_frame = annotated_frame

    def class_key_lookup_by_value(self, value: str) -> int | None:
        """
        Reviews the model's class names to find the key for a given class value.
        """
        for key, val in self.categories.items():
            if val == value:
                return key
        return None

    def get_qty_class_is_found(self, cls: str) -> int:
        """Return the quantity of dice detected in the current analysis."""
        cls_key = self.class_key_lookup_by_value(cls)
        print(f"Found classes type: {type(self.found_classes)}, value: {self.found_classes}")
        if self.found_classes is not None and cls_key is not None:
            return np.count_nonzero(self.found_classes == cls_key)
        return 0
    
    def found_dice_qty(self) -> int:
        """Return the quantity of dice detected in the current analysis."""
        dice_qty = self.get_qty_class_is_found('Dice')
        if self.logging:
            print(f"Getting quantity of dice found in current analysis.: {dice_qty}")
        return dice_qty
    
    def dice_center_coordinates(self):
        """Return the center coordinates of the detected dice."""
        # If there are 0 dice or more than 1, return None since we can't be sure which one to use for the center coordinates.  This is a bit of a band-aid solution, but it should work for now.  In the future, we can implement a more robust solution that can handle multiple dice and track them across frames.
        dice_qty = self.found_dice_qty()
        if dice_qty != 1:
            print(f"Found {dice_qty} dice. Unable to determine center coordinates with certainty.")
            return None
        dice_id = self.class_key_lookup_by_value('Dice')
        boxes = self.analysis.boxes #Makes it easier to read the code below
        # Get corresponding index of where dice_key is found in cls
        target_boxes = boxes[boxes.cls == dice_id]
        print("Target boxes for dice:", target_boxes.xywh.cpu().numpy())
        if self.logging:
            print(f"Found {target_boxes.shape[0]} boxes for dice with class ID {dice_id}.")
        return target_boxes.xywh.cpu().numpy()  # Assuming this returns center coordinates

    def text_value_to_int(self, text_value: str) -> int | None:
        """Convert a textual representation of a number to an integer."""
        text_to_int_map = {
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
            'six': 6
        }
        return text_to_int_map.get(text_value.lower(), None)

    def get_dice_bounding_boxes(self):
        """Return the bounding boxes of the detected dice."""
        dice_id = self.class_key_lookup_by_value('Dice')
        boxes = self.analysis.boxes
        target_boxes = boxes[boxes.cls == dice_id]
        return target_boxes.xyxy.cpu().numpy().astype(int)  # Assuming this returns bounding box coordinates

    def clear_buffers(self):
        """Clear the frame buffer and dice position buffer."""
        self.frame_buffer.clear()
        self.dice_center_coordinates_buffer.clear()

    def frame_monitoring(self):
        """Continuously monitor the frame queue for new frames and update the project data accordingly."""
        if self.logging:
            print("Starting frame monitoring thread (parent).")
        while not self.stop_frame_thread:
            item = self.frame_queue.get()
            if item['type'] == 'New Frame': # As of now, this is the only thing that should come into this queue.  But I figure that could change, so this is a bit of future-proofing.  Or overkill, up to how you see it, I guess.
                frame = item['data']
                self.set_frame(frame)
                self.main_queue.put({'type': 'New Frame', 'data': frame}) # Send a message to the main thread that a new frame has been received and processed
                if self.logging:
                    print("Received new frame from queue and updated project data (parent).")
            else: 
                print("... uh, what?")

    def destroy(self):
        """Clean up any resources used by the project data."""
        if self.logging:
            print("Destroying ProjectData and cleaning up resources.")
        self.clear_buffers()
        self.stop_frame_thread = True

    @abstractmethod
    def dice_value(self):
        """Return value of the dice."""
        pass