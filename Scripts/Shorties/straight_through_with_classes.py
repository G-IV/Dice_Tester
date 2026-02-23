from Scripts.Modules.Analyzers import analyzer as analyzer_module
from Scripts.Modules.Annotators.annotate_factory import AnnotateFactory
from Scripts.Modules.Feed.feed_factory import FeedFactory
from Scripts.Modules.Data.project_data_factory import ProjectDataFactory

from pathlib import Path
import numpy as np

# Just using the pips_by_count, since that is a known quantity
class StraightThrough:
    # Constants
    LOGGING = False
    MODEL_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Testing/data/pips_by_count/pips_by_count.pt')
    IMAGE_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Testing/data/pips_by_count/Images/lighted_blurry_4_0.jpg')
    IMAGE_FOLDER = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Testing/data/pips_by_count/Images')
    VIDEO_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Testing/data/pips_by_count/Video/lighted_blurry_3_to_1_roll.mp4')

    def __init__(self):
        self.data = None
        self.detective = None
        self.feed = None
        self.annotator = None
        pass

    def show_image(self):

        # Initialize components
        self.data = ProjectDataFactory.create_project_data(data_type="pips_by_count", logging=self.LOGGING)
        self.detective = analyzer_module.Analyzer(model_path=self.MODEL_PATH, data=self.data, logging=self.LOGGING)
        self.annotator = AnnotateFactory.create_annotator(annotator_type="pips_by_count", data=self.data, logging=self.LOGGING)
        self.feed = FeedFactory.create_feed(feed_type="image", image_path=self.IMAGE_PATH, annotator=self.annotator, data=self.data, logging=self.LOGGING)

        # Show image
        self.feed.show_image_and_wait(1500)
        # Analyze image
        self.detective.analyze_frame()
        # Show annotated image
        self.feed.show_annotated_frame_and_wait()
        # Clean up
        self.feed.destroy()

    def show_folder_of_images(self):

        # Initialize components
        self.data = ProjectDataFactory.create_project_data(data_type="pips_by_count", logging=self.LOGGING)
        self.detective = analyzer_module.Analyzer(model_path=self.MODEL_PATH, data=self.data, logging=self.LOGGING)
        self.annotator = AnnotateFactory.create_annotator(annotator_type="pips_by_count", data=self.data, logging=self.LOGGING)
        self.feed = FeedFactory.create_feed(feed_type="multi_image", folder_path=self.IMAGE_FOLDER, annotator=self.annotator, data=self.data, logging=self.LOGGING)

        for image in self.feed.images:
            # Show image
            image.show_image_and_wait(250)
            # Analyze image
            self.detective.analyze_frame()
            # Show annotated image
            image.show_annotated_frame_and_wait()

        # Clean up
        self.feed.destroy()

    def show_video(self):

        # Initialize components
        self.data = ProjectDataFactory.create_project_data(data_type="pips_by_count", logging=self.LOGGING)
        self.detective = analyzer_module.Analyzer(model_path=self.MODEL_PATH, data=self.data, logging=self.LOGGING)
        self.annotator = AnnotateFactory.create_annotator(annotator_type="pips_by_count", data=self.data, logging=self.LOGGING)
        self.feed = FeedFactory.create_feed(feed_type="video", video_path=self.VIDEO_PATH, annotator=self.annotator, data=self.data, logging=self.LOGGING)

        # Preprocess video, it should happen somewhat quickly?
        while True:
            try:
                self.feed.capture_frame()
            except ValueError:
                print("End of video reached or error capturing frame.")
                break
            self.detective.analyze_frame()
            self.feed.show_annotated_frame()
            if self.feed.wait_for_fps_interval() & 0xFF == ord('q'):
                continue

        self.feed.destroy()

    def live_stream(self):
        # Initialize components
        self.data = ProjectDataFactory.create_project_data(data_type="pips_by_count", logging=self.LOGGING)
        self.detective = analyzer_module.Analyzer(model_path=self.MODEL_PATH, data=self.data, logging=self.LOGGING)
        self.annotator = AnnotateFactory.create_annotator(annotator_type="pips_by_count", data=self.data, logging=self.LOGGING)
        self.feed = FeedFactory.create_feed(feed_type="cam", cam_index=0, annotator=self.annotator, data=self.data, logging=self.LOGGING)
        while True:
            try:
                self.feed.capture_frame()
            except ValueError as e:
                print(f"Error capturing frame: {e}")
                break
            self.detective.analyze_frame()
            self.feed.show_frame()
            if self.feed.wait_for_fps_interval() & 0xFF == ord('q'):
                continue

tester = StraightThrough()
# tester.show_image()
# tester.show_folder_of_images()
# tester.show_video()
# tester.live_stream()

