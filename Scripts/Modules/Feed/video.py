from Scripts.Modules.Annotators import annotate
from Scripts.Modules.Data import project_data
from Scripts.Modules.Feed import feed
import cv2

from pathlib import Path
import time

class Feed(feed.Feed):
    '''
    A class for processing video feeds of dice rolls.
    '''
    def __init__(
            self,
            annotator: annotate.Annotator,
            data: project_data.ProjectData,
            video_path: Path, 
            auto_play: bool = True,
            logging: bool = False,
        ) -> None:
        super().__init__(
            annotator=annotator,
            data=data, 
            logging=logging
        )
        self.auto_play = auto_play
        self.cap = None
        self.video_path = video_path
        self.processed_frames: list = []
        self.open_source()
        
        if self.logging:
            print(f"Initialized Video Feed with video path: {self.video_path}")

    def open_source(self):
        """Open feed to video file"""
        self.cap = cv2.VideoCapture(str(self.video_path))
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video source: {self.video_path}")
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.current_frame_index = 0
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if self.logging:
            print(f"Opened video source: {self.video_path}")

    def capture_frame(self):
        """Capture a frame from the video feed."""
        if self.cap is None:
            raise ValueError("Video source is not opened.")
        ret, frame = self.cap.read()
        self.frame_captured_time = time.perf_counter()
        # TODO: return the frame, since we'll be using multiprocessing and we can't update the data object in the main process from a Pool
        # self.data.set_frame(frame)
        if not ret:
            raise ValueError("Could not read frame from video source.")
        if self.logging:
            print(f"Captured frame {self.current_frame_index + 1}/{self.frame_count} from video.")
        return frame
        
    def perf_counter(self):
        """In lieu of importing time everywhere I need this for managing when capture_frame is called, I'll just add this as a function call"""
        return time.perf_counter()
    
    def elapsed_time_since_last_capture(self):
        """Calculate the elapsed time since the last frame was captured."""
        if self.frame_captured_time is None:
            return None
        return time.perf_counter() - self.frame_captured_time
    
    def wait_for_fps_interval(self):
        """Wait for the appropriate amount of time to maintain the video's FPS."""
        if self.fps is None or self.fps <= 0:
            raise ValueError("Invalid FPS value. Cannot wait for FPS interval.")
        elapsed_time = self.elapsed_time_since_last_capture()
        if elapsed_time is None:
            return
        frame_rate_interval = 1000 / self.fps # Convert FPS to milliseconds per frame
        elapsed_time_ms = elapsed_time * 1000 # Convert to milliseconds
        time_to_wait = max(1, frame_rate_interval - elapsed_time_ms) # Ensure we wait at least 1 ms to allow for window events
        if self.logging:
            print(f"Elapsed time since last capture: {elapsed_time_ms:.2f} ms, waiting for: {time_to_wait:.2f} ms to maintain FPS of {self.fps:.2f}")
        return self.wait(int(time_to_wait))

    def destroy(self):
        """Clean up resources."""
        if self.cap is not None:
            self.cap.release()
        super().destroy()