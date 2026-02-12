from enum import Enum
import numpy as np

class Dice:
    """
    Maintains the last n iterations of coordinates and provides analysis methods.
    """

    class DiceState(Enum):
        STABLE = 'stable'
        MOVING = 'moving'
        UNKNOWN = 'unknown'
        LOGGED = 'logged'

    """
    Initializes the Dice object to track state and positions.
    Attributes:
        buffer_size (int): The number of previous positions to store.  Set to 1 for single frame analysis.
        state (DiceState): The current state of the dice.
        logged (bool): Flag to indicate if the current state has been logged.
        center_positions (list): List to store the center positions of the dice.
        previous_rolls (list): List to store the history of previous rolls.
        movement_threshold (int): Threshold to determine if the dice is stable or moving, this is movement in pixels.
    """
    def __init__(
            self, 
            buffer_size: int =10, 
            movement_threshold: int =5
        ):
        self.buffer_size = buffer_size
        self.logged = False
        self.center_positions = []
        self.previous_rolls = []
        self.movement_threshold = movement_threshold  # Pixels

    def update_center_coordinates(self, bounding_box: object):
        """Add a new center position to the buffer."""
        # the object is {'x1': float, 'y1': float, 'x2': float, 'y2': float}
        x_center = (bounding_box['x1'] + bounding_box['x2']) / 2
        y_center = (bounding_box['y1'] + bounding_box['y2']) / 2
        position = (x_center, y_center)
        self.center_positions.append(position)
        if len(self.center_positions) > self.buffer_size:
            self.center_positions.pop(0)

    def dice_state(self):
        if self.is_unknown():
            return self.DiceState.UNKNOWN
        elif self.is_stable():
            return self.DiceState.STABLE
        else:
            return self.DiceState.MOVING
    
    def get_movement_magnitude(self):
        """Calculate total movement magnitude between first and last coordinate."""
        if self.is_unknown():
            return 0
        print(f"Center Positions: {self.center_positions}")
        x1, y1 = self.center_positions[0]
        x2, y2 = self.center_positions[-1]
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def is_stable(self):
        """
        Assume that the bounding box will have minor movements even when the die is still.
        If the total movement magnitude is below a certain threshold, consider it stable.
        If the buffer size is 1, we are analyzing a single frame, so consider it stable.
        """
        if self.buffer_size == 1:
            return True
        if self.is_unknown():
            return False
        print(f"Movement Magnitude: {self.get_movement_magnitude()}, Threshold: {self.movement_threshold}")
        return self.get_movement_magnitude() < self.movement_threshold
    
    def is_unknown(self):
        """Determine if the die is stuck (not moving for a prolonged period)."""
        # Different scenarios where the dice position is unknown
        if len(self.center_positions) < self.buffer_size:
            return True
        elif self.center_positions[-1] == None or self.center_positions[0] == None:
            return True
        return False
    
