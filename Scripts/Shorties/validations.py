"""
The initial purpose of this module is to put together the sizes of the dice & pip boxes to help weed out invalid detections.
"""

from Scripts.Modules import vision
import statistics
from pathlib import Path

IMG_SAVE_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Cross_Bars/2_Label_Studio/1_Images/Train')

MODEL = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Scripts/Testing/3_Model/best.pt')

def gather_box_data(analyzer, num_frames=100):
    """Gather box size data over a number of frames for analysis."""
    dice_boxes = []
    pip_boxes = []

    image_files = sorted([f for f in IMG_SAVE_PATH.iterdir() if f.suffix.lower() in ['.jpg', '.jpeg', '.png']])

    analyzer = vision.Analyzer(model=MODEL)
    
    for image_path in image_files[:num_frames]:
        analyzer.load_image(image_path)
        
        dice_box, _ = analyzer.get_dice_bounding_box()
        pip_boxes_list= analyzer.get_pip_bounding_boxes()

        if dice_box is None:
            break
        elif not pip_boxes_list:
            break

        if dice_box:
            x1, y1, x2, y2 = dice_box
            width = x2 - x1
            height = y2 - y1
            dice_boxes.append({'width': width, 'height': height})
        
        for pip_box in pip_boxes_list:
            coord, _ = pip_box
            x1, y1, x2, y2 = coord
            width = x2 - x1
            height = y2 - y1
            pip_boxes.append({'width': width, 'height': height})
    
    return dice_boxes, pip_boxes

def analyze_box_sizes(dice_boxes, pip_boxes):
    """
    Analyze dice and pip box sizes to identify typical sizes and false positives.
    
    Args:
        dice_boxes: List of dice box dimensions
        pip_boxes: List of pip box dimensions
    
    Returns:
        dict: Statistics including mean, std dev, and outlier thresholds
    """
    
    dice_sizes = [box['width'] * box['height'] for box in dice_boxes]
    pip_sizes = [box['width'] * box['height'] for box in pip_boxes]
    
    dice_mean = statistics.mean(dice_sizes) if dice_sizes else 0
    dice_stdev = statistics.stdev(dice_sizes) if len(dice_sizes) > 1 else 0
    
    pip_mean = statistics.mean(pip_sizes) if pip_sizes else 0
    pip_stdev = statistics.stdev(pip_sizes) if len(pip_sizes) > 1 else 0
    
    return {
        'dice': {
            'mean': dice_mean,
            'stdev': dice_stdev,
            'min_threshold': dice_mean - (2 * dice_stdev),
            'max_threshold': dice_mean + (2 * dice_stdev),
        },
        'pips': {
            'mean': pip_mean,
            'stdev': pip_stdev,
            'min_threshold': pip_mean - (2 * pip_stdev),
            'max_threshold': pip_mean + (2 * pip_stdev),
        }
    }

def is_valid_detection(box, box_type='dice', thresholds=None):
    """Check if a box detection is valid based on size thresholds."""
    if not thresholds:
        return True
    
    size = box['width'] * box['height']
    stats = thresholds.get(box_type, {})
    
    return stats['min_threshold'] <= size <= stats['max_threshold']

dice_boxes, pip_boxes = gather_box_data(vision.Analyzer(model=MODEL), num_frames=100)
thresholds = analyze_box_sizes(dice_boxes, pip_boxes)
print("Dice Box Size Statistics:", thresholds['dice'])
print("Pip Box Size Statistics:", thresholds['pips'])

"""
Dice Box Size Statistics: 
    {
    'mean': 40596, 
    'stdev': 0, 
    'min_threshold': 40596, 
    'max_threshold': 40596
    }
Pip Box Size Statistics: 
    {
    'mean': 1666, 
    'stdev': 100.66280345788111, 
    'min_threshold': 1464.6743930842379, 
    'max_threshold': 1867.3256069157621
    }
"""