# Parallel processing related imports
from concurrent.futures import ProcessPoolExecutor as PPE
import multiprocessing as mp
from multiprocessing.queues import Empty

# Custom module imports
from Modules.queue_data import QueueData, Command

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
            if item.cmd == Command.EXIT:
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

    # The first thing we should send to the queue is command to enter the user selection state.
    main_queue.put(QueueData(cmd=Command.MAIN_MENU, data=None))

    while True:
        try:
            item = main_queue.get(timeout=1)  # Wait for an item for up to 1 second
            if ENABLE_LOGGING:
                print(f"Received item: {item}")
            match item.cmd:
                case Command.MAIN_MENU:
                    top_level(main_queue)
                case Command.EXIT: # Exit the application.
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
            print("You selected: Exit")
            queue.put(QueueData(cmd=Command.EXIT, data=None))
        case _:
            print(f"You selected: {choice}. This option is not implemented yet.")
            queue.put(QueueData(cmd=Command.MAIN_MENU, data=None))

if __name__ == "__main__":
    main()
    print("Die Tester Application has terminated.")
