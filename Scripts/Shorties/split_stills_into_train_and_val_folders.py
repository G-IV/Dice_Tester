"""
Splits still images into folders, train and val.
The train and val folders will be in the same folder as the still images.
There should be a minimum of 2 images with the same name prefix, a datetime string with the format YYYYMMDD_HHMMSS_N
That last value after the second underscore indicates the roll number.  The first file with the roll number should go to the train folder, and the second file should go to the val folder.
Any remaining images with the same name prefix will be deleted.
"""

from pathlib import Path
import shutil

def split_images_between_train_and_val(still_images_folder, label_studio_path):
    still_images_folder = Path(still_images_folder)
    train_folder = Path(label_studio_path) / "train"
    val_folder = Path(label_studio_path) / "val"
    train_folder.mkdir(exist_ok=True)
    val_folder.mkdir(exist_ok=True)

    image_files = sorted(still_images_folder.rglob("*"))
    image_files = [f for f in image_files if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}]
    
    for index, image_file in enumerate(image_files):
        if index % 2 == 0:
            shutil.move(image_file, train_folder / image_file.name)
        else:
            shutil.move(image_file, val_folder / image_file.name)

stills = '/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Captures/Images/From_Videos/Pips/Train'
label_studio_path = '/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Pips/2_Label_Studio/1_Images'
split_images_between_train_and_val(stills, label_studio_path)