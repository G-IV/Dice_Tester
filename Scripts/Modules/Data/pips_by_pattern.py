from Scripts.Modules.Data.project_data import ProjectData
from pathlib import Path

class PipsByPattern(ProjectData):
    """
    A class to manage all data related to pips by pattern, including analysis results and database interactions.
    """
    def __init__(
            self,
            model_path: Path,
            logging: bool = False
        ):
        super().__init__(model_path, logging=logging)

    def dice_value(self):
        dice_key = self.class_key_lookup_by_value('Dice')
        non_dice_found_classes = [cls for cls in self.found_classes if cls != dice_key]
        if len(non_dice_found_classes) != 1:
            if self.logging:
                print(f"Expected to find exactly one non-dice class for value determination, but found {len(non_dice_found_classes)}.")
            return None
        found_class = non_dice_found_classes[0]
        if self.logging:
            print(f"Found non-dice classes: {found_class} ({self.categories[found_class]})")
        return self.text_value_to_int(self.categories[found_class])
    
