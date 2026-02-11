from pathlib import Path
from cv2.typing import MatLike
from ultralytics import YOLO
from abc import ABC, abstractmethod

class Analyzer(ABC):
    """
    Analyze frames from the feed to detect dice and count pips.
    """
    
    def __init__(
            self, model: Path,
            logging: bool = False
            ):
        self.logging = logging
        self.model = self.open_model(model)
        self.frame = None
        self.img_analysis = None
        self.dice_value = None

    def open_model(self, model_path):
        """Load the YOLO model for dice detection."""
        self.model = YOLO(model_path)
        if self.logging:
            print(f"Model loaded from {model_path}")
        return self.model

    def load_image(self, frame: MatLike):
        self.frame = frame
        self.analyze_frame(self.frame)

    def analyze_frame(self, frame):
        analysis = self.model(frame)
        self.img_analysis = analysis[0]
    
    def count_dice(self):
        """Count the number of dice detected in the frame."""
        dice_key = self.get_class_key_for_value('Dice')
        img_annotations = self.get_img_annotations()
        dice_count = img_annotations.count(dice_key)
        return dice_count

    def get_class_key_for_value(self, value: str):
        """
        Reviews the model's class names to find the key for a given class value.
        """
        image_classes = self.img_analysis.names
        dice_key = list(image_classes.keys())[list(image_classes.values()).index(value)]
        return dice_key
    
    def get_img_classes(self):
        """Return the class names from the image analysis."""
        return self.img_analysis.names
    
    def get_img_annotations(self):
        """Return the bounding box annotations from the image analysis."""
        return self.img_analysis.boxes.cls.to(int).tolist()

    @abstractmethod
    def dice_value(self):
        """Implement how to get the dice value in child classes."""
        pass

    @abstractmethod
    def get_value_bounding_boxes(self):
        """Implement how to get the bounding boxes in child classes."""
        pass
    
    def get_dice_bounding_box(self):
        """Get the bounding box of the detected die."""
        dice_key = self.get_class_key_for_value('Dice')
        class_mask = (self.img_analysis.boxes.cls == dice_key) # Class of 0 is die, 1 is pip
        box_index = class_mask.nonzero()
        if box_index.numel() != 1:
            return None  # No die detected
        x1, y1, x2, y2 = self.img_analysis.boxes.xyxy[box_index].cpu().numpy().astype(int)[0][0]
        confidence = self.img_analysis.boxes.conf[box_index].cpu().numpy().astype(float)[0][0]
        return (x1, y1, x2, y2), confidence

    def get_dice_center_coordinates(self):
        """Get the center coordinates of the detected die."""
        dice_key = self.get_class_key_for_value('Dice')
        class_mask = (self.img_analysis.boxes.cls == dice_key) # Class of 0 is die, 1 is pip
        box_index = class_mask.nonzero()
        if box_index.numel() != 1:
            return None  # No die detected
        x, y, _, _ = self.img_analysis.boxes.xywh[box_index].cpu().numpy().astype(int)[0][0]
        return (x, y)
