from Scripts.Modules.Data import project_data
from pathlib import Path

class ProjectData(project_data.ProjectData):
    """
    A class to manage all data related to pip counting, including analysis results and database interactions.
    """
    def __init__(
            self,
            model_path: Path,
            logging: bool = False
        ):
        super().__init__(
            logging=logging,
            model_path=model_path
        )
        
        if self.logging:
            print(f"Initialized Pips by Count ProjectData")

    def dice_value(self):
        # For the pip counter, we need to find the number of times a pip is detected
        pip_qty = self.get_qty_class_is_found('Pip')
        if self.logging:
            print(f"Dice value (number of pips found): {pip_qty}")
        return pip_qty
    
