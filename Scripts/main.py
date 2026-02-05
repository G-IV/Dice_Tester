from pathlib import Path
import cv2
from numpy import put
from Scripts.Modules import data, motor, vision, data
import time
from datetime import datetime
from typing import Union
from cv2.typing import MatLike

IMG_SAVE_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Captures/Images')

DATABASE_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Database/dice.db')

MODEL = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Scripts/Testing/3_Model/best.pt')

MANUAL_VIDEO_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Manual/1_Videos')

FPS = 16.67

SAMPLES_TO_COLLECT = 2000

# Helper Functions
def get_path_input(path_type: str = 'file') -> Path:
    """
    Prompts the user for a file or directory path and validates it.
    Args:
        path_type (str): The type of path to validate ('file' or 'directory').
    Returns:
        Path: A valid Path object based on the user's input.
    """
    # Validate path_type
    if path_type not in ['file', 'directory']:
        return -1
    
    # Set up variables for path validation loop
    bad_path_counter = 0
    max_bad_paths = 3
    path_check = False

    while not path_check:
        # Prompt user for path input
        if path_type == 'directory':
            path = Path(input("Enter valid folder path: ").strip())
        else:
            path = Path(input("Enter valid file path: ").strip())
        # path = Path(input(f"Invalid path. Enter path to {path_type}: ").strip())

        # Validate the provided path
        if path_type == 'file':
            path_check = path.is_file()
        else:
            path_check = path.is_dir()

        # If valid, return the path
        if path_check:
            return path

        # If invalid, increment counter and check if max attempts reached
        bad_path_counter += 1
        if bad_path_counter >= max_bad_paths:
            print("Too many invalid attempts. Exiting Cycle Images Mode.")
            return -2
        
        # Reprompt user for path input
        if path_type == 'directory':
            path = Path(input(f"Invalid path {bad_path_counter} of {max_bad_paths}.  Enter valid folder path: ").strip())
        else:
            path = Path(input(f"Invalid path {bad_path_counter} of {max_bad_paths}.  Enter file path: ").strip())

def analyze_image(
        feed: vision.Feed, 
        analyzer: vision.Analyzer, 
        dice: vision.Dice
    ):
    """
    Docstring for analyze_image
    Analyzes a single image for dice detection and pip counting.
    :param feed: Description
    :type feed: vision.Feed
    :param analyzer: Description
    :type analyzer: vision.Analyzer
    :param dice: Description
    :type dice: vision.Dice
    :param image_path: Description
    :type image_path: Path

    You'll need to call feed.capture_frame() before calling this function, since there are instances where running the analyzer isn't needed and it would only slow down the process.
    """
    if feed.frame is None:
        return None
    analyzer.analyze_frame(feed.frame)
    dice.set_center_coordinates(analyzer.get_dice_center_coordinates())
    feed.add_dice_bounding_box(analyzer.get_dice_bounding_box())
    feed.add_pip_bounding_boxes(analyzer.get_pip_bounding_boxes())
    analyzer.count_pips()
    feed.add_border_details(dice, analyzer.dice_value)
    feed.append_annotated_frame()

    return 1

def analyze_video(
        feed: vision.Feed,
        analyzer: vision.Analyzer, 
        dice: vision.Dice, 
        video_path: Path
    ):
    counter = 0
    while True:
        counter += 1
        print(f"Analyzing video frame {counter}...")
        feed.capture_frame()
        if feed.frame is None:
            print("End of video reached or failed to capture frame.")
            break
        ret = analyze_image(feed, analyzer, dice)
        feed.show_frame()
        feed.wait(250)
    print(f"Finished analyzing video: {video_path.name}")

def main():
    print("Die Tester Application - Main Menu")
    
    while True:
        print("\n" + "="*50)
        print("Select an option:")
        print("1) Cycle through images in folder")
        print("2) View single image")
        print("3) View single video")
        print("4) Move to uncap position")
        print("5) Gather sample videos for model training")
        print("6) Gather data for dice analysis")
        print("7) Exit")
        print("="*50)
        
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == '1':
            cycle_images_mode()
        elif choice == '2':
            view_single_image_mode()
        elif choice == '3':
            view_single_video_mode()
        elif choice == '4':
            move_to_uncap_position()
        elif choice == '5':
            gather_video_samples()
        elif choice == '6':
            dice_sampler()
        elif choice == '7':
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
    folder = get_path_input(path_type='directory')
    
    # Load image files from the specified folder
    image_files = sorted([f for f in folder.iterdir() if f.suffix.lower() in ['.jpg', '.jpeg', '.png']])

    if not image_files:
        print("No image files found in the specified folder.")
        return -1
    
    # Initialize components
    feed = vision.Feed(
        feed_type=vision.Feed.FeedType.IMG, 
        source=image_files[0], 
        logging=False,
        show_window=True
        )
    
    dice = vision.Dice(buffer_size=1)  # Single frame analysis
    analyzer = vision.Analyzer(model=MODEL)

    for image_path in image_files:

        feed.open_source(image_path)
        feed.capture_frame()

        analyze_image(feed, analyzer, dice)

        border = "="*20
        print(
            f"{border}\n",
            f"Analyzing Image: {image_path.name}\n",
            "Frame details:",
            dice.get_movement_magnitude(),
            f"\n{border}", 
            )

        feed.show_frame()

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
    print("Entering Single Image Mode\nPress any key to exit.")
    file = get_path_input(path_type='file')

    feed = vision.Feed(
        feed_type=vision.Feed.FeedType.IMG, 
        source=file, 
        logging=False,
        show_window=True
        )
    dice = vision.Dice(buffer_size=1)  # Single frame analysis
    analyzer = vision.Analyzer(model=MODEL)

    feed.capture_frame()

    analyze_image(feed, analyzer, dice)

    feed.show_frame()

    feed.wait(0)

    feed.close_source()
    feed.close_window()
    
    print("Exiting Single Image Mode")

def view_single_video_mode():
    """
    Video mode for testing and debugging the vision system.  Displays the video feed with bounding boxes and pip counts overlaid.
    """
    print("Entering Single Video Mode\nPress 'q' to exit.")
    file = get_path_input(path_type='file')

    feed = vision.Feed(
        feed_type=vision.Feed.FeedType.VIDEO, 
        source=file, 
        logging=False,
        show_window=True
        )
    dice = vision.Dice(buffer_size=10)  # Multi-frame analysis
    analyzer = vision.Analyzer(model=MODEL)

    total_frames = int(feed.cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Total frames in video: {total_frames}")

    analyze_video(feed, analyzer, dice, file)

    feed.close_source()
    feed.close_window()
    
    print("Exiting Single Video Mode")

def move_to_uncap_position():
    print("Entering Uncap Position Mode")
    feed = vision.Feed(
        show_annotations=False
    )
    feed.show_frame()
    ad2 = motor.Motor()
    ad2.move_to_position(motor.Motor.POS_UNCAP)
    ad2.wait(1.0)
    print("Hit the spacebar to complete the process...")
    while True:
        key = feed.wait(200)
        if key & 0xFF == ord(' '):
            break
        feed.capture_frame()
        feed.show_frame()

    feed.destroy()

    ad2.flip_position()
    time.sleep(2)
    ad2.flip_position()
    time.sleep(2)
    ad2.flip_position()
    time.sleep(2)
    
    ad2.close()
    print("Exiting Uncap Position Mode")

def gather_video_samples():
    """
    Lets the user manually trigger the motor control.  This should speed up the time it takes to capture test videos for training future models.
    """
    print("Entering Video Sample Mode")
    video_directory = None
    analyzer = None

    save_video = input("Save videos (y/n): ").strip().lower() == 'y'
    if save_video:
        video_directory = get_path_input(path_type='directory')

    view_with_annotations = input("View live feed with annotations (y/n): ").strip().lower() == 'y'

    auto_roll_when_dice_is_stable = input("Auto roll when dice is stable (y/n): ").strip().lower() == 'y'

    flip_interval = float(input("Enter motor flip interval in seconds (default 0 - manual flip only): ").strip())
    number_of_samples = int(input("Enter number of samples to collect (default 0 - infinite): ").strip())

    ad2 = motor.Motor()
    dice = vision.Dice(buffer_size=10)
    if view_with_annotations:
        analyzer = vision.Analyzer(model=MODEL)

    ad2.move_to_position(motor.Motor.POS_90N)
    ad2.wait(1) # give time for motor to reach position

    feed = vision.Feed(
        feed_type=vision.Feed.FeedType.CAMERA, 
        source=0, 
        logging=False,
        show_window=True,
        show_annotations=view_with_annotations
    )
    feed.show_frame()
    frame_read_time = time.perf_counter() # Start timing for FPS control, since the feed_type is CAMERA and starts immediately capturing video frames

    new_recording = False

    ad2.flip_position()
    roll_counter = 0
    flip_time_start = time.perf_counter() # Start timing for motor flip interval control
    time_since_last_flip = 0

    while True:
        if view_with_annotations:
            analyze_image(feed, analyzer, dice)
            if dice.is_stable() & (time_since_last_flip > 1.0) & auto_roll_when_dice_is_stable:
                print("Die is stable.")
                new_recording = True

        feed.show_frame()

        if new_recording:
            filepath = Path(f"{video_directory}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{roll_counter}.mp4")
            feed.save_video(video_path=filepath, fps=FPS)
            ad2.flip_position()
            flip_time_start = time.perf_counter() # Start timing for motor flip interval control
            new_recording = False
            roll_counter += 1

        current_time = time.perf_counter()

        time_since_last_flip = (current_time - flip_time_start)
        time_since_last_frame = (current_time - frame_read_time) * 1000

        time_before_next_frame_ready = 1000/FPS - time_since_last_frame
        # print(f"Time since last frame: {time_since_last_frame}")
        # print(f"Time before next frame: {time_before_next_frame_ready}")
        # Use remaining time before next frame capture to look for user input
        if(time_before_next_frame_ready > 0):
            wait_time = max(1, round(time_before_next_frame_ready))
            key = feed.wait(wait_time)
            if key & 0xFF == ord('q'):
                print("Exiting Video Sample Mode.")
                break
            elif key & 0xFF == ord(' '):
                new_recording = True
    
        feed.capture_frame()
        frame_read_time = time.perf_counter() # Reset frame read timer

        if time_since_last_flip >= flip_interval:
            new_recording = True

        if roll_counter >= number_of_samples:
            print("Collected required samples. Exiting Video Sample Mode.")
            break

    feed.destroy()
    ad2.close()
    print("Exiting Video Sample Mode")

def dice_sampler():
    """
    This is the main data gathering mode we'll use to gather data for analyzing dice rolls.
    """
    print("Entering Auto Camera Mode for Vision-Based Motor Control")
    analyzer = None

    flip_interval = float(input("Enter motor flip interval in seconds (default 0 - manual flip only): ").strip())
    number_of_samples = int(input("Enter number of samples to collect (default 0 - infinite): ").strip())
    dice_id = int(input("Enter Dice ID for this test session (-1 auto-assigns an ID): ").strip())

    ad2 = motor.Motor()
    dice = vision.Dice(buffer_size=10)
    analyzer = vision.Analyzer(model=MODEL)
    db = data.DatabaseManager(db_path=DATABASE_PATH, dice_id=dice_id if dice_id != -1 else None)

    ad2.move_to_position(motor.Motor.POS_90N)
    ad2.wait(1) # give time for motor to reach position

    feed = vision.Feed() # Defaults are set to what I need for this mode
    feed.show_frame()
    frame_read_time = time.perf_counter() # Start timing for FPS control, since the feed_type is CAMERA and starts immediately capturing video frames

    new_sample = False

    ad2.flip_position()
    sample_counter = 0
    flip_time_start = time.perf_counter() # Start timing for motor flip interval control
    time_since_last_flip = 0
    while True:
        analyze_image(feed, analyzer, dice)

        feed.show_frame()

        if dice.is_stable() & (time_since_last_flip > 1.0):
            print("Die is stable.")
            new_sample = True

        if new_sample:
            timestamp = datetime.now()
            time_string = timestamp.strftime('%Y%m%d_%H%M%S_%f')[:-3]
            filepath = f"{IMG_SAVE_PATH}/{dice_id}_({analyzer.dice_value})_{time_string}.jpg"
            feed.save_image(img_path=Path(filepath))
            db.log_test_result(
                timestamp=timestamp,
                motor_position=ad2.position,
                dice_result=analyzer.dice_value,
                img_path=filepath
            )
            ad2.flip_position()
            flip_time_start = time.perf_counter() # Start timing for motor flip interval control
            new_sample = False
            sample_counter += 1

        current_time = time.perf_counter()

        time_since_last_flip = (current_time - flip_time_start)
        time_since_last_frame = (current_time - frame_read_time) * 1000

        time_before_next_frame_ready = 1000/FPS - time_since_last_frame
        # print(f"Time since last frame: {time_since_last_frame}")
        # print(f"Time before next frame: {time_before_next_frame_ready}")
        # Use remaining time before next frame capture to look for user input
        if(time_before_next_frame_ready > 0):
            wait_time = max(1, round(time_before_next_frame_ready))
            key = feed.wait(wait_time)
            if key & 0xFF == ord('q'):
                print("Exiting Video Sample Mode.")
                break
            elif key & 0xFF == ord(' '):
                new_sample = True
    
        feed.capture_frame()
        frame_read_time = time.perf_counter() # Reset frame read timer

        if time_since_last_flip >= flip_interval:
            new_sample = True

        if sample_counter >= number_of_samples:
            print("Collected required samples. Exiting Video Sample Mode.")
            break

    feed.destroy()
    ad2.close()
    print("Exiting Video Sample Mode")

if __name__ == "__main__":
    main()
    print("Die Tester Application has terminated.")
