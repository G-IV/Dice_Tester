from Scripts.Modules.Data.pip_counter_data import PipCounterData
from Scripts.Modules.Analyzers.pip_counter import PipCounterAnalyzer
from pathlib import Path
import cv2

IMAGE_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Testing/Test_Data/pip_counting/00a214e5-20260204_104306_67_frame0014.jpg')
MODEL_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Testing/Test_Data/pip_counting/pip_counter.pt')
ENABLE_LOGGING = True
# Project Data relies on a previous analysis to populate its attributes
def test_add_analysis_results():
    data = PipCounterData(model_path=MODEL_PATH, logging=ENABLE_LOGGING)  # Create a mock or real ProjectData instance as needed
    analyzer = PipCounterAnalyzer(data=data, logging=ENABLE_LOGGING)
    image = cv2.imread(str(IMAGE_PATH))  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.load_image(image)  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.analyze_frame()  # Run analysis to populate the data object with

    assert data.analysis is not None  # Check if analysis results are stored correctly
    assert data.summary is not None  # Check if summary is generated
    assert data.categories is not None  # Check if categories are populated
    assert data.found_classes is not None  # Check if found classes are populated

def test_class_key_lookup_by_value():
    data = PipCounterData(model_path=MODEL_PATH, logging=ENABLE_LOGGING)  # Create a mock or real ProjectData instance as needed
    analyzer = PipCounterAnalyzer(data=data, logging=ENABLE_LOGGING)
    image = cv2.imread(str(IMAGE_PATH))  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.load_image(image)  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.analyze_frame()  # Run analysis to populate the data object with

    assert data.class_key_lookup_by_value('Dice') == 0  # Test lookup for 'Dice'
    assert data.class_key_lookup_by_value('Pip') == 1  # Test lookup for 'Pip'
    assert data.class_key_lookup_by_value('nonexistent') is None  # Test lookup for a non-existent class

def test_get_qty_class_is_found():
    data = PipCounterData(model_path=MODEL_PATH, logging=ENABLE_LOGGING)  # Create a mock or real ProjectData instance as needed
    analyzer = PipCounterAnalyzer(data=data, logging=ENABLE_LOGGING)
    image = cv2.imread(str(IMAGE_PATH))  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.load_image(image)  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.analyze_frame()  # Run analysis to populate the data object with

    assert data.get_qty_class_is_found('Dice') == 1  # Test quantity of 'die' found
    assert data.get_qty_class_is_found('Pip') == 5  # Test quantity of 'pip' found
    assert data.get_qty_class_is_found('nonexistent') == 0  # Test quantity for a non-existent class

def test_found_dice_qty():
    data = PipCounterData(model_path=MODEL_PATH, logging=ENABLE_LOGGING)  # Create a mock or real ProjectData instance as needed
    analyzer = PipCounterAnalyzer(data=data, logging=ENABLE_LOGGING)
    image = cv2.imread(str(IMAGE_PATH))  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.load_image(image)  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.analyze_frame()  # Run analysis to populate the data object with

    assert data.found_dice_qty() == 1  # Test quantity of dice found using the specific method

def test_dice_center_coordinates():
    data = PipCounterData(model_path=MODEL_PATH, logging=ENABLE_LOGGING)  # Create a mock or real ProjectData instance as needed
    analyzer = PipCounterAnalyzer(data=data, logging=ENABLE_LOGGING)
    image = cv2.imread(str(IMAGE_PATH))  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.load_image(image)  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.analyze_frame()  # Run analysis to populate the data object with

    center_coordinates = data.dice_center_coordinates()
    assert center_coordinates is not None  # Check if center coordinates are calculated correctly

def test_dice_value():
    data = PipCounterData(model_path=MODEL_PATH, logging=ENABLE_LOGGING)  # Create a mock or real ProjectData instance as needed
    analyzer = PipCounterAnalyzer(data=data, logging=ENABLE_LOGGING)
    image = cv2.imread(str(IMAGE_PATH))  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.load_image(image)  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.analyze_frame()  # Run analysis to populate the data object with

    pip_count = data.dice_value()
    assert pip_count == 5  # Check if the pip count is correct based on the test image