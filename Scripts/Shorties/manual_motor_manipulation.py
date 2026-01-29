from Scripts.Modules import motor
import time

ad2 = motor.open()
motor.move_to_position(ad2, motor.POS_90N)
time.sleep(2)
motor.close(ad2)