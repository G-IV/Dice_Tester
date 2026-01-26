'''
This script is designed to test the logic of the die tester application using recorded mp4 files instead of a live camera feed.
'''

# Imports
from Modules import Vision
import os
import random

# Constants
MP4_FILE_PATH = '/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/5 - Tower Rolls/Videos'

def get_random_mp4_file():
    """
        This retreives a random mp4 file from the specified directory for testing purposes.
    """
    files = [f for f in os.listdir(MP4_FILE_PATH) if f.endswith('.mp4')]
    random_file = random.choice(files)
    return os.path.join(MP4_FILE_PATH, random_file)  

if __name__ == "__main__":
    """
        Main function to run the die tester logic using an mp4 file.
    """
    mp4_file = get_random_mp4_file()
    print(f"Using mp4 file for testing: {mp4_file}")
    # Open the mp4 file instead of a live camera feed
    video_capture = Vision.load_mp4_file(mp4_file)
        
    # Release the video capture object
    video_capture.release()
    print("Video processing completed.")