from pathlib import Path
from typing import Any, Protocol


class FeedProtocol(Protocol):
    def destroy(self) -> None:
        ...

    def ready_for_frames(self, ready: bool = True) -> None:
        ...


class StreamProtocol(Protocol):
    window: str | None

    def show_frame(self, frame, delay: int = 1) -> None:
        ...

    def destroy(self) -> None:
        ...


class MotorProtocol(Protocol):
    def close(self) -> None:
        ...

    def move_to_uncap(self) -> None:
        ...

    def flip(self) -> None:
        ...

    def reset_position(self) -> None:
        ...


class ProjectDataProtocol(Protocol):
    frames: list[Any]
    results: list[Any]
    fps: int

    def new_frame(self, frame) -> None:
        ...

    def new_result(self, result) -> None:
        ...

    def clear_frames(self) -> None:
        ...


class DiceProtocol(Protocol):
    dice_state: Any
    sides: int | None

    def set_dice_state(self) -> None:
        ...

    def get_dice_value(self, result) -> int:
        ...

    def get_single_dice_bounds(self, result) -> tuple[int, int, int, int] | None:
        ...


class DatabaseProtocol(Protocol):
    dice_id: str | None

    def generate_id(self) -> str:
        ...

    def write_test_result(
        self,
        dice_result: str | int,
        image: str | Path,
        dice_sides: int | None = None,
        wait: bool = False,
    ) -> None:
        ...

    def wait_for_writes(self) -> None:
        ...

    def stop_writer(self) -> None:
        ...


class ModelProtocol(Protocol):
    def __call__(self, frame, verbose: bool = False):
        ...