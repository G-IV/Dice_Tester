# Parallel processing related imports
from threading import Thread
from queue import Queue

# Project module imports
from Scripts.Modules.Feed.feed import Feed
from Scripts.Modules.Data.project_data import ProjectData

# Image handling support imports
import cv2

# Data type imports
# Class support imports

class FeedCamera(Feed):

    def __init__(
            self,
            data: ProjectData,
            logging: bool = False
        ) -> None:
        
        super().__init__(logging=logging)
        self.data = data
        self._open_source() # Open the camera feed.
        self.capture_thread = Thread(target=self._capture_frame, daemon=True)
        self.capture_thread.start() # Start the thread to capture frames continuously.

    def _open_source(self):
        self.cap = cv2.VideoCapture(0)  # Open the default camera
        if not self.cap.isOpened():
            raise RuntimeError("Failed to open camera feed.")
        if self.logging:
            print("Camera feed opened successfully.")

    def _capture_frame(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                raise RuntimeError("Failed to capture frame from camera feed.")
            self.data.new_frame(frame)
            if self.logging:
                print("Captured new frame from camera feed.")

    def destroy(self) -> None:
        """Release the camera feed and clean up resources."""
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
            if self.logging:
                print("Camera feed released.")
        super().destroy()  # Call the base class destroy to close the window