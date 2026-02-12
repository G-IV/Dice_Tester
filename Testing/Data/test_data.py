from Scripts.Modules.Analyzers.analyzer import Analyzer
from Scripts.Modules.Data.pips_by_count import PipsByCount
from Scripts.Modules.Data.pips_by_pattern import PipsByPattern
from pathlib import Path
import cv2

# TODO: There is a way using the pytest directory thingy to load the data I want instead of making all these constants
IMAGE_PATH_PIPS_BY_COUNT = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Testing/Test_Data/pip_counting/00a214e5-20260204_104306_67_frame0014.jpg')
MODEL_PATH_PIP_BY_COUNT = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Testing/Test_Data/pip_counting/pip_counter.pt')
IMAGE_PATH_PIPS_BY_PATTERN = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Testing/Test_Data/pips_by_pattern/a11eb304-20260207_160654_165_frame0016.jpg')
MODEL_PATH_PIP_BY_PATTERN = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Testing/Test_Data/pips_by_pattern/pips_by_pattern.pt')
ENABLE_LOGGING = True
# Project Data relies on a previous analysis to populate its attributes

def test_text_value_to_int():
    data = PipsByPattern(model_path=MODEL_PATH_PIP_BY_PATTERN, logging=ENABLE_LOGGING)  # Create a mock or real ProjectData instance as needed
    analyzer = Analyzer(data=data, logging=ENABLE_LOGGING)
    image = cv2.imread(str(IMAGE_PATH_PIPS_BY_PATTERN))  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.load_image(image)  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.analyze_frame()  # Run analysis to populate the data object with

    assert data.text_value_to_int('one') == 1  # Test conversion of 'one' to 1
    assert data.text_value_to_int('two') == 2  # Test conversion of 'two' to 2
    assert data.text_value_to_int('three') == 3  # Test conversion of 'three' to 3
    assert data.text_value_to_int('four') == 4  # Test conversion of 'four' to 4
    assert data.text_value_to_int('five') == 5  # Test conversion of 'five' to 5
    assert data.text_value_to_int('six') == 6  # Test conversion of 'six' to 6
    assert data.text_value_to_int('seven') is None  # Test conversion of an invalid value returns None

def test_add_analysis_results():
    data = PipsByCount(model_path=MODEL_PATH_PIP_BY_COUNT, logging=ENABLE_LOGGING)  # Create a mock or real ProjectData instance as needed
    analyzer = Analyzer(data=data, logging=ENABLE_LOGGING)
    image = cv2.imread(str(IMAGE_PATH_PIPS_BY_COUNT))  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.load_image(image)  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.analyze_frame()  # Run analysis to populate the data object with

    assert data.analysis is not None  # Check if analysis results are stored correctly
    assert data.summary is not None  # Check if summary is generated
    assert data.categories is not None  # Check if categories are populated
    assert data.found_classes is not None  # Check if found classes are populated

def test_class_key_lookup_by_value():
    data = PipsByCount(model_path=MODEL_PATH_PIP_BY_COUNT, logging=ENABLE_LOGGING)  # Create a mock or real ProjectData instance as needed
    analyzer = Analyzer(data=data, logging=ENABLE_LOGGING)
    image = cv2.imread(str(IMAGE_PATH_PIPS_BY_COUNT))  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.load_image(image)  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.analyze_frame()  # Run analysis to populate the data object with

    assert data.class_key_lookup_by_value('Dice') == 0  # Test lookup for 'Dice'
    assert data.class_key_lookup_by_value('Pip') == 1  # Test lookup for 'Pip'
    assert data.class_key_lookup_by_value('nonexistent') is None  # Test lookup for a non-existent class

def test_get_qty_class_is_found():
    data = PipsByCount(model_path=MODEL_PATH_PIP_BY_COUNT, logging=ENABLE_LOGGING)  # Create a mock or real ProjectData instance as needed
    analyzer = Analyzer(data=data, logging=ENABLE_LOGGING)
    image = cv2.imread(str(IMAGE_PATH_PIPS_BY_COUNT))  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.load_image(image)  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.analyze_frame()  # Run analysis to populate the data object with

    assert data.get_qty_class_is_found('Dice') == 1  # Test quantity of 'die' found
    assert data.get_qty_class_is_found('Pip') == 5  # Test quantity of 'pip' found
    assert data.get_qty_class_is_found('nonexistent') == 0  # Test quantity for a non-existent class

def test_found_dice_qty():
    data = PipsByCount(model_path=MODEL_PATH_PIP_BY_COUNT, logging=ENABLE_LOGGING)  # Create a mock or real ProjectData instance as needed
    analyzer = Analyzer(data=data, logging=ENABLE_LOGGING)
    image = cv2.imread(str(IMAGE_PATH_PIPS_BY_COUNT))  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.load_image(image)  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.analyze_frame()  # Run analysis to populate the data object with

    assert data.found_dice_qty() == 1  # Test quantity of dice found using the specific method

def test_dice_center_coordinates():
    data = PipsByCount(model_path=MODEL_PATH_PIP_BY_COUNT, logging=ENABLE_LOGGING)  # Create a mock or real ProjectData instance as needed
    analyzer = Analyzer(data=data, logging=ENABLE_LOGGING)
    image = cv2.imread(str(IMAGE_PATH_PIPS_BY_COUNT))  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.load_image(image)  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.analyze_frame()  # Run analysis to populate the data object with

    center_coordinates = data.dice_center_coordinates()
    assert center_coordinates is not None  # Check if center coordinates are calculated correctly

def test_dice_value():
    data = PipsByCount(model_path=MODEL_PATH_PIP_BY_COUNT, logging=ENABLE_LOGGING)  # Create a mock or real ProjectData instance as needed
    analyzer = Analyzer(data=data, logging=ENABLE_LOGGING)
    image = cv2.imread(str(IMAGE_PATH_PIPS_BY_COUNT))  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.load_image(image)  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.analyze_frame()  # Run analysis to populate the data object with

    pip_count = data.dice_value()
    assert pip_count == 5  # Check if the pip count is correct based on the test image

def test_dice_value():
    data = PipsByPattern(model_path=MODEL_PATH_PIP_BY_PATTERN, logging=ENABLE_LOGGING)  # Create a mock or real ProjectData instance as needed
    analyzer = Analyzer(data=data, logging=ENABLE_LOGGING)
    image = cv2.imread(str(IMAGE_PATH_PIPS_BY_PATTERN))  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.load_image(image)  # Load a test image (replace with an actual valid path to an image for real testing)
    analyzer.analyze_frame()  # Run analysis to populate the data object with

    pip_value = data.dice_value()
    assert pip_value == 6  # Check if the pip value is None based on the test image
