from Scripts.Modules.Data.project_data import ProjectData
from enum import Enum
import numpy as np
from abc import ABC, abstractmethod

class Dice(ABC):
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
            data: ProjectData,
            buffer_size: int = 10,
            logging: bool = False, 
            movement_threshold: int = 5
        ):
        self.buffer_size = buffer_size
        self.data = data
        self.logged = False
        self.logging = logging
        self.movement_threshold = movement_threshold  # Pixels
        
        if self.logging:
            print(f"Initialized Dice with buffer size {self.buffer_size} and movement threshold {self.movement_threshold}")

    def dice_state(self):
        if self.is_unknown():
            return self.DiceState.UNKNOWN
        elif self.is_moving():
            return self.DiceState.MOVING
        else:
            return self.DiceState.STABLE
    
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
        if self.buffer_size == 1 and len(self.data.dice_center_coordinates_buffer) == 1:
            return True
        if self.is_unknown() or self.is_moving():
            return False
        print(f"Movement Magnitude: {self.get_movement_magnitude()}, Threshold: {self.movement_threshold}")
        return self.get_movement_magnitude() < self.movement_threshold
    
    def is_unknown(self):
        """Determine if the die is stuck (not moving for a prolonged period)."""
        # If the current frame shows no dice, we consider the state unknown.
        if len(self.found_classes) == 0:
            return True

    def is_moving(self):
        """Determine if the die is moving."""
        # Do we have some stored positions?
        if self.is_unknown():
            return False
        elif len(self.data.dice_center_coordinates_buffer) < self.buffer_size:
            return True
        elif self.get_movement_magnitude() >= self.movement_threshold:
            return True
        else:
            return False
        
    @abstractmethod
    def stringify_details(self):
        """Return a string representation of the dice details."""
        if self.logging:
            print("Stringifying dice details.")
        pass    
