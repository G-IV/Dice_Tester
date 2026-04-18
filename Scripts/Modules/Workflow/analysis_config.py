from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AnalysisConfig:
    """Shared runtime configuration for capture and analysis workflows."""

    model_path: Path
    analysis_image_output_dir: Path
    sample_video_output_dir: Path
    report_output_dir: Path
    max_process_time: int = 20
    max_time_before_flip: int = 4
    sample_video_fps: float = 30.0
    stable_value_window: int = 4
    min_stable_value_occurrences: int = 3
    max_settled_frames_before_unknown: int = 12
