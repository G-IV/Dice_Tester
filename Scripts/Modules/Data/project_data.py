"""
This should be the one stop shop for project data
There is a chance that the Dice class will be subsumed by this?

https://docs.ultralytics.com/reference/engine/results/#ultralytics.engine.results.BaseTensor.to

To gain more insight into the results object, you can run 'breakdown_model_results.py' found in the Shorties folder.
"""

from pathlib import Path
from abc import ABC, abstractmethod
import numpy as np
class ProjectData(ABC):
    """
    A class to manage all project data, including dice information, analysis results, and database interactions.
    """
    def __init__(
            self,
            model_path: Path,
            logging: bool = False
        ):
        """
        Docstring for __init__
        
        :param self: Description
        :param model_path: The path to the folder containing the model and associated notes.json file
        :type model_path: Path
        """
        self.model_path = model_path
        self.logging = logging

        self.analysis = {}
        self.summary = None
        self.categories = None
        self.found_classes = None
        if self.logging:
            print(f"Initialized ProjectData with model path: {model_path}")

    def add_analysis_results(self, analysis_results: list):
        """Add analysis results to the project data."""
        if self.logging:
            print("Adding analysis results to project data.")
        self.analysis = analysis_results[0]
        self.summary = analysis_results[0].summary()
        self.categories = analysis_results[0].names
        self.found_classes = analysis_results[0].boxes.cls.numpy()

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

    @abstractmethod
    def dice_value(self):
        """Return value of the dice."""
        pass