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
from Scripts.Modules.Dice.dice_factory import DiceFactory
from Scripts.Modules.Storage.capture_migration import migrate_capture_layout
from Scripts.Modules.Stream.overlay import FrameContext, composite_with_panel
from Scripts.Modules.Workflow.analysis_config import AnalysisConfig
from Scripts.Modules.Workflow.dice_analysis_session import run_dice_analysis_session
from Scripts.Modules.Workflow.sample_video_session import run_sample_video_session

# Class support imports
from pathlib import Path
from datetime import datetime
import re
import shutil

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


_SUPPORTED_IMAGE_SUFFIXES = {'.jpg', '.jpeg', '.png', '.bmp'}


def _iter_capture_image_files(capture_dir: Path) -> list[Path]:
    return sorted(
        path for path in capture_dir.rglob('*')
        if path.is_file()
        and path.suffix.lower() in _SUPPORTED_IMAGE_SUFFIXES
    )


def _move_file_unique(source: Path, target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    destination = target_dir / source.name
    if source.resolve() == destination.resolve():
        return destination

    if destination.exists():
        stem = destination.stem
        suffix = destination.suffix
        index = 1
        while True:
            candidate = target_dir / f'{stem}_{index}{suffix}'
            if not candidate.exists():
                destination = candidate
                break
            index += 1

    shutil.move(str(source), str(destination))
    return destination


def _count_matching_detections(result, class_id: int) -> int:
    boxes = getattr(result, 'boxes', None)
    classes = getattr(boxes, 'cls', None) if boxes is not None else None
    if classes is None:
        return 0

    try:
        matches = classes == class_id
        nonzero = matches.nonzero(as_tuple=True)
        if isinstance(nonzero, tuple):
            return len(nonzero[0])
        return len(nonzero)
    except Exception:
        try:
            return sum(1 for value in classes if int(value) == class_id)
        except TypeError:
            return 0


def _write_empty_results_report(dice_id: str, output_dir: Path, total_images: int, unknown_images: int) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / 'results.html'
    generated_at = datetime.now().isoformat(timespec='seconds')
    report_path.write_text(
        f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dice {dice_id} analysis report</title>
  <style>
    body {{ font-family: Georgia, serif; margin: 0; padding: 32px; background: #f7f0e5; color: #1f1a17; }}
    main {{ max-width: 860px; margin: 0 auto; background: rgba(255, 250, 242, 0.95); border: 1px solid rgba(79, 59, 43, 0.16); border-radius: 24px; padding: 28px; }}
    h1 {{ margin-top: 0; }}
    .muted {{ color: #6e6258; }}
  </style>
</head>
<body>
  <main>
    <p class="muted">Dice analysis report</p>
    <h1>Die {dice_id} has no validated samples</h1>
    <p>Processed {total_images} image(s) at {generated_at}.</p>
    <p>{unknown_images} image(s) remain in the Unknown folder for model retraining.</p>
  </main>
</body>
</html>
''',
        encoding='utf-8',
    )
    return report_path


def _rebuild_capture_folder_results(
    dice_id: str,
    capture_dir: Path,
    db: DBManager,
    dice,
    model,
) -> tuple[Path, int, int, int]:
    source_files = _iter_capture_image_files(capture_dir)
    if not source_files:
        raise ValueError('No image files found to process.')

    db.delete_results_for_die(dice_id, wait=True)

    images_dir = capture_dir / 'images'
    unknown_dir = capture_dir / 'Unknown'
    valid_count = 0
    unknown_count = 0

    for image_path in source_files:
        frame = cv2.imread(str(image_path))
        if frame is None:
            _move_file_unique(image_path, unknown_dir)
            unknown_count += 1
            continue

        result = model(frame, verbose=False)[0]
        detected_dice = _count_matching_detections(result, dice._dice_key())
        value = dice.get_dice_value(result) if detected_dice == 1 else None
        is_valid = value is not None and 1 <= int(value) <= (dice.sides or int(value))

        if is_valid:
            moved_to = _move_file_unique(image_path, images_dir)
            db.write_test_result(str(value), str(moved_to), dice_sides=dice.sides, wait=False)
            valid_count += 1
        else:
            _move_file_unique(image_path, unknown_dir)
            unknown_count += 1

    db.wait_for_writes()
    rows = db.read_results_for_die(dice_id)

    if rows:
        report = analyze_results(dice_id=dice_id, rows=rows, dice_sides=dice.sides or 6)
        report_path = write_report(report, capture_dir)
    else:
        report_path = _write_empty_results_report(dice_id, capture_dir, len(source_files), unknown_count)

    return report_path, len(source_files), valid_count, unknown_count


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
                case QuCmd.CLEAR_ANALYSIS_DATA:
                    clear_analysis_data(main_queue)
                case QuCmd.CLEAR_DICE_ID_DATA:
                    clear_dice_id_data(main_queue)
                case QuCmd.RERUN_ANALYSIS_ON_CAPTURE_FOLDER:
                    rerun_analysis_on_capture_folder(main_queue)
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
    print('8) Clear collected analysis data')
    print('9) Clear one dice ID data')
    print('10) Rerun analysis on captured photos')
    print('=' * 50)

    choice = input('Enter your choice (0-10): ').strip()

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
        case '8':
            if ENABLE_LOGGING:
                print("'Clear collected analysis data' selected.")
            queue.put(QueueData(cmd=QuCmd.CLEAR_ANALYSIS_DATA, data=None))
        case '9':
            if ENABLE_LOGGING:
                print("'Clear one dice ID data' selected.")
            queue.put(QueueData(cmd=QuCmd.CLEAR_DICE_ID_DATA, data=None))
        case '10':
            if ENABLE_LOGGING:
                print("'Rerun analysis on captured photos' selected.")
            queue.put(QueueData(cmd=QuCmd.RERUN_ANALYSIS_ON_CAPTURE_FOLDER, data=None))
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

    queue.put(QueueData(cmd=QuCmd.EXIT, data=None))


def clear_analysis_data(queue: mp.Queue) -> None:
    """Delete all collected analysis rows plus captured sample images and reports."""
    print('\n' + '=' * 50)
    print('This will permanently delete:')
    print(f'  - all rows in {DBManager().db_path}')
    print(f'  - all generated files under {ANALYSIS_IMAGE_OUTPUT_DIR}')
    print('=' * 50)

    confirmation = input("Type DELETE to confirm, or press Enter to cancel: ").strip()
    if confirmation != 'DELETE':
        print('Clear operation cancelled.')
        queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))
        return

    db = DBManager(logging=ENABLE_LOGGING)
    deleted_paths = 0
    deleted_rows = len(db.read_all_results())

    try:
        if ANALYSIS_IMAGE_OUTPUT_DIR.exists():
            for child in ANALYSIS_IMAGE_OUTPUT_DIR.iterdir():
                if child.is_dir():
                    shutil.rmtree(child)
                    deleted_paths += 1
                elif child.is_file():
                    child.unlink()
                    deleted_paths += 1

        db.clear_all_data()
        print(
            f'Cleared {deleted_rows} database row(s) and removed {deleted_paths} '
            'capture item(s).'
        )
    except Exception as e:
        print(f'main.py clear_analysis_data() encountered an error: {e}.')

    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))


def clear_dice_id_data(queue: mp.Queue) -> None:
    """Delete all DB rows for one dice ID and remove that dice's capture artifacts."""
    db = DBManager(logging=ENABLE_LOGGING)
    all_ids = db.list_dice_ids()
    if not all_ids:
        print('\nNo data found in the database.')
        queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))
        return

    print('\nDice IDs in database: ' + ', '.join(all_ids))
    dice_id = input('Enter dice ID to clear: ').strip()
    if not dice_id:
        print('No dice ID entered. Operation cancelled.')
        queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))
        return

    rows = db.read_results_for_die(dice_id)
    capture_dir = ANALYSIS_IMAGE_OUTPUT_DIR / dice_id
    capture_item_count = 0
    if capture_dir.exists():
        capture_item_count = sum(1 for path in capture_dir.rglob('*') if path.is_file())

    print('\n' + '=' * 50)
    print(f'This will permanently delete data for dice ID: {dice_id}')
    print(f'  - DB rows to delete: {len(rows)}')
    print(f'  - capture files to delete: {capture_item_count}')
    print('=' * 50)

    confirmation = input("Type DELETE to confirm, or press Enter to cancel: ").strip()
    if confirmation != 'DELETE':
        print('Clear operation cancelled.')
        queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))
        return

    deleted_files = 0
    try:
        db.delete_results_for_die(dice_id, wait=True)

        if capture_dir.exists():
            deleted_files = sum(1 for path in capture_dir.rglob('*') if path.is_file())
            shutil.rmtree(capture_dir)

        print(
            f'Cleared dice ID {dice_id}: deleted {len(rows)} DB row(s) '
            f'and {deleted_files} capture file(s).'
        )
    except Exception as e:
        print(f'main.py clear_dice_id_data() encountered an error: {e}.')

    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))


def rerun_analysis_on_capture_folder(queue: mp.Queue) -> None:
    """Rebuild one dice ID from stored photos in its capture folder."""
    if not ANALYSIS_IMAGE_OUTPUT_DIR.exists():
        print('\nNo capture data folder found.')
        queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))
        return

    capture_dirs = sorted(path.name for path in ANALYSIS_IMAGE_OUTPUT_DIR.iterdir() if path.is_dir())
    if not capture_dirs:
        print('\nNo per-die capture folders found.')
        queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))
        return

    print('\nCapture folders: ' + ', '.join(capture_dirs))
    dice_id = input('Enter the dice ID folder to reprocess: ').strip()
    capture_dir = ANALYSIS_IMAGE_OUTPUT_DIR / dice_id
    if not dice_id or not capture_dir.is_dir():
        print(f"No capture folder found for dice ID '{dice_id}'.")
        queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))
        return

    db = DBManager(logging=ENABLE_LOGGING)
    project_data = DataFactory.create_project_data(
        'project_data',
        process_queue=mp.Queue(),
        logging=False,
        model_path=ANALYSIS_CONFIG.model_path,
    )
    dice = DiceFactory.create_dice('six_sided_pips', logging=False, data=project_data)
    model = YOLO(ANALYSIS_CONFIG.model_path)
    try:
        report_path, total_count, valid_count, unknown_count = _rebuild_capture_folder_results(
            dice_id=dice_id,
            capture_dir=capture_dir,
            db=db,
            dice=dice,
            model=model,
        )
    except ValueError as error:
        print(str(error))
        queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))
        return

    if valid_count > 0:
        print(f'Report written to: {report_path}')
    else:
        print(f'No validated images found. Empty report written to: {report_path}')

    print(f'Processed {total_count} image(s): {valid_count} valid, {unknown_count} unknown.')

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