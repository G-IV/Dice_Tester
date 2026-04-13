# use enum to enforce specific values for the name field.
from enum import Enum, auto

class Command(Enum):
    # Main process commands
    EXIT = auto()
    MAIN_MENU = auto()
    MOVE_TO_UNCAP = auto()
    SINGLE_IMAGE = auto() # Command to capture & show a single image.
    GATHER_SAMPLE_VIDEOS = auto() # Command to gather sample videos for model training.
    GATHER_DICE_ANALYSIS_DATA = auto() # Command to gather data for dice analysis.

    # Dice analysis process commands
    GET_NEXT_SAMPLE = auto() # Command to get the next sample for analysis.
    NEW_FRAME_CAPTURED = auto() # Command to notify the dice analysis process that a new frame is ready for processing.
    FRAME_PROCESSED = auto() # Command to notify the main process that a new frame is ready for display.
    RESET_TOWER = auto() # Command to reset the tower by flipping it twice before returning to data gathering.

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