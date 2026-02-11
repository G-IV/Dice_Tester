"""
Given a path to a folder with image and label exports from Label Studio, split the images and corresponding text files with 
    matching names between another given pair of folders, train & val
    /Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Pips/2_Label_Studio/2_Exports/Patterns/train - pips by pattern/images/00b1683b-roll_6_20260125_133634_frame0007.jpg
"""
from pathlib import Path

EXPORT_FOLDER = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Pips/2_Label_Studio/2_Exports/Patterns/train - pips by pattern')
YOLO_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Pips/3_YOLO/Patterns')

def move_files_from_exports_to_yolo():
    export_images = Path(EXPORT_FOLDER, "images")
    export_labels = Path(EXPORT_FOLDER, "labels")
    import_images = Path(YOLO_PATH, "images")
    import_labels = Path(YOLO_PATH, "labels")

    for i, image_file in enumerate(sorted(export_images.glob("*.jpg"))):
        if i % 2 == 0:  # Take every other image (0, 2, 4, ...)
            label_file = export_labels / f"{image_file.stem}.txt"
            if label_file.exists():
                image_file.rename(import_images / 'train' / image_file.name)
                label_file.rename(import_labels / 'train' / label_file.name)
            else:
                print(f"Label file not found for image: {image_file.name}")
        else:
            label_file = export_labels / f"{image_file.stem}.txt"
            if label_file.exists():
                image_file.rename(import_images / 'val' / image_file.name)
                label_file.rename(import_labels / 'val' / label_file.name)
            else:
                print(f"Label file not found for image: {image_file.name}")


move_files_from_exports_to_yolo()
