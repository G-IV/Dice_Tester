from Scripts.Modules.Annotators import annotate
from Scripts.Modules.Data import project_data
class Annotator(annotate.Annotator):
    '''
    A class for annotating frames/images with detected dice and their values, using a pip counting method.
    '''
    def __init__(
            self,
            data: project_data.ProjectData,
            logging: bool = False
        ):
        super().__init__(
            data=data,
            logging=logging
        )
        if self.logging:
            print(f"Initialized PipsByCount Annotator")

    def get_pip_bounding_boxes(self) -> list:
        """Get bounding boxes for detected pips from the project data."""
        return self.data.get_pip_bounding_boxes()

    def annotate_frame(self):
        """Annotate the frame with detected dice and their values using pip counting."""
        if self.logging:
            print("Annotating frame using pip counting method.")
        self.annotate_dice()
        self.annotate_pips()

    def annotate_dice(self) -> list:
        """Annotate detected dice"""
        dice_boxes = self.data.get_dice_bounding_boxes()
        for box in dice_boxes:
            self.draw_bounding_box_and_label(box_coordinates=box)

    def annotate_pips(self):
        """Annotate detected pips"""
        pip_boxes = self.data.get_pip_bounding_boxes()
        for box in pip_boxes:
            self.draw_bounding_box_and_label(box_coordinates=box)