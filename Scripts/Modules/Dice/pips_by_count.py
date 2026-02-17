"""
Adds specific support for dice with pips
"""
from Scripts.Modules.Data.project_data import ProjectData
from Scripts.Modules.Dice import dice

class Dice(dice.Dice):
    """
    A class for dice with pips, such as d6s.
    """
    def __init__(
            self,
            data: ProjectData,
            buffer_size: int = 10, 
            movement_threshold: int = 5,
            logging: bool = False
        ):
        super().__init__(
            data=data,
            buffer_size=buffer_size, 
            movement_threshold=movement_threshold,
            logging=logging
        )
        
        if self.logging:
            print(f"Initialized PipsByCount Dice with buffer size {self.buffer_size} and movement threshold {self.movement_threshold}")

    def stringify_details(self):
        """Return a string representation of the dice details."""
        # TODO: Implement stringification of dice details based on pip counting method.
        details = "TODO: Implement stringification of dice details based on pip counting method."
        if self.logging:
            print(f"Stringified dice details: {details}")
        return details