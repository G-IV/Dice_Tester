import time
from Scripts.Modules import motor

ad2 = motor.open()
motor.move_to_position(ad2, motor.CENTER_POS)
while True:
    user_input = input("Press 'q' to quit: ")
    if user_input.lower() == 'q':
        break
    if user_input == '1':
        motor.move_to_position(ad2, motor.POS_90N)
    elif user_input == '2':
        motor.move_to_position(ad2, motor.POS_90)

motor.close(ad2)
        