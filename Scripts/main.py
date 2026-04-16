# Parallel processing related imports
import multiprocessing as mp
from queue import Empty
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from threading import Thread
import time
from datetime import datetime

# Project module imports
from Scripts.Modules.queue_data import QueueData, Command as QuCmd
from Scripts.Modules.Stream.stream import Stream
from Scripts.Modules.Motor.ad2 import Motor
from Scripts.Modules.Data.data_factory import DataFactory
from Scripts.Modules.Feed.feed_factory import FeedFactory
from Scripts.Modules.Dice.dice_factory import DiceFactory
from Scripts.Modules.Dice.dice import DiceState
from Scripts.Modules.Database.database import DBManager
from Scripts.Modules.Storage.image_writer import write_frame_image

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
ANALYSIS_IMAGE_OUTPUT_DIR = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Scripts/Modules/Database/Captures')
SAMPLE_VIDEO_OUTPUT_DIR = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Captures/Videos/Unsorted')

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
                    view_single_image(main_queue)
                case QuCmd.IMAGE_FOLDER:
                    view_image_folder(main_queue)
                case QuCmd.SINGLE_VIDEO:
                    view_single_video(main_queue)
                case QuCmd.GATHER_SAMPLE_VIDEOS:
                    gather_sample_videos(main_queue)
                case QuCmd.GATHER_DICE_ANALYSIS_DATA:
                    gather_dice_analysis_data(main_queue)
                case QuCmd.VIEW_DICE_DATA:
                    view_dice_data(main_queue)
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
    print("2) View single image")
    print("3) Cycle through images in folder")
    print("4) View single video")
    print("5) Gather sample videos for model training")
    print("6) Gather data for dice analysis")
    print("7) View dice data")
    print("="*50)

    choice = input("Enter your choice (0-7): ").strip()

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
        case "3":
            if ENABLE_LOGGING:
                print("'Cycle through images in folder' selected.")
            queue.put(QueueData(cmd=QuCmd.IMAGE_FOLDER, data=None))
        case "4":
            if ENABLE_LOGGING:
                print("'View single video' selected.")
            queue.put(QueueData(cmd=QuCmd.SINGLE_VIDEO, data=None))
        case "5":
            if ENABLE_LOGGING:
                print("'Gather sample videos for model training' selected.")
            queue.put(QueueData(cmd=QuCmd.GATHER_SAMPLE_VIDEOS, data=None))
        case "6":
            if ENABLE_LOGGING:
                print("'Gather data for dice analysis' selected.")
            queue.put(QueueData(cmd=QuCmd.GATHER_DICE_ANALYSIS_DATA, data=None))
        case "7":
            if ENABLE_LOGGING:
                print("'View dice data' selected.")
            queue.put(QueueData(cmd=QuCmd.VIEW_DICE_DATA, data=None))
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
    """Load an image through FeedImage, show it in a Stream window, and return on Enter."""
    image_path = None
    for attempt in range(3):
        candidate_path = Path(input("Enter the image filepath: ").strip()).expanduser()

        if not candidate_path.is_file():
            print("Entry is not a valid file path.")
        elif candidate_path.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.bmp'}:
            print("Invalid file type.")
        else:
            image_path = candidate_path
            break

        if attempt < 2:
            print("Please try again.")

    if image_path is None:
        print("Returning to the main menu.")
        queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))
        return

    image_queue = mp.Queue()
    stream = None

    try:
        project_data = DataFactory.create_project_data(
            "project_data",
            process_queue=image_queue,
            logging=ENABLE_LOGGING,
        )
        FeedFactory.create_feed(
            "image",
            data=project_data,
            image_path=image_path,
            logging=ENABLE_LOGGING,
        )

        if not project_data.frames:
            raise ValueError("No frame was loaded from the requested image.")

        stream = Stream(logging=ENABLE_LOGGING)
        stream.show_frame(project_data.frames[-1], delay=1)

        print("Press Enter while the image window is focused to return to the main menu.")
        while True:
            key = cv2.waitKey(50)
            if key in (10, 13):
                break
            if stream.window and cv2.getWindowProperty(stream.window, cv2.WND_PROP_VISIBLE) < 1:
                break
    except Exception as e:
        print(f"main.py view_single_image() encountered an error: {e}.")
    finally:
        if stream is not None:
            stream.destroy()
        close_queue(image_queue)

    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))

def view_image_folder(queue: mp.Queue) -> None:
    """Cycle through folder images with YOLO overlays using window keyboard controls."""
    folder_path = None
    for attempt in range(3):
        candidate_path = Path(input("Enter the folder path containing images: ").strip()).expanduser()
        if candidate_path.is_dir():
            folder_path = candidate_path
            break

        print("Entry is not a valid folder path.")
        if attempt < 2:
            print("Please try again.")

    if folder_path is None:
        print("Returning to the main menu.")
        queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))
        return

    image_queue = mp.Queue()
    stream = None

    try:
        project_data = DataFactory.create_project_data(
            "project_data",
            process_queue=image_queue,
            logging=ENABLE_LOGGING,
        )
        multi_feed = FeedFactory.create_feed(
            "multi_image",
            data=project_data,
            folder_path=folder_path,
            logging=ENABLE_LOGGING,
        )
        model = YOLO(MODEL)
        stream = Stream(logging=ENABLE_LOGGING)

        print("Image folder controls (focus image window): 'n' next, 'p' previous, 'q' quit.")

        while True:
            if not project_data.frames:
                raise ValueError("No frame available for rendering.")

            current_frame = project_data.frames[-1]
            results = model(current_frame, verbose=False)
            rendered = results[0].plot()

            image_label = f"{multi_feed.current_image_number()} of {multi_feed.total_images()}"
            cv2.putText(
                rendered,
                image_label,
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            stream.show_frame(rendered, delay=1)

            if stream.window and cv2.getWindowProperty(stream.window, cv2.WND_PROP_VISIBLE) < 1:
                break

            key = cv2.waitKey(0) & 0xFF
            if key == ord('q'):
                break
            if key == ord('n'):
                if not multi_feed.next_image():
                    print(f"Already at last image: {multi_feed.current_image_path().name}")
                continue
            if key == ord('p'):
                if not multi_feed.previous_image():
                    print(f"Already at first image: {multi_feed.current_image_path().name}")
                continue
    except Exception as e:
        print(f"main.py view_image_folder() encountered an error: {e}.")
    finally:
        if stream is not None:
            stream.destroy()
        close_queue(image_queue)

    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))

def view_single_video(queue: mp.Queue) -> None:
    """Play or step through a video in a window with optional YOLO overlays."""
    video_path = None
    supported_formats = {'.mp4', '.mov', '.avi', '.mkv', '.m4v'}
    for attempt in range(3):
        candidate_path = Path(input("Enter the video filepath: ").strip()).expanduser()

        if not candidate_path.is_file():
            print("Entry is not a valid file path.")
        elif candidate_path.suffix.lower() not in supported_formats:
            print("Invalid file type.")
        else:
            video_path = candidate_path
            break

        if attempt < 2:
            print("Please try again.")

    if video_path is None:
        print("Returning to the main menu.")
        queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))
        return

    video_queue = mp.Queue()
    stream = None
    model = None

    try:
        project_data = DataFactory.create_project_data(
            "project_data",
            process_queue=video_queue,
            logging=ENABLE_LOGGING,
        )
        video_feed = FeedFactory.create_feed(
            "video",
            data=project_data,
            video_path=video_path,
            logging=ENABLE_LOGGING,
        )
        if MODEL is not None and MODEL.exists():
            model = YOLO(MODEL)

        stream = Stream(logging=ENABLE_LOGGING)
        is_playing = False

        print("Video controls (focus image window): space play/pause, 'n' next, 'p' previous, 'q' quit.")

        while True:
            if not project_data.frames:
                raise ValueError("No frame available for rendering.")

            frame = project_data.frames[-1]
            if model is not None:
                results = model(frame, verbose=False)
                rendered = results[0].plot()
            else:
                rendered = frame.copy()

            frame_label = f"{video_feed.current_frame_number()} of {video_feed.total_frames()}"
            cv2.putText(
                rendered,
                frame_label,
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            stream.show_frame(rendered, delay=1)

            if stream.window and cv2.getWindowProperty(stream.window, cv2.WND_PROP_VISIBLE) < 1:
                break

            key_delay = 33 if is_playing else 0
            key = cv2.waitKey(key_delay) & 0xFF

            if key == ord('q'):
                break
            if key == ord(' '):
                is_playing = not is_playing
                continue
            if key == ord('n'):
                is_playing = False
                video_feed.next_frame()
                continue
            if key == ord('p'):
                is_playing = False
                video_feed.previous_frame()
                continue

            if is_playing:
                if not video_feed.next_frame():
                    is_playing = False
    except Exception as e:
        print(f"main.py view_single_video() encountered an error: {e}.")
    finally:
        if stream is not None:
            stream.destroy()
        if 'video_feed' in locals() and video_feed is not None:
            video_feed.close()
        close_queue(video_queue)

    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))

def gather_sample_videos(queue: mp.Queue) -> None:
    """Capture buffered sample videos from the camera using window keyboard controls."""
    process_queue = mp.Queue()
    stream = None
    feed = None
    motor = None
    model = None

    def save_buffered_video(frames) -> Path | None:
        """Write the buffered frames to disk as an MP4 clip."""
        if not frames:
            return None

        SAMPLE_VIDEO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        output_path = SAMPLE_VIDEO_OUTPUT_DIR / f"{timestamp}.mp4"

        height, width = frames[0].shape[:2]
        writer = cv2.VideoWriter(
            str(output_path),
            cv2.VideoWriter_fourcc(*"mp4v"),
            30.0,
            (width, height),
        )
        try:
            if not writer.isOpened():
                raise ValueError(f"Failed to open video writer for {output_path}")
            for frame in frames:
                writer.write(frame)
        finally:
            writer.release()

        if ENABLE_LOGGING:
            print(f"  -> Saved sample video: {output_path}")
        return output_path

    try:
        project_data = DataFactory.create_project_data(
            "project_data",
            process_queue=process_queue,
            logging=ENABLE_LOGGING,
            model_path=MODEL,
        )
        feed = FeedFactory.create_feed(
            "camera",
            data=project_data,
            process_queue=process_queue,
            logging=ENABLE_LOGGING,
        )
        stream = Stream(logging=ENABLE_LOGGING)
        motor = Motor(logging=ENABLE_LOGGING, main_queue=queue)
        if MODEL.exists():
            model = YOLO(MODEL)

        motor.move_to_uncap()
        time.sleep(1)
        feed.ready_for_frames(True)

        print("Sample video controls (focus image window): space save+flip, 'q' save+quit.")

        last_rendered_frame = None
        while True:
            try:
                item = process_queue.get(timeout=0.01)
                if item.cmd == QuCmd.NEW_FRAME_CAPTURED:
                    frame = item.data
                    project_data.new_frame(frame)

                    if model is not None:
                        results = model(frame, verbose=False)
                        project_data.new_result(results[0])
                        rendered = results[0].plot()
                    else:
                        rendered = frame.copy()

                    last_rendered_frame = rendered
                    stream.show_frame(rendered, delay=1)
            except Empty:
                if last_rendered_frame is not None:
                    stream.show_frame(last_rendered_frame, delay=1)

            if stream.window and cv2.getWindowProperty(stream.window, cv2.WND_PROP_VISIBLE) < 1:
                save_buffered_video(project_data.frames)
                break

            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):
                save_buffered_video(project_data.frames)
                project_data.clear_frames()
                motor.flip()
                continue
            if key == ord('q'):
                save_buffered_video(project_data.frames)
                break
    except Exception as e:
        print(f"main.py gather_sample_videos() encountered an error: {e}.")
    finally:
        if feed is not None:
            feed.destroy()
        if stream is not None:
            stream.destroy()
        if motor is not None:
            motor.close()
        close_queue(process_queue)

    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))

def gather_dice_analysis_data(queue: mp.Queue) -> None:
    """
    This function is responsible for gathering data for dice analysis.  This is a placeholder function and does not contain any actual logic for gathering data.
    """
    print("\n" + "="*50)
    print("main.py gather_dice_analysis_data() Starting data gathering process for dice analysis.")
    print("="*50 + "\n")

    process_queue = mp.Queue() # Use this to notify the process with data and routine updates
    initial_time = time.perf_counter() # Track how long we've been gathering data for to prevent any potential issues with gathering data for too long.
    max_process_time = 20 # If we've been gathering data for more than this amount of time, we should exit to prevent any potential issues.
    max_time_before_flip = 4 # If we've been gathering data for more than this amount of time, we should flip the tower to get a new roll.
    motor_resetting = False # Track whether the motor is currently resetting to prevent us from trying to analyze frames while the tower is flipping.

    try:
        if ENABLE_LOGGING:
            print("main.py gather_dice_analysis_data() Initializing supporting class instances.")
        process_data = DataFactory.create_project_data("project_data", logging=ENABLE_LOGGING, model_path=MODEL, process_queue=process_queue)
        feed = FeedFactory.create_feed("camera", data=process_data, process_queue=process_queue, logging=ENABLE_LOGGING)
        stream = Stream(logging=ENABLE_LOGGING)
        dice = DiceFactory.create_dice("six_sided_pips", logging=ENABLE_LOGGING, data=process_data)
        motor = Motor(logging=False, main_queue=queue)
        # TODO: Get user input for dice ID at some point.  For now, we can just let it generate an id as we are in dev mode.
        db = DBManager(dice_id=None, logging=ENABLE_LOGGING) # Initialize the database manager with a test dice ID.  In the future, we can make this dynamic based on user input or a dice tracking system.
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
                print("main.py on_analyze_frame_done() Frame analysis complete, processing results.")
            rendered, result = f.result()
            process_data.new_result(result) # Store the results of the processed frame in the data object.
            process_queue.put(QueueData(cmd=QuCmd.SHOW_FRAME, data=rendered)) # Notify the main process that a new frame is ready for display.
            process_queue.put(QueueData(cmd=QuCmd.EVALUATE_DICE_STATE, data=None)) # After showing the frame, we want to evaluate the state of the dice to know if we need to flip the tower for a new roll.
            if ENABLE_LOGGING:
                print("  --> Frame analysis results processed and SHOW_FRAME & EVALUATE_DICE_STATE commands sent to process queue.")
        except Exception as e:
            print(f"main.py on_analyze_frame_done() encountered an error: {e}.")

    def persist_settled_roll(frame, dice_id: str, dice_value: str):
        """Persist settled roll artifacts without blocking the main loop."""
        image_path = write_frame_image(
            frame,
            ANALYSIS_IMAGE_OUTPUT_DIR / dice_id,
            dice_id=dice_id,
            dice_value=dice_value,
        )
        db.write_test_result(dice_value, image_path, wait=False)

    def on_persist_settled_roll_done(f):
        try:
            f.result()
        except Exception as e:
            print(f"main.py on_persist_settled_roll_done() encountered an error: {e}.")
    
    def close():
        if ENABLE_LOGGING:
            print("main.py gather_dice_analysis_data() close() called, closing all supporting class instances.")
        db.wait_for_writes()
        db.stop_writer()
        feed.destroy() # Ensure we release the camera feed when we're done.
        stream.destroy() # Ensure we close the video stream when we're done.
        motor.close() # Ensure we close the motor connection when we're done.
        if ENABLE_LOGGING:
            print("main.py gather_dice_analysis_data() All supporting class instances closed.")
        process_queue.cancel_join_thread()
        process_queue.close() # Close the process queue to clean up resources.

    if ENABLE_LOGGING:
        print("main.py gather_dice_analysis_data() Moving to uncap position.")
    motor.move_to_uncap() # Initial positioning
    time.sleep(1) # Wait for the camera to stabilize before we begin capturing frames.

    if ENABLE_LOGGING:
        print("main.py gather_dice_analysis_data() Motor is in uncap position, starting main data gathering loop.")
    process_queue.put(QueueData(cmd=QuCmd.GET_NEXT_SAMPLE, data=None)) # Start getting a new sample
    feed.ready_for_frames(True) # Now that we're ready to process frames, we can allow the feed to put frames in the process queue.

    with ProcessPoolExecutor(
        initializer=init_worker,
        initargs=(MODEL,)
    ) as executor, ThreadPoolExecutor(max_workers=2, thread_name_prefix="image-writer") as image_executor:
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
                            print("main.py gather_dice_analysis_data() GET_NEXT_SAMPLE command received, preparing for next sample.")
                        process_data.clear_frames() # Clear any frames that were captured during the initial positioning.
                        motor.flip() # Flip the tower to start the next roll.
                    case QuCmd.NEW_FRAME_CAPTURED:
                        if ENABLE_LOGGING:
                            print("main.py gather_dice_analysis_data() NEW_FRAME_CAPTURED command received.")
                        if not motor_resetting:
                            if ENABLE_LOGGING:
                                print("  -> Motor is steady, analyzing frame.")
                            process_data.new_frame(item.data) # Store the new frame in the data object for tracking and potential future use.
                            future_new_frame = executor.submit(analyze_frame_worker, item.data)
                            future_new_frame.add_done_callback(on_analyze_frame_done) # Analyze the frame in a separate process and show the results in the stream when it's done.
                        else:
                            if ENABLE_LOGGING:
                                print("  -> Motor is resetting, skipping frame analysis.")
                            process_queue.put(QueueData(cmd=QuCmd.SHOW_FRAME, data=item.data)) # Even if we're not analyzing the frame, we should still show it in the stream so the user can see what's going on.
                    case QuCmd.SHOW_FRAME:
                        if ENABLE_LOGGING:
                            print("main.py gather_dice_analysis_data() SHOW_FRAME command received, calling stream.show_frame().")
                        stream.show_frame(item.data) # Show the frame in the stream when the analysis is done
                    case QuCmd.EVALUATE_DICE_STATE:
                        if ENABLE_LOGGING:
                            print("main.py gather_dice_analysis_data() EVALUATE_DICE_STATE command received, evaluating dice state.")
                        # I want determine if it is time to start a new roll
                        dice.set_dice_state()
                        if ENABLE_LOGGING:
                            print(f"  -> Current dice state: {dice.dice_state}")
                        # if (dice.dice_state == DiceState.UNKNOWN) and (len(process_data.frames) > process_data.fps * max_time_before_flip): # If the dice state has been unknown for longer than the max time before flip, we should reset the tower to get a new roll.
                        if (dice.dice_state == DiceState.UNKNOWN) and (len(process_data.frames) > process_data.fps * max_time_before_flip): # If the dice state has been unknown for longer than the max time before flip, we should reset the tower to get a new roll.
                            if ENABLE_LOGGING:
                                print("************************************************************")
                                print(f"  -> Dice state is UNKNOWN for longer than {max_time_before_flip} seconds, resetting tower for new roll.")
                                print("************************************************************")
                            motor_resetting = True
                            process_queue.put(QueueData(cmd=QuCmd.RESET_TOWER, data=None))
                            # I want to continue showing the camera feed, but I don't want to include this in evaluation.
                        elif dice.dice_state == DiceState.SETTLED:
                            if ENABLE_LOGGING:
                                print("************************************************************")
                                print("  -> Dice state is SETTLED, capturing dice value and starting new roll.")
                                print("************************************************************")
                            value = dice.get_dice_value(process_data.results[-1]) # Get the value of the dice based on the most recent analyzed frame.
                            
                            if ENABLE_LOGGING:
                                print(f"  -> Current dice value: {value}")

                            if not db.dice_id:
                                db.generate_id()

                            future_persist_roll = image_executor.submit(
                                persist_settled_roll,
                                process_data.frames[-1].copy(),
                                str(db.dice_id),
                                str(value),
                            )
                            future_persist_roll.add_done_callback(on_persist_settled_roll_done)
                            process_queue.put(QueueData(cmd=QuCmd.GET_NEXT_SAMPLE, data=None)) # Start getting a new sample
                    case QuCmd.RESET_TOWER:
                        if ENABLE_LOGGING:
                            print("main.py gather_dice_analysis_data() RESET_TOWER command received, resetting tower for new roll.")
                        motor.reset_position() # Show the last captured frame in the stream while we reset the tower so the user can see what's going on.
                    case QuCmd.MOTOR_RESET_COMPLETE:
                        if ENABLE_LOGGING:
                            print("main.py gather_dice_analysis_data() MOTOR_RESET_COMPLETE command received, motor has completed reset.")
                        motor_resetting = False # Now that the motor has completed the reset, we can start analyzing frames again.
                        process_queue.put(QueueData(cmd=QuCmd.GET_NEXT_SAMPLE, data=None)) # Start getting a new sample now that the motor has completed the reset.
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

def view_dice_data(queue: mp.Queue) -> None:
    """Print all test results for a user-selected dice ID."""
    db = DBManager(logging=ENABLE_LOGGING)

    # Print every known dice ID
    all_ids = db.execute_read_one(
        "SELECT GROUP_CONCAT(DISTINCT dice_id) FROM test_results"
    )
    if all_ids and all_ids[0]:
        print("\nDice IDs in database: " + all_ids[0])
    else:
        print("\nNo data found in the database.")
        input("Press Enter to return to the main menu...")
        queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))
        return

    dice_id = input("Enter the dice ID to view: ").strip()
    results = db.read_results_for_die(dice_id)

    if not results:
        print(f"No results found for dice ID '{dice_id}'.")
    else:
        print(f"\n{'Timestamp':<30} {'Value':<8} Image")
        print("-" * 80)
        for row in results:
            image_name = Path(row["image"]).name
            print(f"{row['timestamp']:<30} {row['dice_result']:<8} {image_name}")

    input("\nPress Enter to return to the main menu...")
    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))

if __name__ == "__main__":
    main()
    print("Die Tester Application has terminated.")
