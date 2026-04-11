# Parallel processing related imports
from concurrent.futures import ProcessPoolExecutor as PPE
import multiprocessing as mp
from multiprocessing.queues import Empty
import time

# Project module imports
from Scripts.Modules.queue_data import QueueData, Command as QuCmd
from Scripts.Modules.Stream.stream import Stream
from Scripts.Modules.Motor.ad2 import Motor
from Scripts.Modules.Feed.feed_factory import FeedFactory

# Constants
ENABLE_LOGGING = True

def close_queue(queue: mp.Queue) -> None:
    """
    Closes the queue and ensures that all remaining items are processed before exiting.
    """
    # Stop any more data from being added to the queue.
    queue.close()
    # Empty the queue of any remaining items.
    while not queue.empty():
        try:
            item = queue.get_nowait()
            if ENABLE_LOGGING:
                print(f"Processing item: {item}")
            if item.cmd == QuCmd.EXIT:
                break
        except Empty:
            if ENABLE_LOGGING:
                print("Main queue is empty. No more items to process.")
            break
    # Queue is now empty and closed, we can safely join the thread.
    queue.join_thread()  # Wait for the queue to be fully processed before exiting.

def main() -> None:
    """
    Starting point for the application.  This is where the user will manage the activities of the application.
    """
    print("Starting the Tester Application...")

    # Setup
    main_queue = mp.Queue()
    stream = Stream(logging=ENABLE_LOGGING)

    # The first thing we should send to the queue is command to enter the user selection state.
    main_queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))

    while True:
        try:
            item = main_queue.get(timeout=1)  # Wait for an item for up to 1 second
            if ENABLE_LOGGING:
                print(f"Received item: {item}")
            match item.cmd:
                case QuCmd.MAIN_MENU:
                    top_level(main_queue)
                case QuCmd.MOVE_TO_UNCAP:
                    if ENABLE_LOGGING:
                        print("Move to uncap position command received.")
                    move_to_uncap(main_queue)
                case QuCmd.FRAME_READY:
                    if ENABLE_LOGGING:
                        print("Frame ready command received. Displaying frame...")
                    stream.show_frame(item.data)
                case QuCmd.EXIT: # Exit the application.
                    if ENABLE_LOGGING:
                        print("Exit command received. Breaking the loop.")
                    break
        except Empty:
            if ENABLE_LOGGING:
                print("Empty queues are expected since we've added a queue timeout.")
        except Exception as e:
            if ENABLE_LOGGING:
                print(f"An unexpected error occurred: {e}.  Exiting the application.")
            break

    # Breakdown
    close_queue(main_queue)
    stream.destroy()

"""
These are the main functions for the application.  The main function is responsible for managing the overall flow of the application, while the top_level function is responsible for presenting the user with options and handling their selections.
"""
def top_level(queue: mp.Queue) -> None:
    """
    This function represents the top-level logic of the application.  It allows the user to select which activity they want to perform.

    This is a blocking function.
    """
    print("\n" + "="*50)
    print("Select an option:")
    print("0) Exit")
    print("1) Move to uncap position")
    print("2) View single image")
    print("3) Cycle through images in folder")
    print("4) View single video")
    print("5) Gather sample videos for model training")
    print("6) Gather data for dice analysis")
    print("="*50)

    choice = input("Enter your choice (0-6): ").strip()

    match choice:
        case "0":
            if ENABLE_LOGGING:
                print("'Exit' selected.")
            queue.put(QueueData(cmd=QuCmd.EXIT, data=None))
        case "1":
            if ENABLE_LOGGING:
                print("'Move to uncap position' selected.")
            queue.put(QueueData(cmd=QuCmd.MOVE_TO_UNCAP, data=None))
        case _:
            if ENABLE_LOGGING:
                print(f"You selected: {choice}. This option is not implemented yet.")
            queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))

def move_to_uncap(queue: mp.Queue) -> None:
    """
    This function is responsible for moving the camera to the uncap position.  This is a placeholder function and does not contain any actual logic for moving the camera.
    """
    if ENABLE_LOGGING:
        print("Moving to uncap position...)")
    try:
        motor = Motor(logging=ENABLE_LOGGING, main_queue=queue)
    except Exception as e:
        if ENABLE_LOGGING:
            print(f"An error occurred while moving to uncap position: {e}")
        queue.put(QueueData(cmd=QuCmd.EXIT, data=None))
        return
    motor.move_to_uncap()
    input('Press Enter to return to the main menu...')
    motor.close() # Ensure we close the motor connection when we're done.
    # After completing the action, return to the main menu
    queue.put(QueueData(cmd=QuCmd.MAIN_MENU, data=None))

if __name__ == "__main__":
    main()
    print("Die Tester Application has terminated.")
