from Scripts.Modules.Data import project_data
from pathlib import Path

class ProjectData(project_data.ProjectData):
    """
    A class to manage all data related to pip counting, including analysis results and database interactions.
    """
    def __init__(
            self,
            logging: bool = False
        ):
        super().__init__(
            logging=logging
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
    
    def frame_monitoring(self):
        """Monitor the frame queue for new frames and update the current frame in project data."""
        if self.logging:
            print("Starting frame monitoring thread (pips_by_count).")
        while not self.stop_frame_thread:
            try:
                queue_data = self.frame_queue.get(timeout=1)  # Wait for a new frame with a timeout
                if queue_data['type'] == 'New Frame':
                    self.set_frame(queue_data['data'])
                    self.analyzer_queue.put({
                        'type': 'New Frame', 
                        'data': None
                        })  # Send frame to analyzer queue
                    if self.logging:
                        print("Updated current frame in project data from frame queue (pips_by_count).")
                elif queue_data['type'] == 'New Analysis':
                    # Handle other types of messages if needed
                    results = queue_data['data']
                    self.add_analysis_results(results)
                    if self.logging:
                        print("Updated analysis results in project data from frame queue (pips_by_count).")
            except Exception as e:
                continue  # Timeout occurred, loop back and check stop_thread flag