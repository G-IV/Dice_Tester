# Project module imports
from Scripts.Modules.Feed.feed import Feed
from Scripts.Modules.Data.project_data import ProjectData

# Data type imports
from pathlib import Path

# Image handling imports
import cv2

class FeedImage(Feed):

    def __init__(
            self,
            data: ProjectData,
            image_path: Path,
            logging: bool = False
        ) -> None:
        
        super().__init__(logging=logging)
        self.data = data
        # We can just load the image right away.
        self._capture_frame(image_path)

    def _open_source(self):
        """We don't use this since we are loading an image"""
        pass

    def _capture_frame(self, image_path: Path):
        frame = cv2.imread(str(image_path))
        if frame is None:
            raise ValueError(f"Failed to load image from path: {image_path}")
        self.data.process_new_frame(frame)