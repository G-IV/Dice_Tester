from pathlib import Path
from xml.parsers.expat import model
from cv2.typing import MatLike
from ultralytics import YOLO
from abc import ABC, abstractmethod
from Scripts.Modules.Data import project_data
from threading import Thread

class Analyzer(ABC):
    """
    Analyze frames from the feed to detect dice and count pips.
    This will only work in non-multithreaded functions, because model = YOLO(MODEL) locks a thread?
    """
    
    def __init__(
            self, 
            model_path: Path,
            data: project_data.ProjectData,
            logging: bool = False,
            ):
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found at {model_path}")
        self.data = data
        self.logging = logging
        self.model_path = model_path
        self.open_model(model_path)
        if self.logging:
            print(f"Initialized Analyzer")

    def open_model(self, model_path: Path):
        """Load the YOLO model for dice detection."""
        if self.logging:
            print(f"Loading model from {model_path}")
        self.model = YOLO(model_path)

    def analyze_frame(self):
        if self.logging:
            print("Running model inference on frame.")
        results = self.model(self.data.frame)
        if self.logging:
            print(f"Analysis results: {results}")
        self.data.add_analysis_results(results)
