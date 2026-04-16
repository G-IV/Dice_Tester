# Project module imports
from Scripts.Modules.Feed.feed import Feed
from Scripts.Modules.Data.project_data import ProjectData

# Data type imports
from pathlib import Path

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
        """Load all supported image files from this folder and its subfolders."""
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
        self.image_paths = sorted(
            [
                p
                for p in self.folder_path.rglob("*")
                if p.is_file() and p.suffix.lower() in supported_formats
            ]
        )
        if not self.image_paths:
            raise ValueError(f"No supported image files found in folder: {self.folder_path}")

    def _capture_frame(self):
        if (self.current_index >= len(self.image_paths)) or (self.current_index < 0):
            raise IndexError(f"Index out of bounds: {self.current_index} for image paths of length {len(self.image_paths)}")
        
        image_path = self.image_paths[self.current_index]
        frame = cv2.imread(str(image_path))
        if frame is None:
            raise ValueError(f"Failed to load image from path: {image_path}")

        # Keep only the currently selected image frame in this viewer flow.
        self.data.clear_frames()
        self.data.new_frame(frame)

    def current_image_path(self) -> Path:
        """Return the file path of the currently loaded image."""
        return self.image_paths[self.current_index]

    def next_image(self):
        """Load the next image in the folder."""
        if self.current_index >= len(self.image_paths) - 1:
            return False
        self.current_index += 1
        self._capture_frame()
        return True

    def previous_image(self):
        """Load the previous image in the folder."""
        if self.current_index <= 0:
            return False
        self.current_index -= 1
        self._capture_frame()
        return True