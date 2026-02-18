from Scripts.Modules.Data import pips_by_count as pips_by_count_data
from Scripts.Modules.Analyzers import analyzer as analyzer_module
from Scripts.Modules.Feed import image as image_feed
from Scripts.Modules.Annotators import pips_by_count as annotate

from pathlib import Path
import numpy as np

# Just using the pips_by_count, since that is a known quantity
class StraightThrough:
    # Constants
    LOGGING = False
    MODEL_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Testing/data/pips_by_count/pips_by_count.pt')
    IMAGE_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Testing/data/pips_by_count/Images/lighted_blurry_4_0.jpg')
    VIDEO_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Testing/data/pips_by_count/Video/lighted_blurry_3_to_1_roll.mp4')

    def __init__(self):
        self.data = None
        self.detective = None
        self.feed = None
        self.annotator = None
        pass

    def show_image(self):

        # Initialize components
        self.data = pips_by_count_data.ProjectData(logging=self.LOGGING)
        self.detective = analyzer_module.Analyzer(model_path=self.MODEL_PATH, data=self.data, logging=self.LOGGING)
        self.annotator = annotate.Annotator(data=self.data, logging=self.LOGGING)
        self.feed = image_feed.Feed(image_path=self.IMAGE_PATH, annotator=self.annotator, data=self.data, logging=self.LOGGING)

        # Show image
        self.feed.show_image_and_wait(1500)
        # Analyze image
        self.detective.analyze_frame()
        # Show annotated image
        self.feed.show_annotated_frame_and_wait()
        # Clean up
        self.destroy()

    def show_folder_of_images(self):
        pass

    def destroy(self):
        self.feed.destroy()

tester = StraightThrough()
# tester.show_image()
tester.show_folder_of_images()

