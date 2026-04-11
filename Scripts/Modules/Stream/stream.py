# Image support imports
import cv2

# Class support imports
from cv2.typing import MatLike

class Stream():

    def __init__(
            self,
            logging: bool = False
        ) -> None:
        self.logging = logging
        self.window = None
        # I'm not calling _open_window here because I want to delay opening the window until we have a frame to display.  This will prevent an empty window from appearing if whatever process I'm running doesn't need the window.

    def _open_window(self):
        """Open a window to display the feed."""
        window_name = 'Die Tester - Camera Feed'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.waitKey(1)  # Brief pause to ensure window displays
        return window_name
    
    def _close_window(self):
        """Close the feed window."""
        if hasattr(self, 'window') and self.window:
            cv2.destroyWindow(self.window)
            cv2.waitKey(1)  # Brief pause to ensure window closes
            self.window = None

    def show_frame(self, frame: MatLike, delay: int = 1):
        """Display the frame in the feed window."""
        if self.window is None:
            self.window = self._open_window()
        
        if frame is None:
            raise ValueError("No frame to display.")
        
        cv2.imshow(self.window, frame)
        cv2.waitKey(delay)  # Brief pause to ensure window displays

    def destroy(self):
        """Clean up resources"""
        self._close_window()