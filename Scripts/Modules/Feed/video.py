# Parallel processing related imports
import asyncio

# Project module imports
from Scripts.Modules.Feed.feed import Feed
from Scripts.Modules.Data.project_data import ProjectData

# Data type imports
from pathlib import Path
from cv2.typing import MatLike

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
        self._open_source() # Open the video file.
        asyncio.create_task(self._video_loop()) # Start the video loop to capture frames.
        

    def _open_source(self):
        self.cap = cv2.VideoCapture(str(self.video_path))
        if not self.cap.isOpened():
            raise ValueError(f"Failed to open video file: {self.video_path}")
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if self.logging:
            print(f"Opened video: {self.video_path.name} with expected length {self.frame_count / self.fps} seconds")

    def _capture_frame(self):
        if self.cap is None or not self.cap.isOpened():
            raise ValueError("Video source is not opened.")
        ret, frame = self.cap.read()
        if not ret:
            self.cap.release()  # Release the video capture if we can't read a frame
            return
        self.data.process_new_frame(frame)
        if self.logging:
            print(f"Captured new frame from video")

    async def _video_loop(self):
        while self.cap.isOpened():
            self._capture_frame()
            await asyncio.sleep(1 / self.fps)  # Sleep to maintain the video's frame rate