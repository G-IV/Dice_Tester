from pathlib import Path
from Scripts.Modules import data, motor, vision, data
import time
from datetime import datetime

IMG_SAVE_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Database/Images/')

DATABASE_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Database/dice.db')


def main():
    print("Die Tester Application - Main Menu")
    
    while True:
        print("\n" + "="*50)
        print("Select an option:")
        print("1) Cycle through images in folder")
        print("2) View single image")
        print("3) View single video")
        print("4) Manual camera with motor controls")
        print("5) Auto camera with vision-based motor control")
        print("6) Exit")
        print("="*50)
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            cycle_images_mode()
        elif choice == '2':
            view_single_image_mode()
        elif choice == '3':
            view_single_video_mode()
        elif choice == '4':
            manual_camera_mode()
        elif choice == '5':
            auto_camera_mode()
        elif choice == '6':
            print("Exiting Die Tester Application.")
            break
        else:
            print("Invalid choice. Please try again.")

def cycle_images_mode():
    """
    Cycle through images in a specified folder, analyzing each image for dice detection and pip counting.
    Allows user to navigate through images using keyboard inputs."""
    # Get necessary inputs from user
    print("Entering Cycle Images Mode\nCycle Images Mode - Press 'n' for next, 'p' for previous, 'q' to quit")
    folder = Path(input("Enter folder path containing images: ").strip())
    bad_path_counter = 0
    max_bad_paths = 3
    while not folder.is_dir():
        bad_path_counter += 1
        if bad_path_counter >= max_bad_paths:
            print("Too many invalid attempts. Exiting Cycle Images Mode.")
            break
        folder = Path(input(f"Invalid path {bad_path_counter} of {max_bad_paths}.  Enter folder path containing images: ").strip())
        return
    if bad_path_counter > 0:
        return -1
    log_to_db = input("Log results to database? (y/n): ").strip().lower() == 'y'

    # Load image files from the specified folder
    image_files = sorted([f for f in folder.iterdir() if f.suffix.lower() in ['.jpg', '.jpeg', '.png']])
    if not image_files:
        print("No image files found in the specified folder.")
        return -1
    
    # Initialize components
    MODEL = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Scripts/Testing/3_Model/best.pt')

    feed = vision.Feed(
        feed_type=vision.Feed.FeedType.IMG, 
        source=image_files[0], 
        logging=False,
        show_window=True
        )
    
    dice = vision.Dice(buffer_size=1)  # Single frame analysis
    analyzer = vision.Analyzer(model=MODEL)

    for image_path in image_files:
        feed.reopen_source(image_path)
        _, image = feed.capture_frame()
        analyzer.analyze_frame(image)
        dice.set_center_coordinates(analyzer.get_dice_center_coordinates())
        image = feed.add_dice_bounding_box(image, analyzer.get_dice_bounding_box())
        image = feed. add_pip_bounding_boxes(image, analyzer.get_pip_bounding_boxes())
        pips = analyzer.count_pips()
        image = feed.add_border_details(image, dice, pips)

        border = "="*20
        print(
            f"{border}\n",
            f"Analyzing Image: {image_path.name}\n",
            "Frame details:",
            dice.get_movement_magnitude(),
            f"\n{border}", 
            )

        feed.show_frame(image)
        print("Press 'p' for previous, 'q' to quit: ")
        key = feed.wait(1)
        if key == 'q':
            break
        elif key == 'p':
            continue

    feed.close_source()
    feed.close_window()
    print("Exiting Cycle Images Mode")

def view_single_image_mode():
    """
    Image mode for testing and debugging the vision system.  Displays the image with bounding boxes and pip counts overlaid.
    """
    print("View Single Image Mode")

def view_single_video_mode():
    """
    Video mode for testing and debugging the vision system.  Displays the video feed with bounding boxes and pip counts overlaid.
    """
    print("View Single Video Mode")

def manual_camera_mode():
    """
    Lets the user manually trigger the motor control.  This should speed up the time it takes to capture test videos for training future models.
    """
    print("Manual Camera Mode with Motor Controls")

def auto_camera_mode():
    """
    This is the main data gathering mode we'll use to gather data for analyzing dice rolls.
    """
    print("Auto Camera Mode with Vision-Based Motor Control")

if __name__ == "__main__":
    main()
    print("Die Tester Application has terminated.")
