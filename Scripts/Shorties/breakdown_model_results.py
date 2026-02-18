"""
This should only implement the most straightforward image capture, analysis, and print the results.
"""
from ultralytics import YOLO
from pathlib import Path
import json
# Constants
MODEL_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Testing/data/pips_by_count/pips_by_count.pt')

IMAGE_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Testing/data/pips_by_count/Images/lighted_blurry_4_0.jpg') 

# Load the model
model = YOLO(MODEL_PATH, verbose=True)

# Analyze the image
results = model(IMAGE_PATH)

print('='*50)
print(f"Number of items in results list: {len(results)}")
print("\n++++++++++   Results[0]:   ++++++++++\n")
print(results[0])
print("\n++++++++++   Results[0] Summary:   ++++++++++\n")
print(results[0].summary())
print("\n++++++++++   Results[0] Verbose:   ++++++++++\n")
print(results[0].verbose())
print("\n++++++++++   Results[0] Boxes:   ++++++++++\n")
print(results[0].boxes)
print("\n++++++++++   Results[0] Boxes[0]:   ++++++++++\n")
print(results[0].boxes[0])
print("\n++++++++++   Results[0] Boxes[0] xywh:   ++++++++++\n")
print(results[0].boxes[0].xywh.cpu().numpy()[0])
print("\n++++++++++   Results[0] Boxes[0] xywh as x1, y1, _, _:   ++++++++++\n")
x1, y1, _, _ = results[0].boxes[0].xywh.cpu().numpy()[0]
print(f"x1: {x1}, y1: {y1}")
print("\n++++++++++   Results[0] Boxes cls from Numpy:   ++++++++++\n")
print(results[0].boxes.cls.numpy())
print('='*50)