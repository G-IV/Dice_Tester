"""
Splits still images into folders, train and val.
The train and val folders will be in the same folder as the still images.
There should be a minimum of 2 images with the same name prefix, a datetime string with the format YYYYMMDD_HHMMSS_N
That last value after the second underscore indicates the roll number.  The first file with the roll number should go to the train folder, and the second file should go to the val folder.
Any remaining images with the same name prefix will be deleted.
"""

from pathlib import Path
import shutil

def move_files_to_train_and_val(still_images_folder):
    still_images_folder = Path(still_images_folder)
    train_folder = still_images_folder / "train"
    val_folder = still_images_folder / "val"
    train_folder.mkdir(exist_ok=True)
    val_folder.mkdir(exist_ok=True)

    images_by_prefix = {}
    for image_path in still_images_folder.glob("*.jpg"):
        prefix = "_".join(image_path.stem.split("_")[:-1])
        images_by_prefix.setdefault(prefix, []).append(image_path)

    for prefix, images in images_by_prefix.items():
        if len(images) < 2:
            shutil.move(str(images[0]), train_folder / images[0].name)
            continue
        images.sort()
        shutil.move(str(images[0]), train_folder / images[0].name)
        shutil.move(str(images[1]), val_folder / images[1].name)
        for image in images[2:]:
            image.unlink()

stills = '/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Captures/Images/From_Videos/Pips'
move_files_to_train_and_val(stills)