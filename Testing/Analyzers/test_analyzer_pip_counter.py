from pyparsing import Path
import pytest
from Scripts.Modules.Analyzers.pip_counter import PipCounterAnalyzer
from Scripts.Modules.Data.pip_counter_data import PipCounterData
import cv2

# I'm going to need data for testing, so I'll need mock data.  It is easier to just import some photos + a working model for each dice type than to try to mimic the results data object.
IMAGE_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Testing/Test_Data/pip_counting/00a214e5-20260204_104306_67_frame0014.jpg')
MODEL_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Testing/Test_Data/pip_counting/pip_counter.pt')

# Test what happens if I try to open the model with an invalid path.
def test_open_model_with_invalid_path():
    invalid_model_path = Path('invalid/path/to/model.pt')
    data = PipCounterData(model_path=invalid_model_path)  # Create a mock or real ProjectData instance as needed
    with pytest.raises(Exception):
        test_analyzer = PipCounterAnalyzer(data=data, logging=True)

def test_open_model_with_valid_path():
    data = PipCounterData(model_path=MODEL_PATH)  # Create a mock or real ProjectData instance as needed
    analyzer_instance = PipCounterAnalyzer(data=data, logging=True)
    assert analyzer_instance.model is not None

def test_load_image():
    data = PipCounterData(model_path=MODEL_PATH)  # Create a mock or real ProjectData instance as needed
    analyzer_instance = PipCounterAnalyzer(data=data, logging=True)
    
    # Load a test image (replace with an actual valid path to an image for real testing)
    test_image = cv2.imread(str(IMAGE_PATH))
    
    analyzer_instance.load_image(test_image)
    
    assert isinstance(analyzer_instance.frame, type(test_image))  # Check if the frame is loaded correctly

def test_analyze_frame():
    data = PipCounterData(model_path=MODEL_PATH)  # Create a mock or real ProjectData instance as needed
    analyzer_instance = PipCounterAnalyzer(data=data, logging=True)
    
    # Load a test image (replace with an actual valid path to an image for real testing)
    test_image = cv2.imread(str(IMAGE_PATH))
    
    analyzer_instance.load_image(test_image)
    analyzer_instance.analyze_frame(test_image)
    
    assert len(analyzer_instance.data.analysis) == 1  # Check if the analysis results are stored in the data object