# Class support imports
from abc import ABC, abstractmethod

# CV2 imports
import cv2
from cv2.typing import MatLike

class Feed(ABC):

    def __init__(
            self,
            logging: bool = False
        ) -> None:

        self.logging = logging
        self.window = None

    @abstractmethod
    def _open_source(self) -> None:
        """Open the feed source based on the feed type."""
        pass

    @abstractmethod
    def _capture_frame(self) -> None:
        """Capture a single frame from the feed."""
        pass