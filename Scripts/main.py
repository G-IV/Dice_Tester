from Scripts.Modules.Analyzers import analyzer as analyzer_module
from Scripts.Modules.Feed import feed
from Scripts.Modules.UI.ui import UI
from Scripts.Modules import motor

from Scripts.Modules.Annotators.annotate_factory import AnnotateFactory
from Scripts.Modules.Data.project_data_factory import ProjectDataFactory
from Scripts.Modules.Dice.dice_factory import DiceFactory
from Scripts.Modules.Feed.feed_factory import FeedFactory

from pathlib import Path

IMG_SAVE_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Captures/Images')

DATABASE_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Database/dice.db')

MODEL = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Scripts/Modules/Analyzers/Models/pips_by_count.pt')
              
MANUAL_VIDEO_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Manual/1_Videos')
"""
/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Pips/3_YOLO/Individual_Pips/images/train
"""

FPS = 16.67

SAMPLES_TO_COLLECT = 2000

LOGGING = True

def main():
    ui = UI(
        logging_enabled=LOGGING
    )
    ui.display_init_message()
    
    while True:
        choice = ui.top_menu_selection()
        
        if choice == '1':
            move_to_uncap_position()
        elif choice == '2':
            view_single_image_mode(ui)
        elif choice == '3':
            cycle_images_mode(ui)
        elif choice == '4':
            view_single_video_mode(ui)
        elif choice == '5':
            gather_video_samples(ui)
        elif choice == '6':
            pass
            # dice_sampler()
        elif choice == '7':
            print("Exiting Die Tester Application.")
            break
        else:
            print("Invalid choice. Please try again.")

def move_to_uncap_position() -> None:
    print("Entering Uncap Position Mode")
    data = ProjectDataFactory.create_project_data(
        data_type="pips_by_count", 
        logging=LOGGING
    )

    annotator = AnnotateFactory.create_annotator(
        annotator_type="pips_by_count", 
        data=data, 
        logging=LOGGING
    )

    feed = FeedFactory.create_feed(
        feed_type="cam", 
        cam_index=0, 
        annotator=annotator, 
        data=data, 
        logging=LOGGING
    )
    ad2 = motor.Motor()
    # It is fine if we allow this to be a blocking function
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
    ad2.close()
    print("Exiting Uncap Position Mode")

def view_single_image_mode(ui: UI) -> None:
    """
    Image mode for testing and debugging the vision system.  Displays the image with bounding boxes and pip counts overlaid.
    """
    print("Entering Single Image Mode\nPress any key to exit.")
    file = ui.get_file()

    data = ProjectDataFactory.create_project_data(
        data_type="pips_by_count", 
        logging=LOGGING
    )
    
    analyzer = analyzer_module.Analyzer(
        model_path=MODEL, 
        data=data, 
        logging=LOGGING
    )

    annotator = AnnotateFactory.create_annotator(
        annotator_type="pips_by_count", 
        data=data, 
        logging=LOGGING
    )

    feed = FeedFactory.create_feed(
        feed_type="image", 
        image_path=file, 
        annotator=annotator, 
        data=data, 
        logging=LOGGING
    )

    feed.show_image_and_wait(1500)

    feed.capture_frame()

    analyzer.analyze_frame()

    feed.show_annotated_frame()

    feed.wait(0)

    feed.destroy()
    
    print("Exiting Single Image Mode")

def cycle_images_mode(ui: UI) -> None:
    """
    Cycle through images in a specified folder, analyzing each image for dice detection and pip counting.
    Allows user to navigate through images using keyboard inputs."""
    # Get necessary inputs from user
    print("Entering Cycle Images Mode\nCycle Images Mode - Press 'n' for next, 'p' for previous, 'q' to quit")
    
    # Initialize components
    folder = ui.get_image_directory()

    data = ProjectDataFactory.create_project_data(
        data_type="pips_by_count", 
        logging=LOGGING
    )
    
    analyzer = analyzer_module.Analyzer(
        model_path=MODEL, 
        data=data, 
        logging=LOGGING
    )

    annotator = AnnotateFactory.create_annotator(
        annotator_type="pips_by_count", 
        data=data, 
        logging=LOGGING
    )

    feed = FeedFactory.create_feed(
        feed_type="multi_image", 
        folder_path=folder, 
        annotator=annotator, 
        data=data, 
        logging=LOGGING
    )

    while True:

        feed.capture_frame()
        analyzer.analyze_frame()
        feed.show_annotated_frame()

        delay_time_ms = 5000
        print(f"Press ' ' for next (auto advance after {delay_time_ms/1000} seconds), 'q' to quit: ")

        key = feed.wait(delay_time_ms)
        if key & 0xFF == ord('q'):
            break
        elif key & 0xFF == ord('n'):
            feed.load_next_image()
        elif key & 0xFF == ord('p'):
            feed.load_previous_image()
        else:
            feed.load_next_image()

    feed.destroy()
    print("Exiting Cycle Images Mode")

def view_single_video_mode(ui: UI) -> None:
    """
    Video mode for testing and debugging the vision system.  Displays the video feed with bounding boxes and pip counts overlaid.
    """
    print("Entering Single Video Mode\nPress 'q' to exit.")
    file = ui.get_file()
    data = ProjectDataFactory.create_project_data(
        data_type="pips_by_count", 
        logging=LOGGING
    )
    
    analyzer = analyzer_module.Analyzer(
        model_path=MODEL, 
        data=data, 
        logging=LOGGING
    )

    annotator = AnnotateFactory.create_annotator(
        annotator_type="pips_by_count", 
        data=data, 
        logging=LOGGING
    )

    feed = FeedFactory.create_feed(
        feed_type="video", 
        video_path=file, 
        annotator=annotator, 
        data=data, 
        logging=LOGGING
    )

    while True:
        try:
            feed.capture_frame()
        except ValueError:
            print("End of video reached or error capturing frame.")
            break
        analyzer.analyze_frame()
        feed.show_annotated_frame()
        if feed.wait_for_fps_interval() & 0xFF == ord('q'):
            continue

    feed.destroy()
    analyzer.destroy()
    
    print("Exiting Single Video Mode")

def gather_video_samples(ui: UI):
    """
    Lets the user manually trigger the motor control.  This should speed up the time it takes to capture test videos for training future models.
    """
    print("Entering Video Sample Mode")
    data = ProjectDataFactory.create_project_data(
        data_type="pips_by_count", 
        logging=LOGGING
    )
    
    analyzer = analyzer_module.Analyzer(
        model_path=MODEL, 
        data=data, 
        logging=LOGGING
    )

    annotator = AnnotateFactory.create_annotator(
        annotator_type="pips_by_count", 
        data=data, 
        logging=LOGGING
    )

    feed = FeedFactory.create_feed(
        feed_type="cam", 
        cam_index=0, 
        annotator=annotator, 
        data=data, 
        logging=LOGGING
    )

    dice = DiceFactory.create_dice(
        dice_type="pips_by_count", 
        data=data, 
        logging=LOGGING
    )

    ad2 = motor.Motor(logging=LOGGING)

    ad2.move_to_position(motor.Motor.POS_90N)
    ad2.wait(2) # give time for motor to reach position
    ad2.async_flip_position(shake=True)
    wait_time_seconds = 0.25
    total_run_time_seconds = 3
    max_runs = int(total_run_time_seconds / wait_time_seconds)
    run_counter = 0
    while True:
        print(f'Shaking & flipping motor - elapsed time {run_counter * wait_time_seconds:.2f} seconds')
        ad2.wait(wait_time_seconds)
        run_counter += 1
        if run_counter >= max_runs:
            break
    ad2.close()
    feed.destroy()
    data.destroy()
    analyzer.destroy()
    print("Exiting Video Sample Mode")

    
'''
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
    dice = feed.Dice(buffer_size=10)
    analyzer = feed.Analyzer(model=MODEL)
    db = database.DatabaseManager(db_path=DATABASE_PATH, dice_id=dice_id if dice_id != -1 else None)

    ad2.move_to_position(motor.Motor.POS_90N)
    ad2.wait(1) # give time for motor to reach position

    feed = feed.Feed() # Defaults are set to what I need for this mode
    feed.show_frame()
    frame_read_time = time.perf_counter() # Start timing for FPS control, since the feed_type is CAMERA and starts immediately capturing video frames

    new_sample = False

    ad2.flip_position(shake=True)
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
            ad2.flip_position(shake=True)
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
'''
if __name__ == "__main__":
    main()
    print("Die Tester Application has terminated.")
