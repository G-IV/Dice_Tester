# Project modules imports
from Scripts.Modules.Data.project_data import ProjectData

# Analaysis support imports
from ultralytics import YOLO
import math

# Data type imports
from ultralytics.engine.results import Results

# Class support imports
from abc import ABC, abstractmethod
from enum import Enum, auto

class DiceState(Enum):
    UNKNOWN = auto()
    MOVING = auto()
    SETTLED = auto()

class Dice(ABC):
    """
    This class assumes there is a model already trained for it.  The whole purpose of this class is to interpret the results from the model predictions.
    """
    def __init__(self, data: ProjectData, logging: bool = False) -> None:
        self.project_data = data
        self.logging = logging
        self._set_dice_keys()

    def _set_dice_keys(self) -> int:
        model = YOLO(self.project_data.model_path)
        self.dice_keys = model.names
        # If the model doesn't have a dice key, we have a serious issue, so we should raise an error.  By doing this here, I can be confident in other class functions that I won't have this issue.
        try:
            self._dice_key()
        except ValueError as e:
            if self.logging:
                print(f"Error in _set_dice_keys: {e}")
            raise e
        except Exception as e:
            if self.logging:
                print(f"Unexpected error in _set_dice_keys: {e}")
            raise e

    def _dice_key(self) -> int | None:
        """Get the class id for the dice class.  This is necessary because different models may have different class ids for the dice."""
        for key, name in self.dice_keys.items():
            if name == "Dice":
                return key
        raise ValueError("Dice class not found in model names.")

    def _dice_center_coords(self, results: Results) -> tuple[float, float] | None:
        """Calculate the center coordinates of the detected dice based on the model results."""
        if not results.boxes:
            return None
        
        """
        I'm not super familiar with working with tensors, so I want to explain what is happening here so I know what's going on the next time I look at this.

        results.boxes.cls is a tensor containing class ids -> tensor([0., 1., 1, 2., ...])
        self.dice_key is the class id for the dice class, so it should be the same data type as any single item in the cls.
        (results.boxes.cls == self.dice_key) creates a boolean tensor where the value is True for any index where the class id matches the dice class, and False otherwise 
            -> (tensor([False, True, False, False, ...]))
        .nonzero() returns the indices of the True values in the boolean tensor -> (tensor([[1], [4], ...]]))
        .nonzero(as_tuple=True) return the indices as a 1D tensor -> (tensor([1, 4, ...]),)
        [0] selects the first element of the tuple, which is the tensor of indices -> tensor(1)
        .numel() returns the number of elements in the tensor, so if there are no dice detected, it will be 0 -> 0
        """
        dice_indices = (results.boxes.cls == self._dice_key()).nonzero(as_tuple=True)[0]
        if dice_indices.numel() == 0:
            return None
        dice_index = dice_indices[0].item()
        x, y, _, _ = results.boxes.xywh[dice_index]
        return (x.item(), y.item())
    
    def get_dice_state(self) -> DiceState:
        
        # Calculate number of frames I want to see a steady state for before I consider the dice settled.
        gap_seconds = 0.25
        gap_frames = 8 # Default to 30fps frames for a 0.25 second gap if fps is not set.
        max_movement_threshold = 3 # This is the maximum distance in pixels that the dice can move in the gap_frames before we consider it moving.  This threshold may need to be adjusted based on the model's accuracy and the camera setup.
        print(f"gap_frames: {gap_frames}, total analyzed frames: {len(self.project_data.results)}")
        if len(self.project_data.results) < gap_frames:
            return DiceState.UNKNOWN
        
        last_frame_coords = self._dice_center_coords(self.project_data.results[-1])
        gap_frame_coords = self._dice_center_coords(self.project_data.results[-gap_frames])

        print(f"last_frame_coords: {last_frame_coords}, gap_frame_coords: {gap_frame_coords}")
        if last_frame_coords is None or gap_frame_coords is None:
            return DiceState.UNKNOWN
        
        distance_moved = math.dist(last_frame_coords, gap_frame_coords)

        print(f"Distance moved in the last {gap_frames} frames: {distance_moved} (min: {max_movement_threshold})")
        if distance_moved > max_movement_threshold: # If the dice moved more than the maximum threshold in the last gap_frames, consider it moving.  This threshold may need to be adjusted based on the model's accuracy and the camera setup.
            return DiceState.MOVING

        return DiceState.SETTLED
    