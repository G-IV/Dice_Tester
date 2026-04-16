import multiprocessing as mp
from dataclasses import dataclass
import time

from ultralytics import YOLO

from Scripts.Modules.Data.data_factory import DataFactory
from Scripts.Modules.Feed.feed_factory import FeedFactory
from Scripts.Modules.Stream.stream import Stream
from Scripts.Modules.Motor.ad2 import Motor
from Scripts.Modules.Workflow.analysis_config import AnalysisConfig
from Scripts.Modules.Workflow.interfaces import FeedProtocol, ModelProtocol, MotorProtocol, ProjectDataProtocol, StreamProtocol


@dataclass
class CameraWorkflowContext:
    process_queue: mp.Queue
    process_data: ProjectDataProtocol
    feed: FeedProtocol
    stream: StreamProtocol
    motor: MotorProtocol
    model: ModelProtocol | None = None


def close_process_queue(queue: mp.Queue) -> None:
    queue.cancel_join_thread()
    queue.close()


def create_camera_workflow_context(
    main_queue: mp.Queue,
    config: AnalysisConfig,
    logging: bool = False,
    motor_logging: bool | None = None,
    include_model: bool = False,
) -> CameraWorkflowContext:
    process_queue = mp.Queue()
    process_data = DataFactory.create_project_data(
        'project_data',
        logging=logging,
        model_path=config.model_path,
        process_queue=process_queue,
    )
    feed = FeedFactory.create_feed(
        'camera',
        data=process_data,
        process_queue=process_queue,
        logging=logging,
    )
    stream = Stream(logging=logging)
    motor = Motor(
        logging=logging if motor_logging is None else motor_logging,
        main_queue=main_queue,
    )
    model = YOLO(config.model_path) if include_model and config.model_path.exists() else None
    return CameraWorkflowContext(
        process_queue=process_queue,
        process_data=process_data,
        feed=feed,
        stream=stream,
        motor=motor,
        model=model,
    )


def cleanup_camera_workflow(context: CameraWorkflowContext) -> None:
    context.feed.destroy()
    context.stream.destroy()
    context.motor.close()
    close_process_queue(context.process_queue)


def begin_camera_capture(context: CameraWorkflowContext, settle_seconds: float = 1.0) -> None:
    context.motor.move_to_uncap()
    time.sleep(settle_seconds)
    context.feed.ready_for_frames(True)