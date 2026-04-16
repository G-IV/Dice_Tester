# Project module imports
from Scripts.Modules.Feed.feed import Feed
from Scripts.Modules.Data.project_data import ProjectData

# Data type imports
from pathlib import Path

# Image handling imports
import cv2

class FeedVideo(Feed):

    def __init__(
            self,
            data: ProjectData,
            video_path: Path,
            logging: bool = False
        ) -> None:
        
        super().__init__(
            logging=logging
        )
        self.data = data
        self.video_path = video_path
        self.cap = None
        self.frame_count = 0
        self.fps = 0.0
        self.current_index = 0
        self._open_source() # Open the video file.
        self._capture_frame() # Load the first frame.
        

    def _open_source(self):
        self.cap = cv2.VideoCapture(str(self.video_path))
        if not self.cap.isOpened():
            raise ValueError(f"Failed to open video file: {self.video_path}")
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if self.frame_count <= 0:
            raise ValueError(f"Video has no frames: {self.video_path}")

    def _read_frame_at(self, frame_index: int):
        if self.cap is None or not self.cap.isOpened():
            raise ValueError("Video source is not opened.")

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = self.cap.read()
        if not ret or frame is None:
            raise ValueError(f"Failed to read frame {frame_index} from video: {self.video_path}")
        return frame

    def _capture_frame(self):
        frame = self._read_frame_at(self.current_index)
        self.data.clear_frames()
        self.data.new_frame(frame)

    def next_frame(self):
        """Move to the next frame if possible."""
        if self.current_index >= self.frame_count - 1:
            return False
        self.current_index += 1
        self._capture_frame()
        return True

    def previous_frame(self):
        """Move to the previous frame if possible."""
        if self.current_index <= 0:
            return False
        self.current_index -= 1
        self._capture_frame()
        return True

    def current_frame_number(self) -> int:
        """Return current frame number (1-based)."""
        return self.current_index + 1

    def total_frames(self) -> int:
        """Return total number of frames in the video."""
        return self.frame_count

    def close(self):
        """Release underlying video resources."""
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()