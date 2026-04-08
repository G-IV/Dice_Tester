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
        if self.logging:
            print(f"Closing connection to AD2 board and closing queues.")
        wavegen.close(self.device_data)
        device.close(self.device_data)
        while True:
            try:
                self.motor_q.get_nowait() # Clear out any remaining commands in the motor queue.
            except Empty:
                if self.logging:
                    print(f"Queue is emptied")
                self.motor_q.join() # Wait for the motor thread to finish processing any remaining commands and exit.
                break
    
    def _motor_control_loop(self) -> None:
        """
        The main loop for controlling the motor, it monitors the motor queue for commands.
        """
        if self.logging:
            print("Motor control thread started.")
        
        while True:
            try:
                item = self.motor_q.get(timeout=1)  # Wait for a command for up to 1 second
                match item.cmd:
                    case Command.EXIT:
                        if self.logging:
                            print("Exit command received in motor control thread. Breaking the loop.")
                        self._close()
                        break
                    case Command.FLIP:
                        if self.logging:
                            print("Flip command received in motor control thread. Flipping the motor.")
                        self.position = self.POS_90N if self.position == self.POS_90 else self.POS_90
                        self._setPWM(symmetry=self.position)
                        time.sleep(1) # Gives motor time to get to position before accepting another command.
                    case Command.MOVE_TO:
                        if self.logging:
                            print(f"Move to command received in motor control thread. Moving to position: {item.data}")
                        self.position = item.data
                        self._setPWM(symmetry=item.data)
                        time.sleep(1) # Gives motor time to get to position before accepting another command.
                    case _:
                        if self.logging:
                            print(f"Received unrecognized command in motor control thread: {item}")
            except Empty:
                # This case handles the timeout exception, which we expect.
                continue
            except Exception as e:
                if self.logging:
                    print(f"An unexpected error occurred in the motor control thread: {e}. Exiting thread.")
                self._close()
                break
        
        if self.logging:
            print("Motor control thread exiting.")

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
            run_time=10.0, 
            wait=1.0, 
            repeat=1)
    
    def close(self) -> None:
        """
        Public method to close the motor connection and clean up resources.
        """
        if self.logging:
            print("Close method called on Motor class. Sending exit command to motor control thread.")
        self.motor_q.put(MotorData(cmd=Command.EXIT, data=None))
        time.sleep(2) # Give the motor thread time to process the exit command and close the connection.

    def flip(self) -> None:
        """
        Public method to flip the motor between the two positions.
        """
        if self.logging:
            print("Flip method called on Motor class. Sending flip command to motor control thread.")
        self.motor_q.put(MotorData(cmd=Command.FLIP, data=None))

    def move_to_uncap(self) -> None:
        """
        Public method to move the motor to the uncap position.
        """
        if self.logging:
            print("Move to uncap method called on Motor class. Sending move to uncap command to motor control thread.")
        self.motor_q.put(MotorData(cmd=Command.MOVE_TO, data=self.POS_UNCAP))

    def move_to_position(self, position: int) -> None:
        """
        Public method to move the motor to a specific position.

        Position should range between 14 and 84, this isn't enforced because sometimes the motor loses its position.
        
        """
        if self.logging:
            print(f"Move to position method called on Motor class. Sending move to position command with position {position} to motor control thread.")
        self.motor_q.put(MotorData(cmd=Command.MOVE_TO, data=position))

    