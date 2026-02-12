"""
This module will build on the analyzer module to analyze dice with pips by counting individual pips.
"""
from Scripts.Modules.Analyzers.analyzer import Analyzer
from Scripts.Modules.Data.project_data import ProjectData
from pathlib import Path

MODEL_PATH = Path('./Models/pip_counter.pt')

class PipCounterAnalyzer(Analyzer):

    def __init__(
            self, 
            data: ProjectData,
            logging: bool = False
        ):
        super().__init__(
            data=data,
            logging=logging
        )

    def dice_value(self):
        """Count the number of pips detected in the frame."""
        pip_key = self.get_class_key_for_value('Pip')
        img_annotations = self.get_img_annotations()
        pip_count = img_annotations.count(pip_key)
        return pip_count
    
    def get_value_bounding_boxes(self):
        """Get the bounding boxes of the detected pips."""
        pip_key = self.get_class_key_for_value('Pip')
        class_mask = (self.img_analysis.boxes.cls == pip_key) # Class of 0 is die, 1 is pip
        box_indices = class_mask.nonzero()
        if box_indices.numel() == 0:
            return []  # No pips detected
        bounding_boxes = []
        print("Number of pips detected:", box_indices.numel())
        for index in box_indices:
            x1, y1, x2, y2 = self.img_analysis.boxes.xyxy[index].cpu().numpy().astype(int)[0]
            confidence = self.img_analysis.boxes.conf[index].cpu().numpy().astype(float)[0]
            area = (x2 - x1) * (y2 - y1)
            bounding_boxes.append(((x1, y1, x2, y2), confidence))
        return bounding_boxes

    pass