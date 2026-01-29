from Scripts.Modules import data, motor, vision
import time
from datetime import datetime

IMG_SAVE_PATH = '/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Database/Images'

def main():
    print("Starting Die Tester Application")
    # Initialize modules
    data.initialize_database()
    # dice_id = data.get_next_id()
    dice_id = 2
    dice = vision.Dice()
    ad2 = motor.open()
    cam = vision.open_camera()
    window = vision.open_feed_window(cam)
    pips = 0
    position = None

    print(f"Testing dice with ID: {dice_id}")

    position = motor.move_to_default_position(ad2)
    time.sleep(2)  # Allow time for motor to reach default position

    number_of_samples_taken = 0
    max_samples = 1000-4  # Number of samples to take per dice
    
    print(f"Beginning main testing loop. {dice_id} will be tested for {max_samples} samples.")
    # Main loop
    while True:
        print(f"\n\n++++++++++++++\nTaking sample {number_of_samples_taken + 1} for dice ID {dice_id}.\n++++++++++++++\n\n")

        dice.reset()

        # Rotate the motor to roll the dice
        position = motor.flip_position(position)
        time.sleep(.25)  # Short delay before observing dice state

        print("Begin monitoring dice state.")
        while True:
            # Capture image from camera
            ret, frame = vision.capture_frame(cam)
            if not ret:
                print("Failed to capture frame from camera.")
                continue
            
            print("Processing image and detecting dice.")
            detections = vision.analyze_frame(frame)

            dice.add_coordinate(detections)
            pips = vision.count_pips_from_detections(detections)

            framed_image = vision.add_bounding_box_to_frame(frame, detections)
            framed_image = vision.add_border_details_to_frame(framed_image, 400, dice, pips)

            print("Displaying frame with detected information.")
            vision.show_frame_in_window(window, framed_image) 

            if dice.dice_state() == 'stable':
                print("Die is stable, proceeding to log results.")
                break

            time.sleep(0.1)  # Small delay to avoid overwhelming the CPU
        
        # Store results
        print("Logging test results to database.")
        timestamp = datetime.now().isoformat()
        dice.update_previous_rolls(pips)
        img_path = vision.save_image(frame, IMG_SAVE_PATH, dice_id, timestamp)
        data.log_test_result(dice_id, timestamp, position, pips, img_path)
        
        print("Preparing for next sample.")
        number_of_samples_taken += 1
        if number_of_samples_taken >= max_samples:
            print(f"Completed {max_samples} samples for dice ID {dice_id}.")
            break

    # Cleanup
    print("Cleaning up resources and closing application.")
    motor.close(ad2)
    vision.close_feed_window(window)
    vision.close_camera(cam)


if __name__ == "__main__":
    main()
    print("Die Tester Application has terminated.")