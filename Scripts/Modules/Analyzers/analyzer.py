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
        self.data_queue = data.analyzer_queue # Use the analyzer queue from project data to share analysis results between threads
        self.logging = logging
        self.stop_thread = False # Flag to signal the thread to stop
        self.thread = Thread(target=self.monitor_analyzer_queue)
        self.thread.start()
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
        self.data_queue.put({
            'type': 'New Analysis',
            'data': results
        })  # Send analysis results to project data through the analyzer queue

    def monitor_analyzer_queue(self):
        """Monitor the analyzer queue for new analysis results and update project data."""
        if self.logging:
            print("Starting analyzer monitoring thread.")
        while self.stop_thread == False:
            try:
                message = self.data_queue.get(timeout=1)  # Wait for a new message with a timeout
                if message['type'] == 'New Frame':
                    self.analyze_frame()  # Run analysis on the new frame
                    if self.logging:
                        print("Updated project data with new analysis results from analyzer queue.")
            except Exception as e:
                continue  # Timeout occurred, loop back and check stop_thread flag

    def destroy(self):
        """Clean up resources and stop threads."""
        self.stop_thread = True  # Signal the thread to stop
        self.thread.join()  # Wait for the thread to finish
        if self.logging:
            print("Analyzer destroyed and monitoring thread stopped.")
