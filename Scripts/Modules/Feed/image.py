from Scripts.Modules.Annotators import annotate
from Scripts.Modules.Feed import feed
from Scripts.Modules.Data import project_data
from pathlib import Path
import cv2

class Feed(feed.Feed):
    '''
    A class for processing images of dice rolls.
    '''
    def __init__(
            self, 
            annotator: annotate.Annotator,
            data: project_data.ProjectData, 
            image_path: Path,
            logging: bool = False,
        ) -> None:
        super().__init__(
            logging=logging,
            annotator=annotator,
            data=data
        )
        self.image_path: Path = image_path
        
        if self.logging:
            print(f"Initialized Image Feed with image path: {self.image_path}")

    def open_source(self):
        """No source to capture, use capture frame directly with image path"""
        pass

    def capture_frame(self):
        """Open the feed source based on the feed type."""
        frame = cv2.imread(str(self.image_path))
        if frame is None:
            raise ValueError(f"Could not open image source: {self.image_path}")
        if self.logging:
            print(f"Opened image source: {self.image_path}")
        self.data.set_frame(frame)

    def show_image_and_wait(self, delay: int = 0):
        """Display the image in the feed window."""
        self.capture_frame()
        self.show_frame(delay)

    def show_annotated_frame_and_wait(self, delay: int = 0):
        """Display the annotated frame in the feed window."""
        self.show_annotated_frame(delay)
