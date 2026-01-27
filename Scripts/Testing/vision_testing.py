import cv2
from Scripts.Modules import vision
import time

def test_open_close_camera_with_window():
    """
    Test opening and closing the camera feed.
    1. Open the camera.
    2. Open the camera feed window.
    3. Wait for 5 seconds to allow visual verification.
    4. Close the camera feed window.
    5. Close the camera.
    """
    print("Vision test: Opening camera...")
    cam = vision.open_camera()

    print("Opening camera feed window...")
    window_name = vision.open_feed_window(cam)

    print("Waiting for 5 seconds to verify camera feed...")
    time.sleep(5)

    print("Closing camera feed window...")
    vision.close_feed_window(window_name)

    print("Closing camera...")
    vision.close_camera(cam)

    print("Vision test completed successfully.")

def test_send_mp4_frames_to_window():
    """
    Test sending frames to the camera feed window.
    1. Open the camera.
    2. Open the camera feed window.
    3. Send 10 frames to the window with a brief pause in between.
    4. Close the camera feed window.
    5. Close the camera.
    """

    mp4_path = '/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Cross_Bars/1_Videos/roll_1_20260125_133620.mp4'

    print("Vision test: Opening MP4 file...")
    cap = vision.open_mp4(mp4_path)

    print("Opening MP4 feed window...")
    window_name = vision.open_feed_window(cap)

    print("Sending frames to MP4 feed window...")
    while True:
        ret, frame = cap.read()
        if ret:
            vision.show_frame_in_window(window_name, frame)
            time.sleep(0.1)  # Brief pause between frames
        else:
            print("No more frames to read or failed to read frame.")
            break
    
    print("Closing MP4 file...")
    vision.close_mp4(cap)

    print("Closing MP4 feed window...")
    vision.close_feed_window(window_name)

    print("Vision test completed successfully.")

def test_draw_box_around_dice_in_frame():
    """
    Test the YOLO model's ability to detect dice in a single frame.
    1. Open the MP4 file.
    2. Capture a single frame.
    3. Run the YOLO model on the captured frame.
    4. Print the detection results.
    5. Close the MP4 file.
    """
    mp4_path = '/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Cross_Bars/1_Videos/roll_1_20260125_133620.mp4'
    print("Vision test: Opening camera...")
    cam = vision.open_mp4(mp4_path)

    print("Capturing a single frame...")
    frame = vision.capture_frame(cam)

    print("Running YOLO model on captured frame...")
    detections = vision.analyze_frame(frame)
    vision.add_bounding_box_to_frame(frame, detections)
    # frame_with_box = vision.draw_boxes_on_frame(frame, x1, y1, x2, y2)
    window = vision.open_feed_window(cam)
    # vision.show_frame_in_window(window, frame_with_box)
    time.sleep(5)  # Pause to view the frame with boxes
    vision.close_feed_window(window)
    vision.close_mp4(cam)

    print("Detection results:")
    # print(results[0])
    # print(results[0].boxes)

    print("Closing camera...")
    vision.close_camera(cam)

    print("Vision test completed successfully.")

def test_pip_counting():
    mp4_path = '/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Modeling/Cross_Bars/1_Videos/roll_1_20260125_133620.mp4'
    print("Vision test: Opening camera...")
    cam = vision.open_mp4(mp4_path)

    print("Capturing a single frame...")
    frame = vision.capture_frame(cam)

    print("Running YOLO model on captured frame...")
    results = vision.analyze_frame(frame)

    print("Pips counted:")
    pips = vision.count_pips_from_detections(results)
    print(pips)

    print("Closing camera...")
    vision.close_camera(cam)

    print("Vision test completed successfully.")

# Run the tests
# test_open_close_camera_with_window()
# test_send_mp4_frames_to_window()
# test_draw_box_around_dice_in_frame()
# test_pip_counting()