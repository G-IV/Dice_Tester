# use enum to enforce specific values for the name field.
from enum import Enum, auto

class Command(Enum):
    EXIT = auto()
    MAIN_MENU = auto()

class QueueData:
    """
    A simple data class to hold information about items in the queue.
    Format:

        "cmd": "Command value",
        "data": "Associated data"

    The data can be just about anything, so I don't need to do any type enforcement.
    """
    def __init__(self, cmd: Command, data):
        self.cmd = cmd
        self.data = data

    def __repr__(self):
        return f"Queue item: (cmd={self.cmd}, data={self.data})"