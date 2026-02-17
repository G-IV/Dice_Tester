from Scripts.Modules.Feed.feed import Feed
from Scripts.Modules.Annotators import annotate

class Annotator(annotate.Annotator):
    '''
    A class for annotating frames/images with detected dice and their values, using a pip counting method.
    '''
    def __init__(
            self,
            feed: Feed,
            logging: bool = False
        ):
        super().__init__(
            feed=feed,
            logging=logging
        )
        if self.logging:
            print(f"Initialized PipsByCount Annotator")

    def annotate_die(self):
        """Place a single bounding box around a detected die and label it with the detected value."""
        if self.logging:
            print("Annotating frame with detected dice using pip counting method.")
        # Placeholder for annotation logic, which would use self.feed.data.analysis results to draw bounding boxes and labels on self.feed.frame based on pip counting method
        pass

    def annotate_all_dice(self):
        """Place bounding boxes around all detected dice and label them with their detected values."""
        if self.logging:
            print("Annotating frame with all detected dice using pip counting method.")
        # Placeholder for annotation logic, which would use self.feed.data.analysis results to draw bounding boxes and labels on self.feed.frame based on pip counting method
        pass