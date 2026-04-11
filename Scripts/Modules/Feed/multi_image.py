# Project module imports
from Scripts.Modules.Feed.feed import Feed
from Scripts.Modules.Data.project_data import ProjectData

# Data type imports
from pathlib import Path
from cv2.typing import MatLike

# Image handling imports
import cv2

class FeedMultiImage(Feed):

    def __init__(
            self,
            data: ProjectData,
            folder_path: Path,
            logging: bool = False
        ) -> None:
        
        super().__init__(logging=logging)
        self.data = data
        self.folder_path = folder_path
        self.current_index = 0
        self._open_source() # Load the image paths from the folder.
        self._capture_frame() # Load the first image.

    def _open_source(self):
        """Using this to load up an array with the path to each image in the folder."""
        supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
        self.image_paths = sorted([p for p in self.folder_path.iterdir() if p.suffix.lower() in supported_formats])
        if not self.image_paths:
            raise ValueError(f"No supported image files found in folder: {self.folder_path}")

    def _capture_frame(self):
        if (self.current_index >= len(self.image_paths)) or (self.current_index < 0):
            raise IndexError(f"Index out of bounds: {self.current_index} for image paths of length {len(self.image_paths)}")
        
        image_path = self.image_paths[self.current_index]
        frame = cv2.imread(str(image_path))
        if frame is None:
            raise ValueError(f"Failed to load image from path: {image_path}")
        
        self.data.new_frame(frame)

    def next_image(self):
        """Load the next image in the folder."""
        self.current_index += 1
        if self.current_index < len(self.image_paths):
            self.current_index = len(self.image_paths) - 1 # Ensure we don't go out of bounds.
        self._capture_frame()
        if self.logging:
            print(f"Loaded next image")

    def previous_image(self):
        """Load the previous image in the folder."""
        self.current_index -= 1
        if self.current_index < 0:
            self.current_index = 0 # Ensure we don't go out of bounds.
        self._capture_frame()
        if self.logging:
            print(f"Loaded previous image")