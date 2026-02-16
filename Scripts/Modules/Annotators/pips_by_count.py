from Scripts.Modules.Feed.feed import Feed
from Scripts.Modules.Annotators.annotate import Annotator

class PipsByCountAnnotator(Annotator):
    '''
    A class for annotating frames/images with detected dice and their values, using a pip counting method.
    '''
    def __init__(
            self, 
            logging: bool = False,
            feed: Feed = None
        ):
        super().__init__(
            logging=logging,
            feed=feed
        )

    def annotate_die(self):
        """Place a single bounding box around a detected die and label it with the detected value."""
        if self.logging:
            print("Annotating frame with detected dice using pip counting method.")
        # Placeholder for annotation logic, which would use self.feed.data.analysis results to draw bounding boxes and labels on self.feed.frame based on pip counting method
        pass

    def annotate_all_dice(self):
        """Place bounding boxes around all detected dice and label them with their detected values."""
        if self.logging:
            print("Annotating frame with all detected dice.")
        # Placeholder for annotation logic, which would use self.feed.data.analysis results to draw bounding boxes and labels on self.feed.frame based on pip counting method
        pass