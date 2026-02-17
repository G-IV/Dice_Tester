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
            image_path: Path, 
            logging: bool = False,
            data: project_data.ProjectData = None,
        ) -> None:
        super().__init__(
            logging=logging,
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
        self.frame = cv2.imread(str(self.image_path))
        if self.frame is None:
            raise ValueError(f"Could not open image source: {self.image_path}")
        if self.logging:
            print(f"Opened image source: {self.image_path}")
