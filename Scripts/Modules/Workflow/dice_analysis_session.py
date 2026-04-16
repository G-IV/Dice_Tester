import multiprocessing as mp
from queue import Empty
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import time
from enum import Enum, auto
from threading import Lock

from ultralytics import YOLO

from Scripts.Modules.queue_data import QueueData, Command as QuCmd
from Scripts.Modules.Dice.dice_factory import DiceFactory
from Scripts.Modules.Dice.dice import DiceState
from Scripts.Modules.Database.database import DBManager
from Scripts.Modules.Storage.image_writer import write_frame_image
from Scripts.Modules.Workflow.analysis_config import AnalysisConfig
from Scripts.Modules.Workflow.interfaces import DatabaseProtocol, DiceProtocol, FeedProtocol, MotorProtocol, ProjectDataProtocol, StreamProtocol
from Scripts.Modules.Workflow.session_utils import begin_camera_capture, create_camera_workflow_context, cleanup_camera_workflow
from Scripts.Modules.Stream.overlay import FrameContext, composite_with_panel


_worker_model = None


def init_worker(model_path):
    global _worker_model
    _worker_model = YOLO(model_path)


def analyze_frame_worker(frame):
    result = _worker_model(frame, verbose=False)[0]
    rendered = result.plot()
    return rendered, result


class AnalysisState(Enum):
    INITIALIZING = auto()
    ANALYZING = auto()
    RESETTING_TOWER = auto()
    STOPPING = auto()


def persist_analysis_roll(
    config: AnalysisConfig,
    db: DatabaseProtocol,
    frame,
    dice_id: str,
    dice_value: str,
    dice_sides: int | None,
) -> None:
    image_path = write_frame_image(
        frame,
        config.analysis_image_output_dir / dice_id / 'images',
        dice_id=dice_id,
        dice_value=dice_value,
        dice_sides=dice_sides,
    )
    # Use wait=True so callback completion means the row has been written.
    db.write_test_result(dice_value, image_path, dice_sides=dice_sides, wait=True)


class DiceAnalysisSession:
    def __init__(
        self,
        process_queue: mp.Queue,
        process_data: ProjectDataProtocol,
        feed: FeedProtocol,
        stream: StreamProtocol,
        dice: DiceProtocol,
        motor: MotorProtocol,
        db: DatabaseProtocol,
        config: AnalysisConfig,
        target_samples: int,
        logging: bool = False,
    ) -> None:
        self.process_queue = process_queue
        self.process_data = process_data
        self.feed = feed
        self.stream = stream
        self.dice = dice
        self.motor = motor
        self.db = db
        self.config = config
        self.target_samples = target_samples
        self.logging = logging
        self.state = AnalysisState.INITIALIZING
        self.sample_lock = Lock()
        self.submitted_samples = 0
        self.persisted_samples = 0
        self.awaiting_next_roll = False
        self._face_counts: dict[int, int] = {}
        self._persisted_timestamps: list[float] = []

    def begin_capture_loop(self) -> None:
        if self.logging:
            print('main.py gather_dice_analysis_data() Moving to uncap position.')
        begin_camera_capture(self)

        if self.logging:
            print('main.py gather_dice_analysis_data() Motor is in uncap position, starting main data gathering loop.')
        self.process_queue.put(QueueData(cmd=QuCmd.GET_NEXT_SAMPLE, data=None))
        self.state = AnalysisState.ANALYZING

    def cleanup(self) -> None:
        self.state = AnalysisState.STOPPING
        self.db.wait_for_writes()
        self.db.stop_writer()
        cleanup_camera_workflow(self)

    def on_analyzed_frame_done(self, future) -> None:
        try:
            rendered, result = future.result()
            self.process_data.new_result(result)
            # Build per-detection list for the overlay
            detections = []
            if result.boxes is not None:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    name = result.names.get(cls_id, str(cls_id))
                    detections.append({'name': name, 'conf': conf})

            with self.sample_lock:
                roll_num = self.submitted_samples

            eta_text = self._estimate_eta_text()

            dice_id = str(self.db.dice_id) if self.db.dice_id else None
            ctx = FrameContext(
                dice_state=self.dice.dice_state.name,
                dice_value=self.dice.get_dice_value(result) if self.dice.dice_state == DiceState.SETTLED else None,
                roll_number=roll_num,
                target_samples=self.target_samples,
                eta_text=eta_text,
                db_linked=self.db.dice_id is not None,
                dice_id=dice_id,
                dice_sides=self.dice.sides,
                total_rolls=sum(self._face_counts.values()) or None,
                mean_roll=(
                    sum(k * v for k, v in self._face_counts.items()) / sum(self._face_counts.values())
                    if self._face_counts else None
                ),
                expected_mean=(
                    (self.dice.sides + 1) / 2 if self.dice.sides else None
                ),
                face_counts=dict(self._face_counts),
                detections=detections,
            )
            composited = composite_with_panel(rendered, ctx)
            self.process_queue.put(QueueData(cmd=QuCmd.SHOW_FRAME, data=composited))
            self.process_queue.put(QueueData(cmd=QuCmd.EVALUATE_DICE_STATE, data=None))
        except Exception as e:
            print(f'main.py on_analyze_frame_done() encountered an error: {e}.')

    def on_persist_settled_roll_done(self, future) -> None:
        try:
            future.result()

            should_exit = False
            with self.sample_lock:
                self.persisted_samples += 1
                self._persisted_timestamps.append(time.time())
                current = self.persisted_samples
                should_exit = self.persisted_samples >= self.target_samples

            if self.logging:
                print(
                    f'main.py gather_dice_analysis_data() persisted sample '
                    f'{current}/{self.target_samples}.'
                )

            if should_exit:
                self.process_queue.put(QueueData(cmd=QuCmd.EXIT, data=None))
        except Exception as e:
            print(f'main.py on_persist_settled_roll_done() encountered an error: {e}.')

    @staticmethod
    def _format_eta(seconds: float) -> str:
        total_seconds = max(0, int(round(seconds)))
        hours, rem = divmod(total_seconds, 3600)
        minutes, secs = divmod(rem, 60)
        if hours > 0:
            return f'{hours:d}:{minutes:02d}:{secs:02d}'
        return f'{minutes:02d}:{secs:02d}'

    def _estimate_eta_text(self) -> str | None:
        with self.sample_lock:
            remaining = self.target_samples - self.persisted_samples
            if remaining <= 0:
                return '00:00'

            if len(self._persisted_timestamps) < 2:
                return None

            elapsed = self._persisted_timestamps[-1] - self._persisted_timestamps[0]
            intervals = len(self._persisted_timestamps) - 1
            if elapsed <= 0 or intervals <= 0:
                return None

            seconds_per_sample = elapsed / intervals

        return self._format_eta(remaining * seconds_per_sample)

    def handle_get_next_sample(self) -> None:
        if self.logging:
            print('main.py gather_dice_analysis_data() GET_NEXT_SAMPLE command received, preparing for next sample.')
        self.process_data.clear_frames()
        self.motor.flip()

    def handle_new_frame_captured(self, item, executor) -> None:
        if self.logging:
            print('main.py gather_dice_analysis_data() NEW_FRAME_CAPTURED command received.')

        if self.state != AnalysisState.RESETTING_TOWER:
            self.process_data.new_frame(item.data)
            future_new_frame = executor.submit(analyze_frame_worker, item.data)
            future_new_frame.add_done_callback(self.on_analyzed_frame_done)
            return

        self.process_queue.put(QueueData(cmd=QuCmd.SHOW_FRAME, data=item.data))

    def handle_show_frame(self, item) -> None:
        self.stream.show_frame(item.data)

    def _coerce_face_value(self, value: object) -> int | None:
        """Return a valid face value for this die, or None when unusable."""
        try:
            face = int(value)
        except (TypeError, ValueError):
            return None

        if self.dice.sides is not None and not (1 <= face <= self.dice.sides):
            return None
        return face

    def handle_evaluate_dice_state(self, image_executor) -> None:
        self.dice.set_dice_state()

        if self.awaiting_next_roll:
            if self.dice.dice_state != DiceState.SETTLED:
                self.awaiting_next_roll = False
            return

        if (self.dice.dice_state == DiceState.UNKNOWN) and (
            len(self.process_data.frames) > self.process_data.fps * self.config.max_time_before_flip
        ):
            self.state = AnalysisState.RESETTING_TOWER
            self.process_queue.put(QueueData(cmd=QuCmd.RESET_TOWER, data=None))
            return

        if self.dice.dice_state == DiceState.SETTLED:
            value = self.dice.get_dice_value(self.process_data.results[-1])
            face = self._coerce_face_value(value)
            if face is None:
                if self.logging:
                    print('main.py gather_dice_analysis_data() Skipping invalid settled value; requesting retry roll.')
                self.awaiting_next_roll = True
                self.process_queue.put(QueueData(cmd=QuCmd.GET_NEXT_SAMPLE, data=None))
                return

            self._face_counts[face] = self._face_counts.get(face, 0) + 1

            if not self.db.dice_id:
                self.db.generate_id()

            with self.sample_lock:
                if self.submitted_samples >= self.target_samples:
                    return
                self.submitted_samples += 1
                should_request_next = self.submitted_samples < self.target_samples

            future_persist_roll = image_executor.submit(
                persist_analysis_roll,
                self.config,
                self.db,
                self.process_data.frames[-1].copy(),
                str(self.db.dice_id),
                str(face),
                self.dice.sides,
            )
            future_persist_roll.add_done_callback(self.on_persist_settled_roll_done)
            self.awaiting_next_roll = True

            if should_request_next:
                self.process_queue.put(QueueData(cmd=QuCmd.GET_NEXT_SAMPLE, data=None))

    def handle_reset_tower(self) -> None:
        self.motor.reset_position()

    def handle_motor_reset_complete(self) -> None:
        self.state = AnalysisState.ANALYZING
        self.process_queue.put(QueueData(cmd=QuCmd.GET_NEXT_SAMPLE, data=None))

    def handle_process_queue_item(self, item, executor, image_executor) -> bool:
        if item.cmd == QuCmd.EXIT:
            return True
        if item.cmd == QuCmd.GET_NEXT_SAMPLE:
            self.handle_get_next_sample()
            return False
        if item.cmd == QuCmd.NEW_FRAME_CAPTURED:
            self.handle_new_frame_captured(item, executor)
            return False
        if item.cmd == QuCmd.SHOW_FRAME:
            self.handle_show_frame(item)
            return False
        if item.cmd == QuCmd.EVALUATE_DICE_STATE:
            self.handle_evaluate_dice_state(image_executor)
            return False
        if item.cmd == QuCmd.RESET_TOWER:
            self.handle_reset_tower()
            return False
        if item.cmd == QuCmd.MOTOR_RESET_COMPLETE:
            self.handle_motor_reset_complete()
            return False
        return False


def create_dice_analysis_session(
    main_queue: mp.Queue,
    config: AnalysisConfig,
    target_samples: int,
    dice_id: str | None = None,
    logging: bool = False,
) -> DiceAnalysisSession:
    context = create_camera_workflow_context(
        main_queue,
        config,
        logging=logging,
        motor_logging=False,
    )
    dice = DiceFactory.create_dice('six_sided_pips', logging=logging, data=context.process_data)
    db = DBManager(dice_id=dice_id, logging=logging)
    return DiceAnalysisSession(
        process_queue=context.process_queue,
        process_data=context.process_data,
        feed=context.feed,
        stream=context.stream,
        dice=dice,
        motor=context.motor,
        db=db,
        config=config,
        target_samples=target_samples,
        logging=logging,
    )


def run_dice_analysis_session(
    main_queue: mp.Queue,
    config: AnalysisConfig,
    target_samples: int,
    dice_id: str | None = None,
    logging: bool = False,
) -> str | None:
    """Run a dice analysis session and return the dice_id, or None if no samples were saved."""
    session = None
    try:
        session = create_dice_analysis_session(
            main_queue,
            config,
            target_samples,
            dice_id=dice_id,
            logging=logging,
        )
        session.begin_capture_loop()

        with ProcessPoolExecutor(
            initializer=init_worker,
            initargs=(config.model_path,),
        ) as executor, ThreadPoolExecutor(max_workers=2, thread_name_prefix='image-writer') as image_executor:
            while True:
                try:
                    item = session.process_queue.get(timeout=1)
                    if session.handle_process_queue_item(item, executor, image_executor):
                        break
                except Empty:
                    pass
                except Exception as e:
                    print(f'main.py gather_dice_analysis_data() encountered an unexpected error: {e}.')
                    break
    except Exception as e:
        print(f'main.py gather_dice_analysis_data() encountered an error while initializing supporting class instances: {e}, attempting to return to the main menu.')
    finally:
        if session is not None:
            session.cleanup()

    return str(session.db.dice_id) if (session is not None and session.db.dice_id is not None) else None
