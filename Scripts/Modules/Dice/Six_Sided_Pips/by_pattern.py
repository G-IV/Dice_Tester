# Project module imports
from Scripts.Modules.Data.project_data import ProjectData
from Scripts.Modules.Dice.dice import Dice, DiceState

# Data type imports
from ultralytics.engine.results import Results

# Varible for found classes -> See notes.json for id -> value mapping.
categories: dict[int, int] = {
    # 0: "Dice", This is the dice class, we can ignore it.
    1: 5,
    2: 4,
    3: 3,
    4: 6,
    5: 3,
    6: 2
}

class SixSidedPips(Dice):
    """
    This class is specifically for interpreting the results of a model trained to detect the pips on a six sided die.  It will use the number of pips detected to determine the value of the die, and it will use the movement of the die to determine if it is settled or not.
    """
    def __init__(self, data: ProjectData, logging: bool = False) -> None:
        super().__init__(data, logging)

    def get_dice_value(self, results: Results) -> int | None:
        """Get the value of the die based on the number of pips detected.  This function assumes that the model is trained to detect pips and that the class names for the pips are in the format "pip_X" where X is the number of pips."""
        #===================
        # I had this stuff for checking the dice, but I'm just going to assume the results passed to this function are from a settled dice, and that the model is accurate enough that I don't need to check for the dice class.  If I find
        # if self.dice_state != DiceState.SETTLED:
        #     return None
        
        dice_indices = (results.boxes.cls != self._dice_key()).nonzero(as_tuple=True)[0]

        # if dice_indices.numel() != 1:
        #     return None
        
        detected_pips_id = results.boxes.cls[dice_indices].item()
        return categories.get(detected_pips_id, None)
