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
    window_name = vision.open_camera_feed(cam)

    print("Waiting for 5 seconds to verify camera feed...")
    time.sleep(5)

    print("Closing camera feed window...")
    vision.close_camera_feed(window_name)

    print("Closing camera...")
    vision.close_camera(cam)

    print("Vision test completed successfully.")

test_open_close_camera_with_window()