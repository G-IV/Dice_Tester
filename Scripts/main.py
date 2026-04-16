# Parallel processing related imports
import multiprocessing as mp
from queue import Empty

# Project module imports
from Scripts.Modules.queue_data import QueueData, Command as QuCmd
from Scripts.Modules.Stream.stream import Stream
from Scripts.Modules.Motor.ad2 import Motor
from Scripts.Modules.Data.data_factory import DataFactory
from Scripts.Modules.Feed.feed_factory import FeedFactory
from Scripts.Modules.Database.database import DBManager
from Scripts.Modules.Workflow.analysis_config import AnalysisConfig
from Scripts.Modules.Workflow.dice_analysis_session import run_dice_analysis_session
from Scripts.Modules.Workflow.sample_video_session import run_sample_video_session

# Class support imports
from pathlib import Path

# Image processing imports
import cv2
from ultralytics import YOLO

# Constants
ENABLE_LOGGING = True
MODEL = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Pips/3_YOLO/Patterns/runs/weights/best.pt')
ANALYSIS_IMAGE_OUTPUT_DIR = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Scripts/Modules/Database/Captures')
SAMPLE_VIDEO_OUTPUT_DIR = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Captures/Videos/Unsorted')
ANALYSIS_CONFIG = AnalysisConfig(
    model_path=MODEL,
    analysis_image_output_dir=ANALYSIS_IMAGE_OUTPUT_DIR,
    sample_video_output_dir=SAMPLE_VIDEO_OUTPUT_DIR,
)


def close_queue(queue: mp.Queue) -> None:
    """Close a multiprocessing queue and stop join tracking."""
    if ENABLE_LOGGING:
        print('main.py close_queue()')

    queue.cancel_join_thread()
    queue.close()

    if ENABLE_LOGGING:
        print('  --> Queue closed, waiting for remaining items to be processed...')


def main() -> None:
    """Starting point for the application."""
    print('==================================')
    print('Starting the Tester Application...')
    print('==================================')

    main_queue = mp.Queue()
    main_queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))

    while True:
        try:
            item = main_queue.get(timeout=1)
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
            pass
        except Exception as e:
            print(f'main.py main() encountered an unexpected error: {e}. Returning to the main menu.')
            break

    close_queue(main_queue)


def top_level(queue: mp.Queue) -> None:
    """Present the user with the application menu."""
    print('\n' + '=' * 50)
    print('Select an option:')
    print('0) Exit')
    print('1) Move to uncap position')
    print('2) View single image')
    print('3) Cycle through images in folder')
    print('4) View single video')
    print('5) Gather sample videos for model training')
    print('6) Gather data for dice analysis')
    print('7) View dice data')
    print('=' * 50)

    choice = input('Enter your choice (0-7): ').strip()

    match choice:
        case '0':
            if ENABLE_LOGGING:
                print("'Exit' selected.")
            queue.put(QueueData(cmd=QuCmd.EXIT, data=None))
        case '1':
            if ENABLE_LOGGING:
                print("'Move to uncap position' selected.")
            queue.put(QueueData(cmd=QuCmd.MOVE_TO_UNCAP, data=None))
        case '2':
            if ENABLE_LOGGING:
                print("'View single image' selected.")
            queue.put(QueueData(cmd=QuCmd.SINGLE_IMAGE, data=None))
        case '3':
            if ENABLE_LOGGING:
                print("'Cycle through images in folder' selected.")
            queue.put(QueueData(cmd=QuCmd.IMAGE_FOLDER, data=None))
        case '4':
            if ENABLE_LOGGING:
                print("'View single video' selected.")
            queue.put(QueueData(cmd=QuCmd.SINGLE_VIDEO, data=None))
        case '5':
            if ENABLE_LOGGING:
                print("'Gather sample videos for model training' selected.")
            queue.put(QueueData(cmd=QuCmd.GATHER_SAMPLE_VIDEOS, data=None))
        case '6':
            if ENABLE_LOGGING:
                print("'Gather data for dice analysis' selected.")
            queue.put(QueueData(cmd=QuCmd.GATHER_DICE_ANALYSIS_DATA, data=None))
        case '7':
            if ENABLE_LOGGING:
                print("'View dice data' selected.")
            queue.put(QueueData(cmd=QuCmd.VIEW_DICE_DATA, data=None))
        case _:
            if ENABLE_LOGGING:
                print(f'You selected: {choice}. This option is not implemented yet.')
            queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))


def move_to_uncap(queue: mp.Queue) -> None:
    """Move the camera to the uncap position."""
    if ENABLE_LOGGING:
        print('Moving to uncap position...)')
    try:
        motor = Motor(logging=ENABLE_LOGGING, main_queue=queue)
    except Exception as e:
        if ENABLE_LOGGING:
            print(f'main.py move_to_uncap() encountered an error while initializing the motor: {e}. Returning to the main menu.')
        queue.put(QueueData(cmd=QuCmd.EXIT, data=None))
        return

    motor.move_to_uncap()
    input('Press Enter to return to the main menu...')
    motor.close()
    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))


def view_single_image(queue: mp.Queue) -> None:
    """Load an image through FeedImage, show it in a Stream window, and return on Enter."""
    image_path = None
    for attempt in range(3):
        candidate_path = Path(input('Enter the image filepath: ').strip()).expanduser()

        if not candidate_path.is_file():
            print('Entry is not a valid file path.')
        elif candidate_path.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.bmp'}:
            print('Invalid file type.')
        else:
            image_path = candidate_path
            break

        if attempt < 2:
            print('Please try again.')

    if image_path is None:
        print('Returning to the main menu.')
        queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))
        return

    image_queue = mp.Queue()
    stream = None

    try:
        project_data = DataFactory.create_project_data(
            'project_data',
            process_queue=image_queue,
            logging=ENABLE_LOGGING,
        )
        FeedFactory.create_feed(
            'image',
            data=project_data,
            image_path=image_path,
            logging=ENABLE_LOGGING,
        )

        if not project_data.frames:
            raise ValueError('No frame was loaded from the requested image.')

        stream = Stream(logging=ENABLE_LOGGING)
        stream.show_frame(project_data.frames[-1], delay=1)

        print('Press Enter while the image window is focused to return to the main menu.')
        while True:
            key = cv2.waitKey(50)
            if key in (10, 13):
                break
            if stream.window and cv2.getWindowProperty(stream.window, cv2.WND_PROP_VISIBLE) < 1:
                break
    except Exception as e:
        print(f'main.py view_single_image() encountered an error: {e}.')
    finally:
        if stream is not None:
            stream.destroy()
        close_queue(image_queue)

    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))


def view_image_folder(queue: mp.Queue) -> None:
    """Cycle through folder images with YOLO overlays using window keyboard controls."""
    folder_path = None
    for attempt in range(3):
        candidate_path = Path(input('Enter the folder path containing images: ').strip()).expanduser()
        if candidate_path.is_dir():
            folder_path = candidate_path
            break

        print('Entry is not a valid folder path.')
        if attempt < 2:
            print('Please try again.')

    if folder_path is None:
        print('Returning to the main menu.')
        queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))
        return

    image_queue = mp.Queue()
    stream = None

    try:
        project_data = DataFactory.create_project_data(
            'project_data',
            process_queue=image_queue,
            logging=ENABLE_LOGGING,
        )
        multi_feed = FeedFactory.create_feed(
            'multi_image',
            data=project_data,
            folder_path=folder_path,
            logging=ENABLE_LOGGING,
        )
        model = YOLO(ANALYSIS_CONFIG.model_path)
        stream = Stream(logging=ENABLE_LOGGING)

        print("Image folder controls (focus image window): 'n' next, 'p' previous, 'q' quit.")

        while True:
            if not project_data.frames:
                raise ValueError('No frame available for rendering.')

            current_frame = project_data.frames[-1]
            results = model(current_frame, verbose=False)
            rendered = results[0].plot()

            image_label = f'{multi_feed.current_image_number()} of {multi_feed.total_images()}'
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
                    print(f'Already at last image: {multi_feed.current_image_path().name}')
                continue
            if key == ord('p'):
                if not multi_feed.previous_image():
                    print(f'Already at first image: {multi_feed.current_image_path().name}')
                continue
    except Exception as e:
        print(f'main.py view_image_folder() encountered an error: {e}.')
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
        candidate_path = Path(input('Enter the video filepath: ').strip()).expanduser()

        if not candidate_path.is_file():
            print('Entry is not a valid file path.')
        elif candidate_path.suffix.lower() not in supported_formats:
            print('Invalid file type.')
        else:
            video_path = candidate_path
            break

        if attempt < 2:
            print('Please try again.')

    if video_path is None:
        print('Returning to the main menu.')
        queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))
        return

    video_queue = mp.Queue()
    stream = None
    model = None

    try:
        project_data = DataFactory.create_project_data(
            'project_data',
            process_queue=video_queue,
            logging=ENABLE_LOGGING,
        )
        video_feed = FeedFactory.create_feed(
            'video',
            data=project_data,
            video_path=video_path,
            logging=ENABLE_LOGGING,
        )
        if ANALYSIS_CONFIG.model_path.exists():
            model = YOLO(ANALYSIS_CONFIG.model_path)

        stream = Stream(logging=ENABLE_LOGGING)
        is_playing = False

        print("Video controls (focus image window): space play/pause, 'n' next, 'p' previous, 'q' quit.")

        while True:
            if not project_data.frames:
                raise ValueError('No frame available for rendering.')

            frame = project_data.frames[-1]
            if model is not None:
                results = model(frame, verbose=False)
                rendered = results[0].plot()
            else:
                rendered = frame.copy()

            frame_label = f'{video_feed.current_frame_number()} of {video_feed.total_frames()}'
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
        print(f'main.py view_single_video() encountered an error: {e}.')
    finally:
        if stream is not None:
            stream.destroy()
        if 'video_feed' in locals() and video_feed is not None:
            video_feed.close()
        close_queue(video_queue)

    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))


def gather_sample_videos(queue: mp.Queue) -> None:
    """Capture buffered sample videos from the camera using the shared sample-video session."""
    run_sample_video_session(queue, ANALYSIS_CONFIG, logging=ENABLE_LOGGING)
    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))


def gather_dice_analysis_data(queue: mp.Queue) -> None:
    """Gather dice analysis data using the shared dice-analysis session."""
    target_samples = None
    for attempt in range(3):
        raw_value = input('Enter number of samples to collect: ').strip()
        if raw_value.isdigit() and int(raw_value) > 0:
            target_samples = int(raw_value)
            break
        print('Please enter a positive integer.')

    if target_samples is None:
        print('Returning to the main menu.')
        queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))
        return

    print('\n' + '=' * 50)
    print(
        'main.py gather_dice_analysis_data() Starting data gathering process '
        f'for {target_samples} samples.'
    )
    print('=' * 50 + '\n')
    run_dice_analysis_session(
        queue,
        ANALYSIS_CONFIG,
        target_samples=target_samples,
        logging=ENABLE_LOGGING,
    )
    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))


def view_dice_data(queue: mp.Queue) -> None:
    """Print all test results for a user-selected dice ID."""
    db = DBManager(logging=ENABLE_LOGGING)

    all_ids = db.execute_read_one(
        'SELECT GROUP_CONCAT(DISTINCT dice_id) FROM test_results'
    )
    if all_ids and all_ids[0]:
        print('\nDice IDs in database: ' + all_ids[0])
    else:
        print('\nNo data found in the database.')
        input('Press Enter to return to the main menu...')
        queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))
        return

    dice_id = input('Enter the dice ID to view: ').strip()
    results = db.read_results_for_die(dice_id)

    if not results:
        print(f"No results found for dice ID '{dice_id}'.")
    else:
        print(f"\n{'Timestamp':<30} {'Value':<8} Image")
        print('-' * 80)
        for row in results:
            image_name = Path(row['image']).name
            print(f"{row['timestamp']:<30} {row['dice_result']:<8} {image_name}")

    input('\nPress Enter to return to the main menu...')
    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))


if __name__ == '__main__':
    main()
    print('Die Tester Application has terminated.')