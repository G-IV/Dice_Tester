from pathlib import Path
from cv2.typing import MatLike
from ultralytics import YOLO
from abc import ABC, abstractmethod
from Scripts.Modules.Data import project_data

class Analyzer(ABC):
    """
    Analyze frames from the feed to detect dice and count pips.
    """
    
    def __init__(
            self, 
            data: project_data.ProjectData,
            logging: bool = False
            ):
        self.logging = logging
        self.open_model(data.model_path)
        self.frame = None
        self.img_analysis = None
        self.dice_value = None
        self.data = data

    def open_model(self, model_path):
        """Load the YOLO model for dice detection."""
        if self.logging:
            print(f"Loading model from {model_path}")
        self.model = YOLO(model_path)

    def load_image(self, frame: MatLike):
        if self.logging:
            print("Loading frame for analysis.")
        self.frame = frame

    def analyze_frame(self):
        if self.logging:
            print("Running model inference on frame.")
        self.data.add_analysis_results(self.model(self.frame))
    
    # TODO: Delete the code below once it is implemented in other locations
    ''' Older tools
    def count_dice(self):
        """Count the number of dice detected in the frame."""
        if self.logging:
            print("Getting dice qty found in analysis.")
        dice_key = self.get_class_key_for_value('Dice')
        img_annotations = self.get_img_annotations()
        dice_count = img_annotations.count(dice_key)
        if self.logging:
            print(f"Dice count: {dice_count}")
        return dice_count

    def get_class_key_for_value(self, value: str):
        """
        Reviews the model's class names to find the key for a given class value.
        """
        if self.logging:
            print(f"Finding class key for value: {value}")
        image_classes = self.img_analysis.names
        dice_key = list(image_classes.keys())[list(image_classes.values()).index(value)]
        if self.logging:
            print(f"Class key for value '{value}': {dice_key}")
        return dice_key
    
    def get_img_classes(self):
        """Return the class names from the image analysis."""
        if self.logging:
            print("Getting class names from image analysis.")
        return self.img_analysis.names
    
    def get_img_annotations(self):
        """Return the bounding box annotations from the image analysis."""
        if self.logging:
            print("Getting bounding box annotations from image analysis.")
        return self.img_analysis.boxes.cls.to(int).tolist()

    @abstractmethod
    def dice_value(self):
        """Implement how to get the dice value in child classes."""
        if self.logging:
            print("Getting dice value from image analysis, should be implemented in child class.")
        pass

    @abstractmethod
    def get_value_bounding_boxes(self):
        """Implement how to get the bounding boxes in child classes."""
        if self.logging:
            print("Getting value bounding boxes from image analysis, should be implemented in child class.")
        pass
    
    def get_dice_bounding_box(self):
        """Get the bounding box of the detected die."""
        if self.logging:
            print("Getting bounding box for detected die.")
        dice_key = self.get_class_key_for_value('Dice')
        class_mask = (self.img_analysis.boxes.cls == dice_key) # Class of 0 is die, 1 is pip
        box_index = class_mask.nonzero()
        if box_index.numel() != 1:
            return None  # No die detected
        x1, y1, x2, y2 = self.img_analysis.boxes.xyxy[box_index].cpu().numpy().astype(int)[0][0]
        confidence = self.img_analysis.boxes.conf[box_index].cpu().numpy().astype(float)[0][0]
        if self.logging:
            print(f"Bounding box for detected die: (x1: {x1}, y1: {y1}, x2: {x2}, y2: {y2}), confidence: {confidence}")
        return (x1, y1, x2, y2), confidence

    def get_dice_center_coordinates(self):
        """Get the center coordinates of the detected die."""
        if self.logging:
            print("Getting center coordinates for detected die.")
        dice_key = self.get_class_key_for_value('Dice')
        class_mask = (self.img_analysis.boxes.cls == dice_key) # Class of 0 is die, 1 is pip
        box_index = class_mask.nonzero()
        if box_index.numel() != 1:
            return None  # No die detected
        x, y, _, _ = self.img_analysis.boxes.xywh[box_index].cpu().numpy().astype(int)[0][0]
        if self.logging:
            print(f"Center coordinates for detected die: (x: {x}, y: {y})")
        return (x, y)

'''