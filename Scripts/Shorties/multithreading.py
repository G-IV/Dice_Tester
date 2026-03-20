from Scripts.Modules.Analyzers import analyzer as analyzer_module
from Scripts.Modules.UI.ui import UI
from Scripts.Modules.motor import Motor

from Scripts.Modules.Annotators.annotate_factory import AnnotateFactory
from Scripts.Modules.Data.project_data_factory import ProjectDataFactory
from Scripts.Modules.Dice.dice_factory import DiceFactory
from Scripts.Modules.Feed.feed_factory import FeedFactory

from pathlib import Path
import time
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor as PPE, as_completed # Going to use this for multiprocessing later.

IMG_SAVE_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Captures/Images')

DATABASE_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Database/dice.db')

MODEL = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Scripts/Modules/Analyzers/Models/pips_by_count.pt')
              
MANUAL_VIDEO_PATH = Path('/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Manual/1_Videos')

LOGGING = True

data = ProjectDataFactory.create_project_data(
    data_type="pips_by_count", 
    logging=LOGGING
)

analyzer = analyzer_module.Analyzer(
    model_path=MODEL, 
    data=data, 
    logging=LOGGING
)

annotator = AnnotateFactory.create_annotator(
    annotator_type="pips_by_count", 
    data=data, 
    logging=LOGGING
)

feed = FeedFactory.create_feed(
    feed_type="cam", 
    cam_index=0, 
    annotator=annotator, 
    data=data, 
    logging=LOGGING
)

dice = DiceFactory.create_dice(
    dice_type="pips_by_count", 
    data=data, 
    logging=LOGGING
)

ad2 = Motor(
    logging=LOGGING
)

# Open feed, use ppe to async get frame

with PPE() as executor:
    feed.open_source()
    while True:
        future_motor = executor.submit(ad2.shake)
        future_frame = executor.submit(feed.get_frame)
        for future in as_completed([future_motor, future_frame, future_show_frame]):
            if future == future_motor:
                motor_result = future.result()
                print(f"Shake should be finished")
            elif future == future_frame:
                frame_result = future.result()
                data.set_frame(frame_result)
                future_show_frame = executor.submit(feed.show_frame)
                print(f"Frame was grabbed")