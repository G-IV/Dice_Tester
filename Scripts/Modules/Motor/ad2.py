"""
The motor is a stepper motor with 180° range of motion.
We'll be controlling the stepper motor positioning using an old Digilent Analog Discovery 2 board as a signal generator.
Digilent published an SDK I can use to communicate with the board:
https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual
https://digilent.com/reference/test-and-measurement/guides/waveforms-sdk-getting-started#creating_modules
"""

# To use the SDK, we have to do a song and dance:
from Scripts.Modules.Motor.WF_SDK import device, wavegen

# To parallelize the motor control, we'll use threading and a queue.
from threading import Thread
from queue import Queue, Empty
import time
from enum import Enum, auto

class Command(Enum):
    EXIT = auto()
    FLIP = auto()
    MOVE_TO = auto()
    RESET_POSITION = auto()

class MotorData:
    """
    A simple data class to hold information about motor commands.
    Format:

        "cmd": "Command value",
        "data": "Associated data"

    The data can be just about anything, so I don't need to do any type enforcement.
    """
    def __init__(self, cmd: Command, data) -> None:
        self.cmd = cmd
        self.data = data

    def __repr__(self) -> str:
        return f"Motor command: (cmd={self.cmd}, data={self.data})"

class Motor:
    """
    A class to control the stepper motor using the AD2 board.
    """

    # PWM frequency for the stepper motor.
    FREQUENCY = 333

    # Duty cycle values for vertical positioning.
    POS_90 = 14
    POS_90N = 84
    POS_START = POS_90
    POS_UNCAP = POS_90

    def __init__(self, logging: bool = False, main_queue: Queue = None) -> None:
        """
        Initializes the motor control thread and queue.
        """
        self.logging = logging
        self.main_q = main_queue

        self.device_data = device.open()

        # Set up the thread for motor control.
        self.motor_q = Queue()
        # Setting daemon=True means that the thread will automatically close when the main program exits, so we don't have to worry about it hanging around.
        self.motor_thread = Thread(target=self._motor_control_loop, daemon=True)
        self.motor_thread.start()

    def _close(self) -> None:
        """
        Closes the connection to the AD2 board and performs any necessary cleanup.
        """
        wavegen.close(self.device_data)
        device.close(self.device_data)
    
    def _motor_control_loop(self) -> None:
        """
        The main loop for controlling the motor, it monitors the motor queue for commands.
        """
        while True:
            try:
                item = self.motor_q.get(timeout=1)  # Wait for a command for up to 1 second
                match item.cmd:
                    case Command.EXIT:
                        self._close()
                        break
                    case Command.FLIP:
                        self.position = self.POS_90N if self.position == self.POS_90 else self.POS_90
                        self._setPWM(symmetry=self.position)
                        time.sleep(1) # Gives motor time to get to position before accepting another command.
                    case Command.MOVE_TO:
                        self.position = item.data
                        self._setPWM(symmetry=item.data)
                        time.sleep(1) # Gives motor time to get to position before accepting another command.
                    case Command.RESET_POSITION:
                        self.motor_q.put(MotorData(cmd=Command.FLIP, data=None)) # Flip the motor to reset it. This will be followed by another flip command to return it to the original position, which is handled in the main process.
                        time.sleep(3) # Wait for the camera to stabilize before we begin capturing frames.
                        self.motor_q.put(MotorData(cmd=Command.FLIP, data=None)) # Flip the motor again to start a new roll.
                        time.sleep(3) # Wait for the camera
                    case _:
                        pass
            except Empty:
                # This case handles the timeout exception, which we expect.
                continue
            except Exception as e:
                self._close()
                print(f"ad2.py _motor_control_loop encountered an error: {e}")
                break

    def _setPWM(self, symmetry: int = 50) -> None:
        """
        Internal method to set the PWM signal on the AD2 board to control the motor position.
        """
        wavegen.generate(
            symmetry=symmetry, 
            device_data = self.device_data, 
            channel=0, 
            function=wavegen.function.pulse, 
            frequency=333,  
            amplitude=5.0, 
            offset=0.0, 
            run_time=0, # Runs indefinitely until we tell it to stop, which is what we want for the stepper motor.
            wait=0, 
            repeat=0)
    
    def _reset_position(self) -> None:
        """
        Internal method to reset the motor position by flipping it twice.
        """
        self._setPWM(symmetry=self.POS_90N)
        time.sleep(1) # Give the motor time to get to the new position before flipping again.
        self._setPWM(symmetry=self.POS_90)
        time.sleep(1) # Give the motor time to get back to the original position before accepting new commands.

    def close(self) -> None:
        """
        Public method to close the motor connection and clean up resources.
        """
        self.motor_q.put(MotorData(cmd=Command.EXIT, data=None))
        self.motor_thread.join() # Wait for the motor control thread to finish before exiting.
        while True:
            try:
                self.motor_q.get_nowait() # Clear out any remaining commands in the motor queue.
            except Empty:
                break

    def flip(self) -> None:
        """
        Public method to flip the motor between the two positions.
        """
        self.motor_q.put(MotorData(cmd=Command.FLIP, data=None))

    def move_to_uncap(self) -> None:
        """
        Public method to move the motor to the uncap position.
        """
        self.motor_q.put(MotorData(cmd=Command.MOVE_TO, data=self.POS_UNCAP))

    def move_to_position(self, position: int) -> None:
        """
        Public method to move the motor to a specific position.

        Position should range between 14 and 84, this isn't enforced because sometimes the motor loses its position.
        
        """
        self.motor_q.put(MotorData(cmd=Command.MOVE_TO, data=position))

    def reset_position(self) -> None:
        """
        Public method to reset the motor position by flipping it twice.
        """
        self.motor_q.put(MotorData(cmd=Command.RESET_POSITION, data=None))