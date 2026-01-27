from Scripts.Modules import vision
import time

cam = vision.open_camera()
window_name = vision.open_camera_feed(cam)

frame = vision.capture_frame(cam)
detections = vision.detect_dice(frame)

print("Detections:", detections)