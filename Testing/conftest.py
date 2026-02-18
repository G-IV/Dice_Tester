import pytest
"""
==============================================================
Model & image paths.
==============================================================
"""
@pytest.fixture(scope="function", name="model_path")
def fixture_model_paths(lazy_shared_datadir):
    """This should only be used by the test_analyzer module, as it provides paths to the model files."""
    return lazy_shared_datadir / "pips_by_count/pips_by_count.pt"

@pytest.fixture(scope="function", name="image_path")
def fixture_image_paths(lazy_shared_datadir):
    """This should only be used by the test_analyzer module, as it provides paths to the image files."""
    return lazy_shared_datadir / "pips_by_count/Images/lighted_blurry_4_0.jpg"

@pytest.fixture(scope="function", name="pips_by_count_test_constants")
def fixture_pips_by_count_test_constants(lazy_shared_datadir):
    return {
        "model_path": lazy_shared_datadir / "pips_by_count/pips_by_count.pt",
        "test_image_path": lazy_shared_datadir / "pips_by_count/Images/lighted_blurry_4_0.jpg",
        "image_folder_path": lazy_shared_datadir / "pips_by_count/Images",
        "video_folder_path": lazy_shared_datadir / "pips_by_count/Videos"
    }

"""
==============================================================
YOLO results data.
==============================================================
"""
@pytest.fixture(scope="function", name="yolo_results")
def fixture_yolo_results():
    """
    Constants derived from:
    Model: /Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Testing/data/pips_by_count/pips_by_count.pt
    Image: /Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Testing/data/pips_by_count/Images/lighted_blurry_4_0.jpg
    File running them: /Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Scripts/Shorties/breakdown_model_results.py
    Date: 2026-02-17
    """
    # Let's just assume that if summary exists, then the results exist
    summary = [{'name': 'Dice', 'class': 0, 'confidence': 0.91286, 'box': {'x1': 937.01709, 'y1': 388.68921, 'x2': 1181.93433, 'y2': 635.31415}}, {'name': 'Pip', 'class': 1, 'confidence': 0.82672, 'box': {'x1': 1037.80017, 'y1': 538.41309, 'x2': 1072.73425, 'y2': 571.81519}}, {'name': 'Pip', 'class': 1, 'confidence': 0.7997, 'box': {'x1': 997.54675, 'y1': 488.0827, 'x2': 1031.9696, 'y2': 521.02295}}, {'name': 'Pip', 'class': 1, 'confidence': 0.75649, 'box': {'x1': 1089.12744, 'y1': 496.68579, 'x2': 1123.88953, 'y2': 530.76904}}, {'name': 'Pip', 'class': 1, 'confidence': 0.7376, 'box': {'x1': 1048.15332, 'y1': 447.67575, 'x2': 1081.89514, 'y2': 480.88385}}]
    categories = [0, 1, 1, 1, 1]
    names = {0: 'Dice', 1: 'Pip'}
    return {
        "summary": summary,
        "categories": categories,
        "names": names
    }