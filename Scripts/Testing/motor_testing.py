'''
This module is used to test the motor functionality of the die tester.
'''

import time
from Scripts.Modules import motor

def test_motor_connection():
    '''
    Test the motor by moving it to +90 degrees, then -90 degrees, and back to center.
    '''
    print("Motor test: Opening AD2 reference...")
    ad2 = motor.open()

    print("Motor test completed... closing AD2 reference.")
    motor.close(ad2)

def test_manual_motor_movement():
    '''
    Test the motor movement by allowing the user to manually enter a duty cycle and position the motor in that position.
    1. open AD2 reference
    2. Ask user for input from 0-100 for duty cycle
    3. call "move_to_position" with the user input
    4. Repeast steps 2-3 until the user decides to quit by typing 'q'
    5. close AD2 reference
    6. end test
    '''
    ad2 = motor.open()

    while True:
        user_input = input("Enter a duty cycle (0-100) to move the motor to that position, or 'q' to quit: ")
        if user_input.lower() == 'q':
            break
        try:
            duty_cycle = float(user_input)
            if duty_cycle < 0 or duty_cycle > 100:
                print("Please enter a valid duty cycle between 0 and 100.")
                continue
            print(f"Moving motor to duty cycle: {duty_cycle}%")
            motor.move_to_position(ad2, position=duty_cycle)
            print("Motor moved. Waiting for 2 seconds before next input.")
            time.sleep(2)
        except ValueError:
            print("Invalid input. Please enter a number between 0 and 100, or 'q' to quit.")

    print("Motor movement test completed... closing AD2 reference.")
    motor.close(ad2)

def test_motor_limits():
    '''
    Test the motor limits by moving it to +90 degrees, then -90 degrees, and back to center.
    '''
    ad2 = motor.open()

    print("Moving motor to +90 degrees...")
    motor.move_to_position(ad2, position=motor.POS_90)
    time.sleep(2)

    print("Moving motor to -90 degrees...")
    motor.move_to_position(ad2, position=motor.POS_90N)
    time.sleep(2)

    print("Moving motor back to center (0 degrees)...")
    motor.move_to_position(ad2, position=50)
    time.sleep(2)

    print("Motor limit test completed... closing AD2 reference.")
    motor.close(ad2)

# test_motor_connection()
# test_manual_motor_movement()
test_motor_limits()