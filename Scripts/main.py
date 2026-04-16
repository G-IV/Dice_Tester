# Parallel processing related imports
import multiprocessing as mp
from queue import Empty

# Project module imports
from Scripts.Modules.Analysis.reporting import analyze_results, build_summary_lines, write_report
from Scripts.Modules.Database.database import DBManager
from Scripts.Modules.queue_data import QueueData, Command as QuCmd
from Scripts.Modules.Stream.stream import Stream
from Scripts.Modules.Motor.ad2 import Motor
from Scripts.Modules.Data.data_factory import DataFactory
from Scripts.Modules.Feed.feed_factory import FeedFactory
from Scripts.Modules.Storage.capture_migration import migrate_capture_layout
from Scripts.Modules.Stream.overlay import FrameContext, composite_with_panel
from Scripts.Modules.Workflow.analysis_config import AnalysisConfig
from Scripts.Modules.Workflow.dice_analysis_session import run_dice_analysis_session
from Scripts.Modules.Workflow.sample_video_session import run_sample_video_session

# Class support imports
from pathlib import Path
import re

# Image processing imports
import cv2
from ultralytics import YOLO

# Constants
ENABLE_LOGGING = True
MODEL = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Pips/3_YOLO/Patterns/runs/weights/best.pt')
ANALYSIS_IMAGE_OUTPUT_DIR = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Scripts/Modules/Database/Captures')
SAMPLE_VIDEO_OUTPUT_DIR = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Captures/Videos/Unsorted')
LEGACY_ANALYSIS_REPORT_OUTPUT_DIR = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Captures/Images/Results')
ANALYSIS_CONFIG = AnalysisConfig(
    model_path=MODEL,
    analysis_image_output_dir=ANALYSIS_IMAGE_OUTPUT_DIR,
    sample_video_output_dir=SAMPLE_VIDEO_OUTPUT_DIR,
    report_output_dir=ANALYSIS_IMAGE_OUTPUT_DIR,
)
MIGRATION_HAS_RUN = False


def _compute_roll_stats(rows: list[dict], dice_sides: int | None = None) -> tuple[int | None, float | None, float | None, dict[int, int]]:
    face_counts: dict[int, int] = {}
    total = 0
    weighted_sum = 0
    for row in rows:
        try:
            face = int(row['dice_result'])
        except (TypeError, ValueError):
            continue
        face_counts[face] = face_counts.get(face, 0) + 1
        total += 1
        weighted_sum += face

    if total == 0:
        return None, None, None, {}

    mean_roll = weighted_sum / total
    # Infer sides from the highest face seen if not explicitly provided
    if dice_sides is None and face_counts:
        dice_sides = max(face_counts.keys())
    expected_mean = ((dice_sides + 1) / 2) if dice_sides else None
    return total, mean_roll, expected_mean, face_counts


def _parse_filename_token(stem: str, key: str) -> str | None:
    pattern = rf'(?:^|__)' + re.escape(key) + r'-([^_]+(?:_[^_]+)*)'
    match = re.search(pattern, stem)
    return match.group(1) if match else None


def _parse_video_metadata(video_path: Path) -> tuple[str | None, int | None]:
    stem = video_path.stem
    dice_id = _parse_filename_token(stem, 'die')
    sides_token = _parse_filename_token(stem, 'sides')
    try:
        dice_sides = int(sides_token) if sides_token and sides_token != 'unknown' else None
    except ValueError:
        dice_sides = None
    if dice_id == 'unknown':
        dice_id = None
    return dice_id, dice_sides


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
    db = DBManager(logging=False)
    image_row_lookup: dict[Path, dict] = {}
    rows_by_dice_id: dict[str, list[dict]] = {}

    for row in db.read_all_results():
        image_path = Path(row['image']).expanduser().resolve()
        image_row_lookup[image_path] = row
        dice_id_key = str(row['dice_id'])
        rows_by_dice_id.setdefault(dice_id_key, []).append(row)

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
            result = results[0]
            detections = []
            if result.boxes is not None:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    name = result.names.get(cls_id, str(cls_id))
                    detections.append({'name': name, 'conf': conf})

            current_image_path = multi_feed.current_image_path().expanduser().resolve()
            matched_row = image_row_lookup.get(current_image_path)
            if matched_row is not None:
                dice_id = str(matched_row['dice_id'])
                dice_sides = matched_row.get('dice_sides')
                all_rows_for_die = rows_by_dice_id.get(dice_id, [])
                total_rolls, mean_roll, expected_mean, face_counts = _compute_roll_stats(
                    all_rows_for_die,
                    dice_sides=dice_sides,
                )
            else:
                dice_id = None
                dice_sides = None
                total_rolls, mean_roll, expected_mean, face_counts = (None, None, None, {})

            ctx = FrameContext(
                detections=detections,
                image_index=multi_feed.current_image_number(),
                image_total=multi_feed.total_images(),
                image_name=multi_feed.current_image_path().name,
                db_linked=matched_row is not None,
                dice_id=dice_id,
                dice_sides=dice_sides,
                total_rolls=total_rolls,
                mean_roll=mean_roll,
                expected_mean=expected_mean,
                face_counts=face_counts,
            )
            stream.show_frame(composite_with_panel(rendered, ctx), delay=1)

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

    video_dice_id, video_dice_sides = _parse_video_metadata(video_path)
    video_total_rolls = None
    video_mean_roll = None
    video_expected_mean = None
    video_face_counts: dict[int, int] = {}
    if video_dice_id is not None:
        db = DBManager(logging=False)
        rows = db.read_results_for_die(video_dice_id)
        if rows:
            if video_dice_sides is None:
                recorded_sides = {row['dice_sides'] for row in rows if row['dice_sides'] is not None}
                if len(recorded_sides) == 1:
                    video_dice_sides = recorded_sides.pop()
            video_total_rolls, video_mean_roll, video_expected_mean, video_face_counts = _compute_roll_stats(
                rows,
                dice_sides=video_dice_sides,
            )

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
            if model is not None:
                result = results[0]
                detections = []
                if result.boxes is not None:
                    for box in result.boxes:
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        name = result.names.get(cls_id, str(cls_id))
                        detections.append({'name': name, 'conf': conf})
            else:
                detections = []
            ctx = FrameContext(
                detections=detections,
                frame_number=video_feed.current_frame_number(),
                frame_total=video_feed.total_frames(),
                db_linked=video_total_rolls is not None,
                dice_id=video_dice_id,
                dice_sides=video_dice_sides,
                total_rolls=video_total_rolls,
                mean_roll=video_mean_roll,
                expected_mean=video_expected_mean,
                face_counts=video_face_counts,
            )
            stream.show_frame(composite_with_panel(rendered, ctx), delay=1)

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
    dice_id_entry = input('Optional dice ID for video filename metadata [blank to skip]: ').strip()
    dice_id = dice_id_entry if dice_id_entry else None

    sides_entry = input('Optional dice sides for video filename metadata [blank to skip]: ').strip()
    if sides_entry:
        try:
            dice_sides = int(sides_entry)
        except ValueError:
            print(f"Invalid sides entry '{sides_entry}'. Metadata will use unknown sides.")
            dice_sides = None
    else:
        dice_sides = None

    run_sample_video_session(
        queue,
        ANALYSIS_CONFIG,
        dice_id=dice_id,
        dice_sides=dice_sides,
        logging=ENABLE_LOGGING,
    )
    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))


def gather_dice_analysis_data(queue: mp.Queue) -> None:
    """Gather dice analysis data using the shared dice-analysis session."""
    dice_id_entry = input('Optional dice ID for analysis session [blank to auto-generate]: ').strip()
    requested_dice_id = dice_id_entry if dice_id_entry else None

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
    dice_id = run_dice_analysis_session(
        queue,
        ANALYSIS_CONFIG,
        target_samples=target_samples,
        dice_id=requested_dice_id,
        logging=ENABLE_LOGGING,
    )

    if dice_id is not None:
        try:
            db = DBManager(logging=ENABLE_LOGGING)
            rows = db.read_results_for_die(dice_id)
            if rows:
                recorded_sides = {row['dice_sides'] for row in rows if row['dice_sides'] is not None}
                dice_sides = recorded_sides.pop() if len(recorded_sides) == 1 else 6
                report = analyze_results(dice_id=dice_id, rows=rows, dice_sides=dice_sides)
                report_path = write_report(report, ANALYSIS_CONFIG.report_output_dir / dice_id)
                print('\n' + '=' * 50)
                for line in build_summary_lines(report):
                    print(line)
                print(f'Report written to: {report_path}')
                print('=' * 50)
        except Exception as e:
            print(f'main.py gather_dice_analysis_data() failed to write report: {e}.')

    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))


def view_dice_data(queue: mp.Queue) -> None:
    """Re-analyze and regenerate the HTML report for any existing dice ID, with optional side override."""
    global MIGRATION_HAS_RUN

    db = DBManager(logging=ENABLE_LOGGING)

    if not MIGRATION_HAS_RUN:
        try:
            migration_summary = migrate_capture_layout(
                db,
                captures_root=ANALYSIS_CONFIG.analysis_image_output_dir,
                legacy_reports_root=LEGACY_ANALYSIS_REPORT_OUTPUT_DIR,
                logging=ENABLE_LOGGING,
            )
            MIGRATION_HAS_RUN = True
            if migration_summary.changed():
                print('Capture layout migration applied for legacy files.')
        except Exception as e:
            print(f'main.py view_dice_data() migration helper encountered an error: {e}.')

    all_ids = db.list_dice_ids()
    if not all_ids:
        print('\nNo data found in the database.')
        input('Press Enter to return to the main menu...')
        queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))
        return

    print('\nDice IDs in database: ' + ', '.join(all_ids))

    dice_id = input('Enter the dice ID to view: ').strip()
    results = db.read_results_for_die(dice_id)

    if not results:
        print(f"No results found for dice ID '{dice_id}'.")
    else:
        recorded_sides = {row['dice_sides'] for row in results if row['dice_sides'] is not None}
        if len(recorded_sides) > 1:
            print(f"Dice ID '{dice_id}' has inconsistent side counts in the database: {sorted(recorded_sides)}")
        else:
            default_sides = recorded_sides.pop() if recorded_sides else 6
            sides_entry = input(f'Enter the number of sides for analysis [{default_sides}]: ').strip()

            try:
                dice_sides = default_sides if not sides_entry else int(sides_entry)
                report = analyze_results(dice_id=dice_id, rows=results, dice_sides=dice_sides)
            except ValueError as error:
                print(f'Unable to analyze dice data: {error}')
            else:
                report_path = write_report(report, ANALYSIS_CONFIG.report_output_dir / dice_id)

                for line in build_summary_lines(report):
                    print(line)

                print(f'Report written to: {report_path}')
                print('Most recent captured images:')
                for row in results[-5:]:
                    print(f"  {row['timestamp']} -> {Path(row['image']).name}")

    input('\nPress Enter to return to the main menu...')
    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))


if __name__ == '__main__':
    main()
    print('Die Tester Application has terminated.')