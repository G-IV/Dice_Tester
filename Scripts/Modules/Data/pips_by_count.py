from Scripts.Modules.Data import project_data
from pathlib import Path
from multiprocessing.queues import Queue

class ProjectData(project_data.ProjectData):
    """
    A class to manage all data related to pip counting, including analysis results and database interactions.
    """
    def __init__(
            self,
            logging: bool = False,
            main_queue: Queue | None = None
        ):
        super().__init__(
            logging=logging,
            main_queue=main_queue

        )
        
        if self.logging:
            print(f"Initialized Pips by Count ProjectData")

    def dice_value(self):
        # For the pip counter, we need to find the number of times a pip is detected
        pip_qty = self.get_qty_class_is_found('Pip')
        if self.logging:
            print(f"Dice value (number of pips found): {pip_qty}")
        return pip_qty
    
    def get_pip_bounding_boxes(self) -> list:
        """Get bounding boxes for detected pips from the analysis results."""
        if self.get_qty_class_is_found('Pip') == 0:
            if self.logging:
                print("No pips found in current analysis, returning None for pip bounding boxes.")
            return []
        pip_key = self.class_key_lookup_by_value('Pip')
        boxes = self.analysis.boxes
        target_boxes = boxes[boxes.cls == pip_key]
        if self.logging:
            print(f"Retrieved {len(target_boxes)} pip bounding boxes from analysis results.")
        return target_boxes.xyxy.cpu().numpy().astype(int)
