from Scripts.Modules.Feed.feed import Feed
from Scripts.Modules.Data.project_data import ProjectData
from pathlib import Path
import cv2
from cv2.typing import Matlike

class ImageFeed(Feed):
    '''
    A class for processing images of dice rolls.
    '''
    def __init__(
            self, 
            image_path: Path, 
            logging: bool = False,
            data: ProjectData = None,
        ) -> None:
        super().__init__(
            logging=logging,
            data=data
        )
        self.image_path: Path = image_path

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
