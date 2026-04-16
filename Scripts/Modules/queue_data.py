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
    ANALYZE_FRAME = auto() # Command to analyze a frame using the model and store the results.
    FRAME_PROCESSED = auto() # Command to notify the main process that a new frame is ready for display.
    RESET_TOWER = auto() # Command to reset the tower by flipping it twice before returning to data gathering.
    EVALUATE_DICE_STATE = auto() # Command to evaluate the current state of the dice based on the latest processed frame.

    # Stream control commands
    SHOW_FRAME = auto() # Command to show a frame in the stream window.

    # Data control commands
    CLEAR_FRAMES = auto() # Command to clear the stored frames and results in the data
    PROCESS_FRAME = auto() # Command to process a new frame in the data

    # Motor control commands
    MOTOR_RESET_COMPLETE = auto() # Command to flip the motor to the next position.

    # Database control commands
    DB_EXECUTE_SQL = auto() # Command to execute a parameterized SQL write.
    DB_WRITE_TEST_RESULT = auto() # Command to write a test result row to the database.
    DB_CLEAR_ALL_DATA = auto() # Command to delete all rows in test_results.
    DB_STOP_WRITER = auto() # Command to stop the database writer thread.
    VIEW_DICE_DATA = auto() # Command to view stored results for a given dice ID.

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