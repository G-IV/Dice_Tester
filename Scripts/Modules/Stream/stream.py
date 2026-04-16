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

    def _open_window(self):
        """Open a window to display the feed."""
        if self.logging:
            print("stream.py _open_window() Opening feed window...")
        window_name = 'Die Tester - Camera Feed'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.waitKey(1)  # Brief pause to ensure window displays
        if self.logging:
            print("  -> Feed window opened.")
        return window_name
    
    def destroy(self):
        """Close the feed window."""
        if self.logging:
            print("stream.py destroy() Closing feed window...")
        if hasattr(self, 'window') and self.window:
            cv2.destroyAllWindows()
            cv2.waitKey(1)  # Brief pause to ensure window closes
            self.window = None
        if self.logging:
            print("  -> Feed window closed.")

    def show_frame(self, frame: MatLike, delay: int = 1):
        """Display the frame in the feed window."""
        if self.logging:
            print("stream.py show_frame() Displaying frame...")
        if self.window is None:
            if self.logging:
                print("  -> No window found. Opening new window...")
            self.window = self._open_window()
        
        if frame is None:
            raise ValueError("No frame to display.")
        cv2.imshow(self.window, frame)
        cv2.waitKey(delay)  # Brief pause to ensure window displays
        if self.logging:
            print("  -> Frame displayed.")