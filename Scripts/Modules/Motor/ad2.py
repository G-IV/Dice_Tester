"""
The motor is a stepper motor with 180° range of motion.
We'll be controlling the stepper motor positioning using an old Digilent Analog Discovery 2 board as a signal generator.
Digilent published an SDK I can use to communicate with the board:
https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual
https://digilent.com/reference/test-and-measurement/guides/waveforms-sdk-getting-started#creating_modules
"""

# To use the SDK, we have to do a song and dance:
from Scripts.Modules.Motor.WF_SDK import device, wavegen
from Scripts.Modules.queue_data import QueueData, Command as QuCmd

# To parallelize the motor control, we'll use threading and a queue.
from threading import Thread, current_thread
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

class MotorState(Enum):
    """
    An enum to represent the current state of the motor.
    """
    UNINITIALIZED = auto()
    STEADY = auto()
    RESETTING = auto()

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

    # Monitor state of the motor, will help with the main process logic.
    state = MotorState.UNINITIALIZED


    def __init__(self, logging: bool = False, main_queue: Queue = None) -> None:
        """
        Initializes the motor control thread and queue.
        """
        self.logging = logging
        self.main_q = main_queue

        self.device_data = device.open()

        # Set up the thread for motor control.
        self.motor_q = Queue()
        self._closed = False
        # Setting daemon=True means that the thread will automatically close when the main program exits, so we don't have to worry about it hanging around.
        self.motor_thread = Thread(target=self._motor_control_loop, daemon=True)
        self.motor_thread.start()

    def _close(self) -> None:
        """
        Closes the connection to the AD2 board and performs any necessary cleanup.
        """
        if self._closed:
            return

        if self.logging:
            print("ad2.py _close() called, closing connection to AD2 board.")

        self.state = MotorState.UNINITIALIZED

        wavegen.close(self.device_data)
        device.close(self.device_data)
        self._closed = True

        if self.logging:
            print("  -> Connection to AD2 board closed.")
    
    def _motor_control_loop(self) -> None:
        """
        The main loop for controlling the motor, it monitors the motor queue for commands.
        """
        self.state = MotorState.STEADY
        if self.logging:
            print("ad2.py _motor_control_loop started, waiting for motor commands.")
        while True:
            try:
                item = self.motor_q.get(timeout=1)  # Wait for a command for up to 1 second
                match item.cmd:
                    case Command.EXIT:
                        if self.logging:
                            print("ad2.py _motor_control_loop received EXIT command.")
                        break
                    case Command.FLIP:
                        if self.logging:
                            print("ad2.py _motor_control_loop received FLIP command, calling _setPWM().")
                        self.position = self.POS_90N if self.position == self.POS_90 else self.POS_90
                        if self.logging:
                            print(f"  -> Sending {self.position} to _setPWM()...")
                        self._setPWM(symmetry=self.position)
                        time.sleep(1) # Gives motor time to get to position before accepting another command.
                        if self.logging:
                            print("  -> 1 second delay completed.")
                    case Command.MOVE_TO:
                        if self.logging:
                            print(f"ad2.py _motor_control_loop received MOVE_TO command, moving to position {item.data}.")
                        self.position = item.data
                        if self.logging:
                            print(f"  -> Setting {self.position}")
                        self._setPWM(symmetry=item.data)
                        time.sleep(1) # Gives motor time to get to position before accepting another command.
                        if self.logging:
                            print("  -> 1 second delay completed.")
                    case Command.RESET_POSITION:
                        sleep_time = 1.5
                        if self.logging:
                            print("ad2.py _motor_control_loop received RESET_POSITION command, resetting position.")
                        self.position = self.POS_90N if self.position == self.POS_90 else self.POS_90
                        self._setPWM(symmetry=self.position)
                        time.sleep(sleep_time) # Wait for the camera to stabilize before we begin capturing frames.
                        if self.logging:
                            print(f"  -> First flip completed + {sleep_time} seconds delay.")
                        self.position = self.POS_90N if self.position == self.POS_90 else self.POS_90
                        self._setPWM(symmetry=self.position)
                        time.sleep(sleep_time) # Wait for the camera
                        if self.logging:
                            print(f"  -> Second flip completed + {sleep_time} seconds delay.")
                        self.main_q.put(QueueData(cmd=QuCmd.MOTOR_RESET_COMPLETE, data=None)) # Notify the main process that we've completed the reset so it can update its state accordingly.
                    case _:
                        if self.logging:
                            print(f"ad2.py _motor_control_loop received unknown command: {item.cmd}, ignoring it.")
                        pass
            except Empty:
                # This case handles the timeout exception, which we expect.
                continue
            except Exception as e:
                self._close()
                if self.logging:
                    print("ad2.py _motor_control_loop encountered an unexpected error, closing connection to AD2 board and exiting motor control loop.")
                print(f"ad2.py _motor_control_loop encountered an error: {e}")
                break
        
        if self.logging:
            print("  -> Motor control thread closed, calling _close() to clean up connection to AD2 board.")

        self._close()

    def _setPWM(self, symmetry: int = 50) -> None:
        """
        Internal method to set the PWM signal on the AD2 board to control the motor position.
        """
        if self.logging:
            print(f"ad2.py _setPWM called with symmetry={symmetry}, setting PWM signal on AD2 board.")
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
    
    def close(self) -> None:
        """
        Public method to close the motor connection and clean up resources.
        """
        if self.logging:
            print("ad2.py Motor.close() called, sending EXIT command to motor control thread")
        self.motor_q.put(MotorData(cmd=Command.EXIT, data=None))
        if self.logging:
            print("  -> EXIT command sent, waiting for motor control thread to finish...")
        if current_thread() is not self.motor_thread:
            self.motor_thread.join() # Wait for the motor control thread to finish before exiting.
        else:
            if self.logging:
                print("  -> close() called from motor thread; skipping join().")
        if self.logging:
            print("  -> Motor control thread finished, motor connection closed.")

    def flip(self) -> None:
        """
        Public method to flip the motor between the two positions.
        """
        if self.logging:
            print("ad2.py Motor.flip() called, sending FLIP command to motor control thread.")
        self.motor_q.put(MotorData(cmd=Command.FLIP, data=None))

    def move_to_uncap(self) -> None:
        """
        Public method to move the motor to the uncap position.
        """
        if self.logging:
            print("ad2.py Motor.move_to_uncap() called, sending MOVE_TO command with POS_UNCAP to motor control thread.")
        self.motor_q.put(MotorData(cmd=Command.MOVE_TO, data=self.POS_UNCAP))

    def move_to_position(self, position: int) -> None:
        """
        Public method to move the motor to a specific position.

        Position should range between 14 and 84, this isn't enforced because sometimes the motor loses its position.
        
        """
        if self.logging:
            print(f"ad2.py Motor.move_to_position() called, sending MOVE_TO command with position {position} to motor control thread.")
        self.motor_q.put(MotorData(cmd=Command.MOVE_TO, data=position))

    def reset_position(self) -> None:
        """
        Public method to reset the motor position by flipping it twice.
        """
        if self.logging:
            print("ad2.py Motor.reset_position() called, sending RESET_POSITION command to motor control thread.")
        self.motor_q.put(MotorData(cmd=Command.RESET_POSITION, data=None))