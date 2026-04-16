import multiprocessing as mp
from queue import Empty
from datetime import datetime
from pathlib import Path

import cv2

from Scripts.Modules.queue_data import QueueData, Command as QuCmd
from Scripts.Modules.Workflow.analysis_config import AnalysisConfig
from Scripts.Modules.Workflow.interfaces import FeedProtocol, ModelProtocol, MotorProtocol, ProjectDataProtocol, StreamProtocol
from Scripts.Modules.Workflow.session_utils import begin_camera_capture, create_camera_workflow_context, cleanup_camera_workflow


class SampleVideoSession:
    def __init__(
        self,
        process_queue: mp.Queue,
        process_data: ProjectDataProtocol,
        feed: FeedProtocol,
        stream: StreamProtocol,
        motor: MotorProtocol,
        model: ModelProtocol | None,
        config: AnalysisConfig,
        logging: bool = False,
    ) -> None:
        self.process_queue = process_queue
        self.process_data = process_data
        self.feed = feed
        self.stream = stream
        self.motor = motor
        self.model = model
        self.config = config
        self.logging = logging

    def save_buffered_video(self, frames) -> Path | None:
        if not frames:
            return None

        self.config.sample_video_output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        output_path = self.config.sample_video_output_dir / f'{timestamp}.mp4'

        height, width = frames[0].shape[:2]
        writer = cv2.VideoWriter(
            str(output_path),
            cv2.VideoWriter_fourcc(*'mp4v'),
            self.config.sample_video_fps,
            (width, height),
        )
        try:
            if not writer.isOpened():
                raise ValueError(f'Failed to open video writer for {output_path}')
            for frame in frames:
                writer.write(frame)
        finally:
            writer.release()

        if self.logging:
            print(f'  -> Saved sample video: {output_path}')
        return output_path

    def begin_capture_loop(self) -> None:
        begin_camera_capture(self)

    def run(self) -> None:
        print("Sample video controls (focus image window): space save+flip, 'q' save+quit.")
        last_rendered_frame = None

        while True:
            latest_frame = None
            while True:
                try:
                    item = self.process_queue.get_nowait()
                except Empty:
                    break

                if item.cmd != QuCmd.NEW_FRAME_CAPTURED:
                    continue

                frame = item.data
                self.process_data.new_frame(frame)
                latest_frame = frame

            if latest_frame is not None:
                if self.model is not None:
                    results = self.model(latest_frame, verbose=False)
                    self.process_data.new_result(results[0])
                    rendered = results[0].plot()
                else:
                    rendered = latest_frame.copy()

                last_rendered_frame = rendered
                self.stream.show_frame(rendered, delay=1)
            elif last_rendered_frame is not None:
                self.stream.show_frame(last_rendered_frame, delay=1)

            if self.stream.window and cv2.getWindowProperty(self.stream.window, cv2.WND_PROP_VISIBLE) < 1:
                self.save_buffered_video(self.process_data.frames)
                break

            # Poll keys on a steady cadence independent of queue timing.
            key = cv2.waitKey(10) & 0xFF
            if key == ord(' '):
                self.save_buffered_video(self.process_data.frames)
                self.process_data.clear_frames()
                self.motor.flip()
                continue
            if key == ord('q'):
                self.save_buffered_video(self.process_data.frames)
                break

    def cleanup(self) -> None:
        cleanup_camera_workflow(self)


def create_sample_video_session(main_queue: mp.Queue, config: AnalysisConfig, logging: bool = False) -> SampleVideoSession:
    context = create_camera_workflow_context(
        main_queue,
        config,
        logging=logging,
        include_model=True,
    )
    return SampleVideoSession(
        process_queue=context.process_queue,
        process_data=context.process_data,
        feed=context.feed,
        stream=context.stream,
        motor=context.motor,
        model=context.model,
        config=config,
        logging=logging,
    )


def run_sample_video_session(main_queue: mp.Queue, config: AnalysisConfig, logging: bool = False) -> None:
    session = None
    try:
        session = create_sample_video_session(main_queue, config, logging=logging)
        session.begin_capture_loop()
        session.run()
    except Exception as e:
        print(f'main.py gather_sample_videos() encountered an error: {e}.')
    finally:
        if session is not None:
            session.cleanup()
