import multiprocessing as mp
from queue import Empty
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import time
from enum import Enum, auto

from ultralytics import YOLO

from Scripts.Modules.queue_data import QueueData, Command as QuCmd
from Scripts.Modules.Dice.dice_factory import DiceFactory
from Scripts.Modules.Dice.dice import DiceState
from Scripts.Modules.Database.database import DBManager
from Scripts.Modules.Storage.image_writer import write_frame_image
from Scripts.Modules.Workflow.analysis_config import AnalysisConfig
from Scripts.Modules.Workflow.session_utils import begin_camera_capture, create_camera_workflow_context, cleanup_camera_workflow


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


def persist_analysis_roll(config: AnalysisConfig, db: DBManager, frame, dice_id: str, dice_value: str) -> None:
    image_path = write_frame_image(
        frame,
        config.analysis_image_output_dir / dice_id,
        dice_id=dice_id,
        dice_value=dice_value,
    )
    db.write_test_result(dice_value, image_path, wait=False)


class DiceAnalysisSession:
    def __init__(
        self,
        process_queue: mp.Queue,
        process_data,
        feed,
        stream,
        dice,
        motor,
        db: DBManager,
        config: AnalysisConfig,
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
        self.logging = logging
        self.state = AnalysisState.INITIALIZING

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
            self.process_queue.put(QueueData(cmd=QuCmd.SHOW_FRAME, data=rendered))
            self.process_queue.put(QueueData(cmd=QuCmd.EVALUATE_DICE_STATE, data=None))
        except Exception as e:
            print(f'main.py on_analyze_frame_done() encountered an error: {e}.')

    def on_persist_settled_roll_done(self, future) -> None:
        try:
            future.result()
        except Exception as e:
            print(f'main.py on_persist_settled_roll_done() encountered an error: {e}.')

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

    def handle_evaluate_dice_state(self, image_executor) -> None:
        self.dice.set_dice_state()

        if (self.dice.dice_state == DiceState.UNKNOWN) and (
            len(self.process_data.frames) > self.process_data.fps * self.config.max_time_before_flip
        ):
            self.state = AnalysisState.RESETTING_TOWER
            self.process_queue.put(QueueData(cmd=QuCmd.RESET_TOWER, data=None))
            return

        if self.dice.dice_state == DiceState.SETTLED:
            value = self.dice.get_dice_value(self.process_data.results[-1])

            if not self.db.dice_id:
                self.db.generate_id()

            future_persist_roll = image_executor.submit(
                persist_analysis_roll,
                self.config,
                self.db,
                self.process_data.frames[-1].copy(),
                str(self.db.dice_id),
                str(value),
            )
            future_persist_roll.add_done_callback(self.on_persist_settled_roll_done)
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


def create_dice_analysis_session(main_queue: mp.Queue, config: AnalysisConfig, logging: bool = False) -> DiceAnalysisSession:
    context = create_camera_workflow_context(
        main_queue,
        config,
        logging=logging,
        motor_logging=False,
    )
    dice = DiceFactory.create_dice('six_sided_pips', logging=logging, data=context.process_data)
    db = DBManager(dice_id=None, logging=logging)
    return DiceAnalysisSession(
        process_queue=context.process_queue,
        process_data=context.process_data,
        feed=context.feed,
        stream=context.stream,
        dice=dice,
        motor=context.motor,
        db=db,
        config=config,
        logging=logging,
    )


def run_dice_analysis_session(main_queue: mp.Queue, config: AnalysisConfig, logging: bool = False) -> None:
    session = None
    try:
        session = create_dice_analysis_session(main_queue, config, logging=logging)
        session.begin_capture_loop()

        start_time = time.perf_counter()
        with ProcessPoolExecutor(
            initializer=init_worker,
            initargs=(config.model_path,),
        ) as executor, ThreadPoolExecutor(max_workers=2, thread_name_prefix='image-writer') as image_executor:
            while True:
                if time.perf_counter() - start_time > config.max_process_time:
                    session.process_queue.put(QueueData(cmd=QuCmd.EXIT, data=None))
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
