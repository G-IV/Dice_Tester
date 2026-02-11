"""
This module will build on the analyzer module to analyze dice with pips by analyzing the pattern of the pips.
"""

from . import Analyzer
from pathlib import Path

MODEL_PATH = Path('./Models/pips_by_pattern.pt')

class PipsByPattern(Analyzer):

    def __init__(self):
        super().__init__(model = MODEL_PATH)

    def dice_value(self):
        # TODO: Get a list of keys that aren't 'Dice'
        available_class_names = self.get_img_classes()
        pip_keys = [key for key, value in available_class_names.items() if value != 'Dice']
        img_annotations = self.get_img_annotations()
        pip_counts = {available_class_names[key]: img_annotations.count(key) for key in pip_keys}
        print("Pip counts by pattern:", pip_counts)
        pass

    def get_value_bounding_boxes(self):
        # TODO: This will be just a single bounding box, hopefully
        pass

    pass