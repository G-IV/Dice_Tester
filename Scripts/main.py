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
    top_level(main_queue)

    while True:
        try:
            item = main_queue.get(timeout=1)  # Wait for an item for up to 1 second
            if ENABLE_LOGGING:
                print(f"Received item: {item}")
            if item.cmd == Command.EXIT: # Exit the application.
                if ENABLE_LOGGING:
                    print("Exit command received. Breaking the loop.")
                break
        except Empty:
            if ENABLE_LOGGING:
                print("Empty queues are expected since we've added a queue timeout.")
        break

    # Breakdown
    close_queue(main_queue)

def top_level(queue: mp.Queue) -> None:
    # This is just for proving that the queue is working and that we can exit the application gracefully.
    queue.put(QueueData(cmd=Command.EXIT, data=None))

if __name__ == "__main__":
    main()
    print("Die Tester Application has terminated.")
