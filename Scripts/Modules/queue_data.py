# use enum to enforce specific values for the name field.
from enum import Enum, auto

class Command(Enum):
    EXIT = auto()
    MAIN_MENU = auto()
    MOVE_TO_UNCAP = auto()
    SINGLE_IMAGE = auto() # Command to capture & show a single image.
    GATHER_SAMPLE_VIDEOS = auto() # Command to gather sample videos for model training.
    GATHER_DICE_ANALYSIS_DATA = auto() # Command to gather data for dice analysis.
    FRAME_READY = auto() # Notify main process the next frame to show is ready.

class QueueData:
    """
    A simple data class to hold information about items in the queue.
    Format:

        "cmd": "Command value",
        "data": "Associated data"

    The data can be just about anything, so I don't need to do any type enforcement.
    """
    def __init__(self, cmd: Command, data) -> None:
        self.cmd = cmd
        self.data = data

    def __repr__(self) -> str:
        return f"Queue item: (cmd={self.cmd}, data={self.data})"