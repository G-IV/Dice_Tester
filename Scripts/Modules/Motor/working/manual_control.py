from Scripts.Modules.Motor.ad2 import Motor
import time

motor = Motor(logging=True)
motor.move_to_position(Motor.POS_90N)
time.sleep(2)
motor.move_to_position(Motor.POS_90)
time.sleep(2)

motor.close()