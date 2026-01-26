'''
The purpose of this file is to use the webcam to take still images of the die being tested.  These images can then be used for training a machine learning model to recognize the die and its pips, which will be used in the main testing process to determine the result of each test.  The file will include functionality to capture images, save them with appropriate naming conventions, and potentially allow for manual labeling of the images for training purposes.

I need to be able to show a window with the webcam feed and uses the keyboard [space] key to capture an image.  When the [space] button is pressed, the current frame from the webcam should be saved as an image file in a specified directory.  The file name should include a timestamp to ensure uniqueness and to help with organizing the images for training.
'''
import cv2
import os
from datetime import datetime   

# Directory to save captured images
SAVE_DIR = './single-side/captured_images'
# Create the directory if it doesn't exist
os.makedirs(SAVE_DIR, exist_ok=True)

def capture_images():
    # Initialize webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Press [space] to capture an image, or [q] to quit.")

    while True:
        # Read frame from webcam
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame.")
            break

        # Display the webcam feed
        cv2.imshow('Webcam Feed', frame)

        # Wait for key press
        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):  # Space key to capture image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{SAVE_DIR}/die_image_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Image captured and saved as {filename}")
        
        elif key == ord('q'):  # 'q' key to quit
            print("Exiting...")
            break

    # Release the webcam and close windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_images()