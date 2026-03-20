from Scripts.Modules.motor import Motor
import time

"""
In lieu of a full test suite, this script manually tests the motor module.
"""

ad2 = Motor()
ad2._cmd('FLIP', True) # Move to -90 degrees
time.sleep(4) # Wait for 2 seconds
ad2._cmd('close')
# Because we are threading this, we need to keep this program running with this while loop until stop_thread is True
while ad2.stop_thread == False:
   time.sleep(0.1)