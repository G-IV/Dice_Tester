from Scripts.Modules import motor
import time

"""
In lieu of a full test suite, this script manually tests the motor module.
"""

def test_motor_module():
    print("Initializing motor...")
    ad2 = motor.Motor()
    print("Moving to default position...")
    ad2.move_to_default_position()
    time.sleep(2)
    print("Moving to 90 degree position...")
    ad2.move_to_position(ad2.POS_90)
    time.sleep(2)
    print("Flipping position...")
    ad2.flip_position()
    time.sleep(2)
    print("Closing...")
    ad2.close()

def move_motor_to_position(position):
    print(f"Initializing motor to move to position {position}...")
    ad2 = motor.Motor()
    ad2.move_to_position(position)
    time.sleep(2)
    print("Closing...")
    ad2.close()

# move_motor_to_position(motor.Motor.POS_90)
test_motor_module()