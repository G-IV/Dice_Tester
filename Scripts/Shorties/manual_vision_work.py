'''
This script combines motor control and vision processing to analyze die rolls.
It captures frames from a video feed, detects dice using a YOLO model, and overlays bounding boxes and additional information on the frames.
The motor is controlled to adjust the position of the die, and the system monitors the stability of the die's position.
When the dice have stabilized, the motor moves to the next position.
'''

# from curses import window
from Scripts.Modules import vision
from Scripts.Modules import motor
import time

'''
# Add a boundging box around the detected die
mp4_path = '/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Cross_Bars/1_Videos/roll_1_20260125_133620.mp4'

print("Vision test: Opening camera...")
cam = vision.open_mp4(mp4_path)

window = vision.open_feed_window(cam)

print("Capturing a single frame...")
frame = vision.capture_frame(cam)

print("Running YOLO model on captured frame...")
detections = vision.analyze_frame(frame)

vision.add_bounding_box_to_frame(frame, detections)
vision.show_frame_in_window(window, frame)

time.sleep(5)  # Pause to view the frame with boxes

vision.close_feed_window(window)
vision.close_mp4(cam)

print("Vision test completed successfully.")
'''

# Add bounding boxes to the frame
# Add a border + details to the frame
# Show state of motion to the frame
mp4_path = '/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Cross_Bars/1_Videos/roll_1_20260125_133620.mp4'

print("Vision test: Opening camera...")
cam = vision.open_camera()

window = vision.open_feed_window(cam)
dice = vision.Dice()

ad2 = motor.open()
position = motor.move_to_position(ad2, 50)
time.sleep(2)

for _ in range(10):
    position = motor.get_next_position(position)
    position = motor.move_to_position(ad2, position)
    time.sleep(1)

    while True:
        print("Capturing a single frame...")
        ret, frame = vision.capture_frame(cam)
        if not ret:
            print("No more frames to read or failed to read frame.")
            break
        else:
            detections = vision.analyze_frame(frame)

            # Update the coordinate buffer with the die's center position if detected
            dice.add_coordinate(detections)
            pips = vision.count_pips_from_detections(detections)
            frame = vision.add_bounding_box_to_frame(frame, detections)
            frame = vision.add_border_details_to_frame(frame, 400, dice.dice_state(), pips)
            vision.show_frame_in_window(window, frame)
            if dice.dice_state() == 'stable':
                print("Die is stable, moving motor to next position.")
                break
            if dice.is_stuck():
                position = motor.get_next_position(position)
                position = motor.move_to_position(ad2, position)
                time.sleep(1.25)
                position = motor.get_next_position(position)
                position = motor.move_to_position(ad2, position)
                time.sleep(1.25)

vision.close_feed_window(window)
vision.close_camera(cam)
motor.close(ad2)

print("Vision test completed successfully.")