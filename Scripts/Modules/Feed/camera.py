# Parallel processing related imports
from threading import Thread
from queue import Queue

# Project module imports
from Scripts.Modules.Feed.feed import Feed
from Scripts.Modules.Data.project_data import ProjectData
from Scripts.Modules.queue_data import QueueData, Command as QuCmd

# Image handling support imports
import cv2

# Data type imports
# Class support imports

class FeedCamera(Feed):

    def __init__(
            self,
            data: ProjectData,
            process_queue: Queue, # I can't think of a way to make this an optional value when considering my approach to gathering frames from the camera feed.
            logging: bool = False
        ) -> None:
        
        super().__init__(logging=logging)
        self.data = data
        self.process_queue = process_queue
        self._open_source() # Open the camera feed.
        self.continue_thread = True # Flag to signal the capture thread to stop when we're done.
        self.capture_thread = Thread(target=self._capture_frame, daemon=True)
        self.capture_thread.start() # Start the thread to capture frames continuously.

    def _open_source(self):
        self.cap = cv2.VideoCapture(0)  # Open the default camera
        self.data.fps = self.cap.get(cv2.CAP_PROP_FPS)  # Get the frames per second of the camera feed.
        if not self.cap.isOpened():
            raise RuntimeError("Failed to open camera feed.")
        if self.logging:
            print("Camera feed opened successfully.")

    def _capture_frame(self):
        while self.continue_thread:
            ret, frame = self.cap.read()
            if not ret:
                raise RuntimeError("Failed to capture frame from camera feed.")
            if self.process_queue is not None:
                self.process_queue.put(QueueData(QuCmd.NEW_FRAME_CAPTURED, frame))
            if self.logging:
                print("Captured new frame from camera feed.")
        self.cap.release()  # Release the camera feed when we're done.

    def destroy(self) -> None:
        """Release the camera feed and clean up resources."""
        self.continue_thread = False  # Signal the capture thread to stop.
        if self.logging:
            print("Camera feed released.")
        self.capture_thread.join()  # Wait for the capture thread to finish before exiting.
        if self.logging:
            print("Camera feed destroyed.")

