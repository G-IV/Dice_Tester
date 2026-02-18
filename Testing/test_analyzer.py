from Scripts.Modules.Analyzers import analyzer
from Scripts.Modules.Data import pips_by_count as pips_by_count_data
from pathlib import Path
import pytest
import cv2


class TestAnalyzerWithPipsByCount:

    def test_model_path_fail(self, lazy_shared_datadir):
        # Bad model path
        model_path = lazy_shared_datadir / "model.pt"
        with pytest.raises(FileNotFoundError, match=r".*Model file not found at.*"):
            analyzer.Analyzer(model_path, data=pips_by_count_data.ProjectData())

    # def test_model_path_pass(self, model_path, lazy_shared_datadir):
    def test_model_path_success(self, model_path):
        detective = analyzer.Analyzer(model_path, data=pips_by_count_data.ProjectData())

        # Check that the model is loaded (in this case, just check that it's not None)
        assert detective.model is not None

    def test_analyze_image(self, pips_by_count_test_constants):
        detective = analyzer.Analyzer(pips_by_count_test_constants["model_path"], data=pips_by_count_data.ProjectData())
        frame = cv2.imread(str(pips_by_count_test_constants["test_image_path"]))
        detective.data.set_frame(frame)
        # Analyze the image
        detective.analyze_frame()

        # Check that results is a list and contains at least one result
        results = detective.data.analysis

        # Check that the first result has the expected attributes
        first_result = results[0]
        assert hasattr(first_result, "names")
        assert hasattr(first_result, "boxes")