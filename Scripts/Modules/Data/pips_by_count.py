from Scripts.Modules.Data.project_data import ProjectData
from pathlib import Path

class PipsByCount(ProjectData):
    """
    A class to manage all data related to pip counting, including analysis results and database interactions.
    """
    def __init__(
            self,
            model_path: Path,
            logging: bool = False
        ):
        super().__init__(model_path, logging=logging)

    def dice_value(self):
        # For the pip counter, we need to find the number of times a pip is detected
        pip_qty = self.get_qty_class_is_found('Pip')
        if self.logging:
            print(f"Dice value (number of pips found): {pip_qty}")
        return pip_qty
    
