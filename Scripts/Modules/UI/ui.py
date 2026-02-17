from abc import ABC, abstractmethod
from pathlib import Path

class UI(ABC):
    """
    This class is responsible for all user interface elements, such as displaying the feed, showing results, and allowing the user to interact with the program.  It should be separate from the main logic of the program, which is handled by the other classes.  This way, if I want to change the UI in the future, I won't have to worry about breaking the core functionality of the program.
    """
    def __init__(
            self,
            logging_enabled: bool = False
        ) -> None:
        self.logging_enabled = logging_enabled

    def display_init_message(self) -> None:
        print("Welcome to the Die Tester!")

    def top_menu_selection(self) -> str:
        print("\n" + "="*50)
        print("Select an option:")
        print("1) Move to uncap position")
        print("2) View single image")
        print("3) Cycle through images in folder")
        print("4) View single video")
        print("5) Gather sample videos for model training")
        print("6) Gather data for dice analysis")
        print("7) Exit")
        print("="*50)

        return input("Enter your choice (1-7): ").strip()
    
    def get_image_directory(self) -> Path | str:
        """Prompts the user to input a directory path and validates it as a directory with image files.  If it returns a string, that indicates there is an issue with the given path."""
        directory_path = self.get_path_to_file_or_dir('directory')
        self.validate_image_directory(directory_path)
        return directory_path
    
    def get_file(self) -> Path | None:
        return self.get_path_to_file_or_dir('file')
    
    def get_path_to_file_or_dir(self, path_type: str) -> Path | None:
        if path_type not in ['file', 'directory']:
            raise ValueError("Invalid path type. Must be 'file' or 'directory'.")
    
        # Set up variables for path validation loop
        bad_path_counter = 0
        max_bad_paths = 3
        path_check = False

        while not path_check:
            # Prompt user for path input
            path = Path(input(f"Enter valid {path_type} path: ").strip())

            # Validate the provided path
            if (path_type == 'file') & path.is_file():
                return path
            elif (path_type == 'directory') & path.is_dir():
                return path

            # If invalid, increment counter and check if max attempts reached
            bad_path_counter += 1
            if bad_path_counter >= max_bad_paths:
                raise ValueError(f"Maximum number of invalid path attempts ({max_bad_paths}) reached.")
            
            # Reprompt user for path input
            path = Path(input(f"Invalid path ({bad_path_counter} of {max_bad_paths}).  Enter valid {path_type} path: ").strip())

    def validate_image_directory(self, folder: Path) -> bool | str:
        if not any(f.suffix.lower() in ['.jpg', '.jpeg', '.png'] for f in folder.iterdir()):
            raise ValueError("Provided folder does not contain any image files.")
        return True 
