'''
This file is just to try things out.
'''
from Scripts.Modules import vision
from pathlib import Path

IMAGE = '/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Scripts/Testing/1_Images/roll_1_20260125_133620_frame0000.jpg'

MODEL = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Scripts/Testing/3_Model/best.pt')

a = Path(IMAGE)

feed = vision.Feed(
    feed_type=vision.Feed.FeedType.IMG, 
    source=IMAGE, 
    logging=False,
    show_window=False
    )

analyzer = vision.Analyzer(
    model=MODEL,
    logging=False
    )   

dice = vision.Dice()

_, image = feed.capture_frame()
analyzer.analyze_frame(image)
dice.set_center_coordinates(analyzer.get_dice_center_coordinates())
feed.add_bounding_box(image, analyzer.get_dice_bounding_box())

border = "===================="
print(
    f"{border}\n",
    "Frame details:",
    dice.get_movement_magnitude(),
    f"\n{border}", 
    )