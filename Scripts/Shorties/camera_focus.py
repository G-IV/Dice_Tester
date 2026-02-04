from Scripts.Modules import vision, motor
import cv2

"""
This script will open up a view window using the vision module, allowing the user to see the camera and adjust the camera settings on the fly.
The script will also allow the user to flip the motor to see how well the dice is visible.
My guess is I'll eventually need to make a json file or some other file where I store the camera settings.
"""

feed = vision.Feed(
    show_annotations=False
    )
# ad2 = motor.Motor()

# autofocus = feed.cap.get(cv2.CAP_PROP_AUTOFOCUS)
# if autofocus == 1:
#     feed.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
#     print(f"Autofocus disabled. {feed.cap.get(cv2.CAP_PROP_AUTOFOCUS)}")

# focus = feed.cap.get(cv2.CAP_PROP_FOCUS)
# print(f"Current focus: {focus}")

# ad2.move_to_position(ad2.POS_90)

while True:
    feed.capture_frame()
    feed.show_frame()
    key = feed.wait(500)
    if key & 0xFF == ord('q'):
        break
    # else:
    #     focus += 5.0
    #     feed.cap.set(cv2.CAP_PROP_FOCUS, int(focus))
    #     print(f"Updated focus + 5: {focus} -> {feed.cap.get(cv2.CAP_PROP_FOCUS)}")
    #     if focus> 255:
    #         break

feed.destroy()
# ad2.close()