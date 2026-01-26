'''
The goal of this this python script is to extract still image from each video located in a specified input directory and save them as individual image files in a specified output directory. The script processes all video files in the input directory, extracts each frame from the videos, and saves them as image files in the output directory with a naming convention that includes the original video filename and the frame number.
'''
import cv2
import os

def video_to_stills(input_dir, output_dir):
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Iterate over all files in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):  # Add more video formats if needed
            video_path = os.path.join(input_dir, filename)
            cap = cv2.VideoCapture(video_path)

            frame_count = 0
            success, frame = cap.read()
            while success:
                # Construct the output image filename
                image_filename = f"{os.path.splitext(filename)[0]}_frame{frame_count:04d}.jpg"
                image_path = os.path.join(output_dir, image_filename)

                # Save the frame as an image file
                cv2.imwrite(image_path, frame)

                # Read the next frame
                success, frame = cap.read()
                frame_count += 1

            cap.release()
            print(f"Extracted {frame_count} frames from {filename}")

if __name__ == "__main__":
    input_directory = "/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/5 - Tower Rolls/Videos"  # Replace with your input directory path
    output_directory = "/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/5 - Tower Rolls/Stills"  # Replace with your output directory path
    video_to_stills(input_directory, output_directory)