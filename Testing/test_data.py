from Scripts.Modules.Data import project_data, pips_by_count, pips_by_pattern
from Scripts.Modules.Analyzers import analyzer
import pytest
from unittest.mock import MagicMock
from pathlib import Path
import cv2

class TestProjectData:
    def test_results_are_added_and_verified(self, yolo_results, pips_by_count_test_constants):
        # Create an instance of ProjectData
        """
        I know I'm not supposed to do it this way, but I need a whole results instance and I have no idea how to create one without doing this.
        """
        detective = analyzer.Analyzer(pips_by_count_test_constants["model_path"], data=pips_by_count.ProjectData())
        frame = cv2.imread(str(pips_by_count_test_constants["test_image_path"]))
        detective.data.set_frame(frame)
        detective.analyze_frame()
        results = detective.data.analysis
        """
        I'm done cheating... One day, I'll figure out a better approach to this.
        """

        assert detective.data.analysis, "Object should not be empty"
        assert detective.data.analysis.summary() == yolo_results["summary"], "Summary should match expected results"
        assert detective.data.analysis.boxes.cls.numpy().tolist() == yolo_results["categories"], "Categories should match expected results"
        assert detective.data.analysis.names == yolo_results["names"], "Names should match expected results"
        