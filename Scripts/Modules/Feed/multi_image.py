from Scripts.Modules.Feed.feed import Feed
from Scripts.Modules.Feed.image import ImageFeed
from Scripts.Modules.Data.project_data import ProjectData
from pathlib import Path
import cv2

class MultiImageFeed(Feed):
    '''
    A class for processing multiple images of dice rolls.
    '''
    def __init__(
            self, 
            folder_path: Path, 
            logging: bool = False,
            data: ProjectData = None,
        ) -> None:
        super().__init__(
            logging=logging,
            data=data
        )
        self.folder: Path = folder_path
        self.compile_image_list()

    def compile_image_list(self):
        """Compile a list of image file paths from the specified folder."""
        supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
        list_of_image_paths = [self.folder / f for f in self.folder.iterdir() if f.suffix.lower() in supported_formats]
        if len(list_of_image_paths) == 0:
            raise ValueError(f"No supported image files found in folder: {self.folder}")
        self.current_index = 0  # Reset index to start of the list
        self.images = [ImageFeed(image_path=path, logging=self.logging, data=self.data) for path in list_of_image_paths]       
        if self.logging:
            print(f"Compiled list of images: {self.images}")

    def load_current_image(self):
        """Load the current image based on the current index."""
        if self.logging:
            print(f"Loading image at index {self.current_index} from list of images.")
        image_feed = self.images[self.current_index]
        image_feed.open_source()

    def load_next_image(self):
        """Load the next image in the list."""
        self.next_index()
        self.load_current_image()

    def load_previous_image(self):
        """Load the previous image in the list."""
        self.previous_index()
        self.load_current_image()

    def next_index(self):
        """Load the next image in the list."""
        self.current_index = min(len(self.images) - 1, self.current_index + 1)  # Ensure we don't go beyond the last index
        if self.logging:
            print(f"Moved index up: {self.current_index}")

    def previous_index(self):
        """Load the previous image in the list."""
        self.current_index = max(0, self.current_index - 1)  # Ensure we don't go below 0
        if self.logging:
            print(f"Moved index down: {self.current_index}")
