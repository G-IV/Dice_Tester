from Scripts.Modules.Feed import feed
from Scripts.Modules.Data import project_data
import cv2

from pathlib import Path

class Feed(feed.Feed):
    '''
    A class for processing video feeds of dice rolls.
    '''
    def __init__(
            self, 
            video_path: Path, 
            auto_play: bool = False,
            data: project_data.ProjectData = None,
            logging: bool = False,
        ) -> None:
        super().__init__(
            data=data, 
            logging=logging
        )
        self.auto_play = auto_play
        self.cap = None
        self.current_frame_index = 0
        self.frame_count = 0
        self.fps = 0
        self.video_path: Path = video_path
        self.open_source()
        
        if self.logging:
            print(f"Initialized Video Feed with video path: {self.video_path}")

    def open_source(self):
        """Open the feed source based on the feed type."""
        self.cap = cv2.VideoCapture(str(self.video_path))
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video source: {self.video_path}")
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if self.logging:
            print(f"Opened video source: {self.video_path}")

    def capture_frame(self):
        """Capture a frame from the video feed."""
        if self.cap is None:
            raise ValueError("Video source is not opened.")
        ret, self.frame = self.cap.read()
        if not ret:
            raise ValueError("Could not read frame from video source.")
        
    def next_index(self):
        """Move to the next frame index."""
        self.current_frame_index = min(self.frame_count - 1, self.current_frame_index + 1)
        self.set_frame_index()
        if self.logging:
            print(f"Moved to next frame index: {self.current_frame_index}")

    def previous_index(self):
        """Move to the previous frame index."""
        self.current_frame_index = max(0, self.current_frame_index - 1)
        self.set_frame_index()
        if self.logging:
            print(f"Moved to previous frame index: {self.current_frame_index}")

    def set_frame_index(self, index: int = None):
        """Set the current frame index."""
        if index is not None:
            self.current_frame_index = index
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_index)

    def get_next_frame(self):
        """Get the next frame from the video feed."""
        self.next_index()
        self.capture_frame()

    def get_previous_frame(self):
        """Get the previous frame from the video feed."""
        self.previous_index()
        self.capture_frame()