from Scripts.Modules import motor
import time

"""
In lieu of a full test suite, this script manually tests the motor module.
"""

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