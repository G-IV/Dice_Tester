from Scripts.Modules.Analyzers import analyzer as analyzer_module
from Scripts.Modules.UI.ui import UI
from Scripts.Modules import motor

from Scripts.Modules.Annotators.annotate_factory import AnnotateFactory
from Scripts.Modules.Data.project_data_factory import ProjectDataFactory
from Scripts.Modules.Dice.dice_factory import DiceFactory
from Scripts.Modules.Feed.feed_factory import FeedFactory

from pathlib import Path
from concurrent.futures import ProcessPoolExecutor as PPE
import multiprocessing as mp
import time

# These are used in the local function, analyze_image. 
from ultralytics import YOLO
from ultralytics.engine.results import Results
from cv2.typing import MatLike

IMG_SAVE_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Captures/Images')

DATABASE_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Database/dice.db')

MODEL = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Pips/3_YOLO/Individual_Pips/runs/training/weights/best.pt')
              
MANUAL_VIDEO_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Manual/1_Videos')
"""
/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Pips/3_YOLO/Individual_Pips/images/train
"""

FPS = 16.67

SAMPLES_TO_COLLECT = 2000

LOGGING = True

def analyze_image(image: MatLike):
    model = YOLO(MODEL)
    return model(image)

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
    ad2._move_to_position(motor.Motor.POS_UNCAP)
    ad2._wait(1.0)
    print("Hit the spacebar to complete the process...")
    while True:
        key = feed.wait(200)
        if key & 0xFF == ord(' '):
            break
        feed.capture_frame()
        feed.show_frame()

    feed.destroy()
    ad2._close()
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

    feed.show_image_and_wait(500) # wait ms

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

    queue = mp.Queue() # Create a multiprocessing queue for communication between processes

    data = ProjectDataFactory.create_project_data(
        data_type="pips_by_count", 
        main_queue=queue,
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
    # Need to give the motor time to move, since it's a threaded function
    ad2._wait(3.0)

    empty_queue_count = 0
    using_analyzer = True # This is a bit of a band-aid solution to allow us to run the video sample mode without the analyzer, since the analyzer is currently required to trigger the feed to show the annotated frame.  In the future, we can implement a more robust solution that can handle both cases more elegantly.

    frame_count = 0
    max_frames = FPS * 30 # 30 seconds worth of frames, just for troubleshooting at the moment.

    print("Just before with PPE in main loop")
    with PPE() as ppe: # Context manager
        print("Starting main loop for video sample mode.")
        while True:
            try:
                item = queue.get(timeout=1) # Wait for a message from the ProjectData frame monitoring thread
                if LOGGING:
                    print(f"Received message from frame monitoring thread: {item}")
                if item['type'] == 'New Frame':
                    frame_count += 1
                    data.set_frame(item['data']) # Update the project data with the new frame
                    if LOGGING:
                        print(f"Received new frame message in main loop. Frame count: {frame_count}")
                    if using_analyzer: # If we are running an analyzer, we'll analyze the frame and save the results to the database.  If not, we'll just capture the frame and save it to the database without analysis.  This is a bit of a band-aid solution, but it should work for now.  In the future, we can implement a more robust solution that can handle both cases more elegantly.
                        future_analysis = ppe.submit(analyze_image, item['data']) # Run the analysis in a separate process to avoid blocking the main thread, since the analysis can take a significant amount of time and we don't want to block the feed from showing the annotated frame.  This is a bit of a band-aid solution, but it should work for now.  In the future, we can implement a more robust solution that can handle this more elegantly, perhaps by using a separate thread for the analysis and using a queue to communicate between the threads.
                        while not future_analysis.done():
                            time.sleep(0.1) # Wait for the analysis to complete, but don't block the main thread
                        analysis_results = future_analysis.result() # Get the results of the analysis
                        data.add_analysis_results(analysis_results) # Add the analysis results to the project data
                        feed.show_annotated_frame() # Show the annotated frame with the analysis results
                    else:
                        feed.show_frame()
                        if LOGGING:
                            print("Analyzer not enabled, showing unannotated frame.")
                    if frame_count >= max_frames:
                        if LOGGING:
                            print(f"Collected {frame_count} frames. Exiting video sample mode.")
                        break
                elif item['type'] == 'Stop Pool':
                    break
                else:
                    print(f"Received unexpected message type from frame monitoring thread: {item['type']}")
            except queue.empty:
                if LOGGING:
                    print("No message received from frame monitoring thread within timeout period.")
                    empty_queue_count += 1
                if empty_queue_count >= 5: # If we've gone a certain number of iterations without receiving a message, we can assume something has gone wrong and exit the loop to prevent it from running indefinitely.  This is a bit of a band-aid solution, but it should work for now.  In the future, we can implement a more robust solution that can detect when the frame monitoring thread has stopped working and handle it accordingly.
                    if LOGGING:
                        print("No messages received from frame monitoring thread after multiple attempts. Exiting pool loop.")
                    break
                print('Empty queue, waiting for messages from frame monitoring thread...')
                continue
            except Exception as e:
                if LOGGING:
                    print(f"Unexpected error in main loop: {e}")
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
