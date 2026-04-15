# Parallel processing related imports
import multiprocessing as mp
from queue import Empty
from concurrent.futures import ProcessPoolExecutor
from threading import Thread
import time

# Project module imports
from Scripts.Modules.queue_data import QueueData, Command as QuCmd
from Scripts.Modules.Stream.stream import Stream
from Scripts.Modules.Motor.ad2 import Motor
from Scripts.Modules.Data.data_factory import DataFactory
from Scripts.Modules.Feed.feed_factory import FeedFactory
from Scripts.Modules.Dice.dice_factory import DiceFactory
from Scripts.Modules.Dice.dice import DiceState

# Class support imports
from pathlib import Path

# Image processing imports
import cv2
from ultralytics import YOLO

# Troubleshooting imports
import random

# Constants
ENABLE_LOGGING = True
MODEL = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Pips/3_YOLO/Patterns/runs/weights/best.pt')

#============================
# AI says that opening a new model is expensive, so it is beter to do as a worker not for each frame.
# So I'm following it's advice on analyzing the frames & storing the results & displaying the resulting frame
_workder_model = None
def init_worker(model_path: Path):
    global _worker_model
    _worker_model = YOLO(model_path)

def analyze_frame_worker(frame):
    if ENABLE_LOGGING:
        print("main.py analyze_frame_worker()")
    result = _worker_model(frame, verbose=False)[0]
    rendered = result.plot()  # Get the rendered frame with detections drawn on it.
    if ENABLE_LOGGING:
        print("  --> Frame analysis complete, returning rendered frame and result data.")
    return rendered, result

#============================

def close_queue(queue: mp.Queue) -> None:
    """
    Closes the queue and ensures that all remaining items are processed before exiting.
    """
    if ENABLE_LOGGING:
        print("main.py close_queue()")
    
    queue.cancel_join_thread()
    queue.close()

    if ENABLE_LOGGING:
        print("  --> Queue closed, waiting for remaining items to be processed...")

def main() -> None:
    """
    Starting point for the application.  This is where the user will manage the activities of the application.
    """
    print("==================================")
    print("Starting the Tester Application...")
    print("==================================")

    # Setup
    main_queue = mp.Queue()

    # The first thing we should send to the queue is command to enter the user selection state.
    main_queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))

    while True:
        try:
            item = main_queue.get(timeout=1)  # Wait for an item for up to 1 second
            match item.cmd:
                case QuCmd.MAIN_MENU:
                    top_level(main_queue)
                case QuCmd.MOVE_TO_UNCAP:
                    move_to_uncap(main_queue)
                case QuCmd.SINGLE_IMAGE:
                    single_image_thread = Thread(target=view_single_image, args=(main_queue,), daemon=True)
                    single_image_thread.start()
                case QuCmd.GATHER_SAMPLE_VIDEOS:
                    gather_sample_videos_thread = Thread(target=gather_sample_videos, args=(main_queue,), daemon=True)
                    gather_sample_videos_thread.start()
                case QuCmd.GATHER_DICE_ANALYSIS_DATA:
                    gather_dice_analysis_data(main_queue)
                case QuCmd.EXIT:
                    break
        except Empty:
            # Timeouts are expected
            pass
        except Exception as e:
            print(f"main.py main() encountered an unexpected error: {e}. Returning to the main menu.")
            break

    # Breakdown
    close_queue(main_queue)

"""
These are the main functions for the application.  The main function is responsible for managing the overall flow of the application, while the top_level function is responsible for presenting the user with options and handling their selections.
"""
def top_level(queue: mp.Queue) -> None:
    """
    This function represents the top-level logic of the application.  It allows the user to select which activity they want to perform.

    This is a blocking function.
    """
    print("\n" + "="*50)
    print("Select an option:")
    print("0) Exit")
    print("1) Move to uncap position")
    # print("2) View single image")
    # print("3) Cycle through images in folder")
    # print("4) View single video")
    # print("5) Gather sample videos for model training")
    print("6) Gather data for dice analysis")
    print("="*50)

    choice = input("Enter your choice (0-6): ").strip()

    match choice:
        case "0":
            if ENABLE_LOGGING:
                print("'Exit' selected.")
            queue.put(QueueData(cmd=QuCmd.EXIT, data=None))
        case "1":
            if ENABLE_LOGGING:
                print("'Move to uncap position' selected.")
            queue.put(QueueData(cmd=QuCmd.MOVE_TO_UNCAP, data=None))
        case "2":
            if ENABLE_LOGGING:
                print("'View single image' selected.")
            queue.put(QueueData(cmd=QuCmd.SINGLE_IMAGE, data=None))
        case "5":
            if ENABLE_LOGGING:
                print("'Gather sample videos for model training' selected.")
            queue.put(QueueData(cmd=QuCmd.GATHER_SAMPLE_VIDEOS, data=None))
        case "6":
            if ENABLE_LOGGING:
                print("'Gather data for dice analysis' selected.")
            queue.put(QueueData(cmd=QuCmd.GATHER_DICE_ANALYSIS_DATA, data=None))
        case _:
            if ENABLE_LOGGING:
                print(f"You selected: {choice}. This option is not implemented yet.")
            queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))

def move_to_uncap(queue: mp.Queue) -> None:
    """
    This function is responsible for moving the camera to the uncap position.  This is a placeholder function and does not contain any actual logic for moving the camera.
    """
    if ENABLE_LOGGING:
        print("Moving to uncap position...)")
    try:
        motor = Motor(logging=ENABLE_LOGGING, main_queue=queue)
    except Exception as e:
        if ENABLE_LOGGING:
            print(f"main.py move_to_uncap() encountered an error while initializing the motor: {e}. Returning to the main menu.")
        queue.put(QueueData(cmd=QuCmd.EXIT, data=None))
        return
    motor.move_to_uncap()
    input('Press Enter to return to the main menu...')
    motor.close() # Ensure we close the motor connection when we're done.
    # After completing the action, return to the main menu
    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))

def view_single_image(queue: mp.Queue) -> None:
    """
    This function is responsible for capturing and displaying a single image from the camera.  This is a placeholder function and does not contain any actual logic for capturing or displaying an image.
    """

    # Get the path via user input
    image_path = Path(input("Enter the image filepath: ").strip())

    # Validate the file exists
    if not image_path.is_file():
        print("Entry is not a valid file path.")
        queue.put(QueueData(cmd=QuCmd.SINGLE_IMAGE, data=None))
        return

    # Validate the file path and type
    if not any(f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp'] for f in [image_path]):
        print("Invalid file type.")
        queue.put(QueueData(cmd=QuCmd.SINGLE_IMAGE, data=None))
        return
    
    project_data = DataFactory.create_project_data("project_data", logging=ENABLE_LOGGING, main_queue=queue, model_path=MODEL)
    FeedFactory.create_feed("image", data=project_data, image_path=image_path, logging=ENABLE_LOGGING)

    # I can get away with this by calling this in a separate thread.
    while True:
        # Wait for the user to return to end this function
        input('Press Enter to return to the main menu...\n')
        break

    project_data.close() # Stop the data processing thread.

    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))
    
    # I want to wait for the image to be shown in the stream and then wait for the user to return to end this function
    """
    /Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Pips/3_YOLO/Patterns/images/val/0a4f5708-20260204_104633_136_frame0020.jpg
    """

def gather_sample_videos(queue: mp.Queue) -> None:
    """
    This function is responsible for gathering sample videos for model training.  This is a placeholder function and does not contain any actual logic for gathering videos.
    """
    project_data = DataFactory.create_project_data("project_data", logging=False, main_queue=queue, model_path=MODEL)
    feed = FeedFactory.create_feed("camera", data=project_data, logging=False)

    motor = Motor(logging=ENABLE_LOGGING, main_queue=queue)
    motor.move_to_uncap() # Initial positioning
    motor.flip() # Start the flipping process to capture videos.
    time.sleep(2) # Wait for the flipping to start before we begin capturing frames.
    # This is where we'll control a new roll or quitting back to the main menu.
    while True:
        choice = input("Press 'n' to flip the tower and capture a vidoe, or press 'q' to return to the main menu: ").strip().lower()
        if choice == "n":
            project_data.new_roll()
            motor.flip()
        elif choice == "q":
            break
    
    feed.destroy() # Ensure we release the camera feed when we're done.
    project_data.close() # Stop the data processing thread.
    motor.close() # Ensure we close the motor connection when we're done.

    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))

def gather_dice_analysis_data(queue: mp.Queue) -> None:
    """
    This function is responsible for gathering data for dice analysis.  This is a placeholder function and does not contain any actual logic for gathering data.
    """
    print("\n" + "="*50)
    print("main.py gather_dice_analysis_data() Starting data gathering process for dice analysis.")
    print("="*50 + "\n")

    process_queue = mp.Queue() # Use this to notify the process with data and routine updates
    initial_time = time.perf_counter() # Track how long we've been gathering data for to know when to reset the tower if the dice get stuck.
    max_process_time = 20 # If we've been gathering data for more than this amount of time, we should exit to prevent any potential issues.
    start_time = time.perf_counter() # Start a timer to track how long we've been gathering data for.
    max_time_before_flip = 4 # If we've been gathering data for more than this amount of time, we should flip the tower to get a new roll.
    
    try:
        if ENABLE_LOGGING:
            print("main.py gather_dice_analysis_data() Initializing supporting class instances...")
        process_data = DataFactory.create_project_data("project_data", logging=ENABLE_LOGGING, model_path=MODEL, process_queue=process_queue)
        feed = FeedFactory.create_feed("camera", data=process_data, process_queue=process_queue, logging=ENABLE_LOGGING)
        stream = Stream(logging=ENABLE_LOGGING)
        dice = DiceFactory.create_dice("six_sided_pips", logging=ENABLE_LOGGING, data=process_data)
        motor = Motor(logging=False, main_queue=queue)
        if ENABLE_LOGGING:
            print("  --> Successfully initialized all classes for gathering dice analysis data.")
    except Exception as e:
        if 'feed' in locals() and feed is not None:
            feed.destroy()
        if 'stream' in locals() and stream is not None:
            stream.destroy()
        if 'motor' in locals() and motor is not None:
            motor.close() 
        if 'process_data' in locals() and process_data is not None:
            process_data.destroy()
        print(f"main.py gather_dice_analysis_data() encountered an error while initializing supporting class instances: {e}, attempting to return to the main menu.")
        queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))
        return
    
    # Helper functions that are reliant on class instances
    def on_analyze_frame_done(f):
        try:
            if ENABLE_LOGGING:
                print("main.py on_analyze_frame_done() Frame analysis complete, processing results...")
            rendered, result = f.result()
            process_data.new_result(result) # Store the results of the processed frame in the data object.
            process_queue.put(QueueData(cmd=QuCmd.SHOW_FRAME, data=rendered)) # Notify the main process that a new frame is ready for display.
            process_queue.put(QueueData(cmd=QuCmd.EVALUATE_DICE_STATE, data=None)) # After showing the frame, we want to evaluate the state of the dice to know if we need to flip the tower for a new roll.
            if ENABLE_LOGGING:
                print("  --> Frame analysis results processed and SHOW_FRAME & EVALUATE_DICE_STATE commands sent to process queue.")
        except Exception as e:
            print(f"main.py on_analyze_frame_done() encountered an error: {e}.")
    
    def close():
        if ENABLE_LOGGING:
            print("main.py gather_dice_analysis_data() close() called, closing all supporting class instances...")
        feed.destroy() # Ensure we release the camera feed when we're done.
        stream.destroy() # Ensure we close the video stream when we're done.
        motor.close() # Ensure we close the motor connection when we're done.
        if ENABLE_LOGGING:
            print("main.py gather_dice_analysis_data() All supporting class instances closed.")
        process_queue.cancel_join_thread()
        process_queue.close() # Close the process queue to clean up resources.

    if ENABLE_LOGGING:
        print("main.py gather_dice_analysis_data() Moving to uncap position...")
    motor.move_to_uncap() # Initial positioning
    time.sleep(1) # Wait for the camera to stabilize before we begin capturing frames.

    if ENABLE_LOGGING:
        print("main.py gather_dice_analysis_data() Motor is in uncap position, starting main data gathering loop...")
    process_queue.put(QueueData(cmd=QuCmd.GET_NEXT_SAMPLE, data=None)) # Start getting a new sample
    feed.ready_for_frames(True) # Now that we're ready to process frames, we can allow the feed to put frames in the process queue.

    with ProcessPoolExecutor(
        initializer=init_worker,
        initargs=(MODEL,)
    ) as executor:
        while True:
            # TODO: Change this to tracking samples, not elapsed time
            if time.perf_counter() - initial_time > max_process_time: # If we've been gathering data for too long, we should exit to prevent any potential issues.
                if ENABLE_LOGGING:
                    print("main.py gather_dice_analysis_data() Maximum processing time reached, passing EXIT command to process queue...")
                process_queue.put(QueueData(cmd=QuCmd.EXIT, data=None))
            try:
                item = process_queue.get(timeout=1)  # Wait for an item for up to 1 second
                # print(f"cmd received: {item.cmd}")
                match item.cmd:
                    case QuCmd.EXIT:
                        if ENABLE_LOGGING:
                            print("main.py gather_dice_analysis_data() EXIT command received, breaking loop.")
                        break
                    case QuCmd.GET_NEXT_SAMPLE:
                        if ENABLE_LOGGING:
                            print("main.py gather_dice_analysis_data() GET_NEXT_SAMPLE command received, preparing for next sample...")
                        process_data.clear_frames() # Clear any frames that were captured during the initial positioning.
                        motor.flip() # Flip the tower to start the next roll.
                        start_time = time.perf_counter() # Reset the timer for the new roll.
                    case QuCmd.NEW_FRAME_CAPTURED:
                        if ENABLE_LOGGING:
                            print("main.py gather_dice_analysis_data() NEW_FRAME_CAPTURED command received, submitting frame for analysis...")
                        future_new_frame = executor.submit(analyze_frame_worker, item.data)
                        future_new_frame.add_done_callback(on_analyze_frame_done) # Analyze the frame in a separate process and show the results in the stream when it's done.
                    case QuCmd.SHOW_FRAME:
                        if ENABLE_LOGGING:
                            print("main.py gather_dice_analysis_data() SHOW_FRAME command received, calling stream.show_frame()...")
                        stream.show_frame(item.data) # Show the frame in the stream when the analysis is done
                    case QuCmd.EVALUATE_DICE_STATE:
                        if ENABLE_LOGGING:
                            print("main.py gather_dice_analysis_data() EVALUATE_DICE_STATE command received, evaluating dice state...")
                        # I want determine if it is time to start a new roll
                        dice_state = dice.get_dice_state()
                        # print(f"  --> Current dice state: {dice_state}")
                        #   There's been no movement & no dice for a while.  The dice is stuck somewhere, we need to reset the tower.
                        if time.perf_counter() - start_time > max_time_before_flip and dice_state == DiceState.UNKNOWN:
                            if ENABLE_LOGGING:
                                print(f"  -> Dice state is UNKNOWN for longer than {max_time_before_flip} seconds, resetting tower for new roll...")
                            process_queue.put(QueueData(cmd=QuCmd.RESET_TOWER, data=None))
                            process_data.clear_frames() # Clear any frames that were captured during this roll since we're going to reset the tower and start a new roll.
                        #   - Yes if the dice are settled.  In this case, we would want to capture the value of the dice.
                        if dice_state == DiceState.SETTLED:
                            if ENABLE_LOGGING:
                                print("  -> Dice state is SETTLED, capturing dice value and starting new roll...")
                            value = dice.get_dice_value(process_data.results[-1]) # Get the value of the dice based on the most recent analyzed frame.
                            if ENABLE_LOGGING:
                                print(f"  -> Current dice value: {value}") 
                            # TODO: store value to database
                            process_queue.put(QueueData(cmd=QuCmd.GET_NEXT_SAMPLE, data=None)) # Start getting a new sample
                    case QuCmd.RESET_TOWER:
                        # print(". --> Resetting the tower...")
                        future_motor_reset = executor.submit(motor.reset_position) # Show the last captured frame in the stream while we reset the tower so the user can see what's going on.
                        future_motor_reset.add_done_callback(lambda f: process_queue.put(QueueData(cmd=QuCmd.GET_NEXT_SAMPLE, data=None))) # After the tower is reset, start getting a new sample.
                    case _:
                        # Handle other commands as needed
                        pass
            except Empty:
                pass
            except Exception as e:
                print(f"main.py gather_dice_analysis_data() encountered an unexpected error: {e}.")
                break

    if ENABLE_LOGGING: 
        print("main.py gather_dice_analysis_data() Main loop exited, calling close().")

    close()

    if ENABLE_LOGGING:
        print("main.py gather_dice_analysis_data() Data gathering process for dice analysis has completed, returning to main menu.")
    # Return to the main queue after completing the process
    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))

if __name__ == "__main__":
    main()
    print("Die Tester Application has terminated.")
