#Imports
import board
import displayio
import digitalio
import time
import pulseio

#Configuration
toggle_btn = digitalio.DigitalInOut(board.D0)
toggle_btn.switch_to_input(pull=digitalio.Pull.UP)
stage_btn = digitalio.DigitalInOut(board.D1)
stage_btn.switch_to_input(pull=digitalio.Pull.UP)
send_btn = digitalio.DigitalInOut(board.D2)
send_btn.switch_to_input(pull=digitalio.Pull.UP)

pir = digitalio.DigitalInOut(board.D3)
pir.direction = digitalio.Direction.INPUT

buzzer = pulseio.PWMOut(board.D4, variable_frequency=True)

OFF = 0
ON = 2**15

#Main
while True:
# TEST BUTTONS
#     print("Toggle button: " + str(toggle_btn.value))
#     print("Stage button: " + str(stage_btn.value))
#     print("Send button: " + str(send_btn.value))
#     print("------------------------------------")
#     time.sleep(0.5)
    
# TEST PIR SENSOR
#     print(pir.value)
#     time.sleep(0.5)

# TEST BUZZER
#     buzzer.frequency = 262
#     buzzer.duty_cycle = OFF
#     time.sleep(0.5)

#     pass
